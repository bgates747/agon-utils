#!/usr/bin/env python3
"""Interactively inspect image records in an AGNB container."""

import argparse
import struct
import tempfile
import tkinter as tk
from dataclasses import dataclass
from pathlib import Path
from tkinter import font as tkfont
from tkinter import ttk

import agonutils
from PIL import Image, ImageTk


DEFAULT_CONTAINER = Path(__file__).resolve().parents[1] / "tgt" / "images.agnb"
MIN_SCALE = 1
MAX_SCALE = 32


@dataclass(frozen=True)
class ImageRecord:
    index: int
    buffer_id: int
    width: int
    height: int
    image_format: int
    data_offset: int
    data_size: int
    list_offset: int


def read_chunk(data: bytes, offset: int, boundary: int):
    if offset + 8 > boundary:
        raise ValueError(f"Truncated chunk header at file offset {offset}")

    chunk_id = data[offset : offset + 4]
    payload_size = struct.unpack_from("<I", data, offset + 4)[0]
    payload_start = offset + 8
    payload_end = payload_start + payload_size
    next_offset = payload_start + ((payload_size + 3) & ~3)
    if payload_end > boundary or next_offset > boundary:
        raise ValueError(f"Chunk {chunk_id!r} at {offset} crosses its boundary")
    if any(data[payload_end:next_offset]):
        raise ValueError(f"Chunk {chunk_id!r} at {offset} has nonzero padding")

    return chunk_id, payload_start, payload_end, next_offset


def parse_container(path: Path) -> tuple[bytes, list[ImageRecord]]:
    data = path.read_bytes()
    if len(data) < 12 or data[:4] != b"RIFF" or data[8:12] != b"AGNB":
        raise ValueError(f"Not a RIFF AGNB file: {path}")
    declared_size = struct.unpack_from("<I", data, 4)[0]
    if declared_size != len(data) - 8:
        raise ValueError(
            f"RIFF size mismatch: header says {declared_size}, file needs {len(data) - 8}"
        )

    records = []
    version_seen = False
    offset = 12
    while offset < len(data):
        chunk_offset = offset
        chunk_id, payload_start, payload_end, offset = read_chunk(
            data, offset, len(data)
        )

        if chunk_id == b"VERS":
            if version_seen or records:
                raise ValueError("VERS must occur once before all buffer records")
            if data[payload_start:payload_end] != b"\x00\x01":
                raise ValueError("Viewer supports only AGNB version 0.1")
            version_seen = True
            continue

        if chunk_id != b"LIST":
            continue
        if not version_seen:
            raise ValueError("LIST BUFR encountered before VERS")
        if payload_end - payload_start < 4:
            raise ValueError(f"Truncated LIST at file offset {chunk_offset}")
        if data[payload_start : payload_start + 4] != b"BUFR":
            continue

        nested = []
        nested_offset = payload_start + 4
        while nested_offset < payload_end:
            nested_chunk = read_chunk(data, nested_offset, payload_end)
            nested.append(nested_chunk)
            nested_offset = nested_chunk[3]
        if nested_offset != payload_end:
            raise ValueError(f"Invalid LIST boundary at file offset {chunk_offset}")
        if [item[0] for item in nested] != [b"BHDR", b"IMAG", b"DATA"]:
            raise ValueError(
                f"Unsupported BUFR layout at file offset {chunk_offset}: "
                f"{[item[0] for item in nested]!r}"
            )

        _id, start, end, _next = nested[0]
        if end - start != 2:
            raise ValueError(f"Invalid BHDR size at file offset {chunk_offset}")
        buffer_id = struct.unpack_from("<H", data, start)[0]
        if buffer_id == 0xFFFF:
            raise ValueError(f"Reserved buffer ID at file offset {chunk_offset}")

        _id, start, end, _next = nested[1]
        if end - start != 5:
            raise ValueError(f"Invalid IMAG size at file offset {chunk_offset}")
        width, height, image_format = struct.unpack_from("<HHB", data, start)
        if image_format != 1:
            raise ValueError(f"Unsupported image format {image_format}")

        _id, data_start, data_end, _next = nested[2]
        data_size = data_end - data_start
        if not width or not height or data_size != width * height:
            raise ValueError(
                f"Invalid RGBA2222 dimensions or DATA size at {chunk_offset}"
            )

        records.append(
            ImageRecord(
                index=len(records),
                buffer_id=buffer_id,
                width=width,
                height=height,
                image_format=image_format,
                data_offset=data_start,
                data_size=data_size,
                list_offset=chunk_offset,
            )
        )

    if not version_seen:
        raise ValueError("Missing VERS chunk")
    if not records:
        raise ValueError("Container contains no supported image records")
    if len({record.buffer_id for record in records}) != len(records):
        raise ValueError("Container contains duplicate buffer IDs")
    return data, records


class ContainerViewer(tk.Tk):
    def __init__(self, container_path: Path):
        super().__init__()
        self.container_path = container_path
        self.container_data, self.records = parse_container(container_path)
        self.record_index = 0
        self.scale = 1
        self.current_payload = b""
        self.source_image = None
        self.display_image = None
        self.tk_image = None
        self.temp_dir = tempfile.TemporaryDirectory(prefix="agnb-viewer-")

        self.title(f"AGNB Viewer — {container_path.name}")
        self.geometry("1400x1000")
        self.minsize(900, 650)
        self.protocol("WM_DELETE_WINDOW", self.close)
        self.enlarge_fonts()

        self.metadata_var = tk.StringVar()
        self.scale_var = tk.StringVar()
        self.pixel_var = tk.StringVar(value="Move over the image to inspect a pixel")
        self.jump_var = tk.StringVar(value="1")

        self.build_ui()
        self.bind_keys()
        self.show_record(0)

    def enlarge_fonts(self):
        """Make the standard Tk widget fonts large and high-contrast."""
        font_names = (
            "TkDefaultFont",
            "TkTextFont",
            "TkMenuFont",
            "TkHeadingFont",
            "TkCaptionFont",
            "TkSmallCaptionFont",
            "TkIconFont",
            "TkFixedFont",
        )
        for name in font_names:
            try:
                font = tkfont.nametofont(name)
            except tk.TclError:
                continue
            current_size = int(font.cget("size"))
            enlarged_size = current_size * 2
            font.configure(size=enlarged_size, weight="bold")

    def build_ui(self):
        toolbar = ttk.Frame(self, padding=12)
        toolbar.grid(row=0, column=0, sticky="ew")
        ttk.Button(toolbar, text="|<", command=lambda: self.show_record(0)).pack(
            side="left"
        )
        ttk.Button(toolbar, text="<", command=lambda: self.step_record(-1)).pack(
            side="left"
        )
        ttk.Button(toolbar, text=">", command=lambda: self.step_record(1)).pack(
            side="left"
        )
        ttk.Button(
            toolbar,
            text=">|",
            command=lambda: self.show_record(len(self.records) - 1),
        ).pack(side="left")

        ttk.Label(toolbar, text="  Record:").pack(side="left")
        jump_entry = ttk.Entry(toolbar, width=7, textvariable=self.jump_var)
        jump_entry.pack(side="left")
        jump_entry.bind("<Return>", self.jump_to_record)
        ttk.Button(toolbar, text="Go", command=self.jump_to_record).pack(side="left")

        ttk.Separator(toolbar, orient="vertical").pack(
            side="left", fill="y", padx=10
        )
        ttk.Button(toolbar, text="−", command=lambda: self.change_scale(-1)).pack(
            side="left"
        )
        ttk.Label(toolbar, textvariable=self.scale_var, width=8, anchor="center").pack(
            side="left"
        )
        ttk.Button(toolbar, text="+", command=lambda: self.change_scale(1)).pack(
            side="left"
        )
        ttk.Button(toolbar, text="1:1", command=lambda: self.set_scale(1)).pack(
            side="left", padx=(6, 0)
        )

        ttk.Label(
            self,
            textvariable=self.metadata_var,
            padding=(16, 6),
            justify="left",
            font="TkFixedFont",
        ).grid(row=1, column=0, sticky="ew")

        image_frame = ttk.Frame(self)
        image_frame.grid(row=2, column=0, sticky="nsew")
        image_frame.rowconfigure(0, weight=1)
        image_frame.columnconfigure(0, weight=1)

        self.canvas = tk.Canvas(
            image_frame, background="#303030", highlightthickness=0
        )
        x_scroll = ttk.Scrollbar(
            image_frame, orient="horizontal", command=self.canvas.xview
        )
        y_scroll = ttk.Scrollbar(
            image_frame, orient="vertical", command=self.canvas.yview
        )
        self.canvas.configure(xscrollcommand=x_scroll.set, yscrollcommand=y_scroll.set)
        self.canvas.grid(row=0, column=0, sticky="nsew")
        y_scroll.grid(row=0, column=1, sticky="ns")
        x_scroll.grid(row=1, column=0, sticky="ew")
        self.canvas.bind("<Motion>", self.inspect_pixel)
        self.canvas.bind("<Leave>", lambda _event: self.pixel_var.set(""))

        ttk.Label(
            self,
            textvariable=self.pixel_var,
            padding=12,
            anchor="w",
            font="TkFixedFont",
        ).grid(row=3, column=0, sticky="ew")

        self.rowconfigure(2, weight=1)
        self.columnconfigure(0, weight=1)

    def bind_keys(self):
        self.bind("<Left>", lambda _event: self.step_record(-1))
        self.bind("<Right>", lambda _event: self.step_record(1))
        self.bind("<Home>", lambda _event: self.show_record(0))
        self.bind("<End>", lambda _event: self.show_record(len(self.records) - 1))
        for key in ("<plus>", "<equal>", "<KP_Add>"):
            self.bind(key, lambda _event: self.change_scale(1))
        for key in ("<minus>", "<KP_Subtract>"):
            self.bind(key, lambda _event: self.change_scale(-1))
        self.bind("<Escape>", lambda _event: self.close())
        self.bind("q", lambda _event: self.close())

    def decode_current_record(self, record: ImageRecord) -> Image.Image:
        payload = self.container_data[
            record.data_offset : record.data_offset + record.data_size
        ]
        self.current_payload = payload

        temp_root = Path(self.temp_dir.name)
        rgba_file = temp_root / "record.rgba2"
        png_file = temp_root / "record.png"
        rgba_file.write_bytes(payload)
        agonutils.rgba2_to_img(
            str(rgba_file), str(png_file), record.width, record.height
        )
        with Image.open(png_file) as image:
            return image.convert("RGBA").copy()

    def show_record(self, index: int):
        self.record_index = max(0, min(index, len(self.records) - 1))
        record = self.records[self.record_index]
        self.source_image = self.decode_current_record(record)
        self.jump_var.set(str(self.record_index + 1))
        self.metadata_var.set(
            f"Record: {self.record_index + 1}/{len(self.records)}    "
            f"Buffer ID: {record.buffer_id} (0x{record.buffer_id:04X})\n"
            f"Image: {record.width}×{record.height}    Format: {record.image_format} "
            f"(RGBA2222)    DATA: {record.data_size} bytes\n"
            f"LIST offset: 0x{record.list_offset:08X}    "
            f"DATA offset: 0x{record.data_offset:08X}"
        )
        self.render_image()

    def render_image(self):
        width = self.source_image.width * self.scale
        height = self.source_image.height * self.scale
        if self.scale == 1:
            self.display_image = self.source_image
        else:
            self.display_image = self.source_image.resize(
                (width, height), Image.Resampling.NEAREST
            )
        self.tk_image = ImageTk.PhotoImage(self.display_image)
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor="nw", image=self.tk_image)
        self.canvas.configure(scrollregion=(0, 0, width, height))
        self.scale_var.set(f"{self.scale}×")
        self.pixel_var.set("Move over the image to inspect a pixel")

    def step_record(self, amount: int):
        self.show_record((self.record_index + amount) % len(self.records))

    def jump_to_record(self, _event=None):
        try:
            requested = int(self.jump_var.get())
        except ValueError:
            self.bell()
            return
        if not 1 <= requested <= len(self.records):
            self.bell()
            return
        self.show_record(requested - 1)

    def set_scale(self, scale: int):
        scale = max(MIN_SCALE, min(scale, MAX_SCALE))
        if scale != self.scale:
            self.scale = scale
            self.render_image()

    def change_scale(self, amount: int):
        self.set_scale(self.scale + amount)

    def inspect_pixel(self, event):
        record = self.records[self.record_index]
        x = int(self.canvas.canvasx(event.x) // self.scale)
        y = int(self.canvas.canvasy(event.y) // self.scale)
        if not 0 <= x < record.width or not 0 <= y < record.height:
            self.pixel_var.set("")
            return

        packed = self.current_payload[y * record.width + x]
        red = (packed & 0x03) * 85
        green = ((packed >> 2) & 0x03) * 85
        blue = ((packed >> 4) & 0x03) * 85
        alpha = ((packed >> 6) & 0x03) * 85
        self.pixel_var.set(
            f"x={x} y={y}    RGBA2222=0x{packed:02X}    "
            f"RGBA8888=({red}, {green}, {blue}, {alpha})"
        )

    def close(self):
        self.temp_dir.cleanup()
        self.destroy()


def main():
    parser = argparse.ArgumentParser(description="Inspect images in an AGNB file.")
    parser.add_argument(
        "container",
        nargs="?",
        type=Path,
        default=DEFAULT_CONTAINER,
        help=f"AGNB file to inspect (default: {DEFAULT_CONTAINER})",
    )
    args = parser.parse_args()

    viewer = ContainerViewer(args.container.resolve())
    viewer.mainloop()


if __name__ == "__main__":
    main()
