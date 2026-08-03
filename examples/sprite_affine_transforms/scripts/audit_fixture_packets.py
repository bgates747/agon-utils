#!/usr/bin/env python3
"""Byte-audit every VDU packet template emitted by the assembly fixtures."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
ORIGIN = 0x040000
SYMBOL_PATTERN = re.compile(r"^(\S+)\s+\$([0-9a-fA-F]+)$")


def parse_symbols(path: Path) -> dict[str, int]:
    symbols: dict[str, int] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        match = SYMBOL_PATTERN.match(line.strip())
        if match:
            symbols[match.group(1)] = int(match.group(2), 16)
    if not symbols:
        raise RuntimeError(f"No symbols parsed from {path}")
    return symbols


def u16(value: int) -> list[int]:
    return [value & 0xFF, (value >> 8) & 0xFF]


def expected_packets(transform_id: int, symbols: dict[str, int]) -> dict[str, bytes]:
    affine = [23, 0, 0xA0, *u16(transform_id), 0x20]
    packets = {
        "vdu_text_cursor_move_packet": bytes([31, 0, 0]),
        "vdu_set_screen_mode_packet": bytes([22, 0]),
        "vdu_clear_screen_packet": bytes([12]),
        "vdu_cursor_hide_packet": bytes([23, 1, 0]),
        "vdu_cursor_show_packet": bytes([23, 1, 1]),
        "vdu_logical_coordinates_off_packet": bytes([23, 0, 0xC0, 0]),
        "vdu_logical_coordinates_on_packet": bytes([23, 0, 0xC0, 1]),
        "vdu_gcol_packet": bytes([18, 0, 0]),
        "vdu_buffer_clear_packet": bytes([23, 0, 0xA0, 0, 0, 2]),
        "vdu_buffer_append_packet": bytes([23, 0, 0xA0, 0, 0, 0, 0, 0]),
        "vdu_buffer_consolidate_packet": bytes([23, 0, 0xA0, 0, 0, 14]),
        "vdu_buffer_clear_all_packet": bytes([23, 0, 0xA0, 0xFF, 0xFF, 2]),
        "vdu_bitmap_select_packet": bytes([23, 27, 0x20, 0, 0]),
        "vdu_bitmap_create_packet": bytes([23, 27, 0x21, 0, 0, 0, 0, 0]),
        "vdu_bitmap_plot_packet": bytes([23, 27, 3, 0, 0, 0, 0]),
        "vdu_sprite_select_packet": bytes([23, 27, 4, 0]),
        "vdu_sprite_clear_frames_packet": bytes([23, 27, 5]),
        "vdu_sprite_add_buffer_frame_packet": bytes([23, 27, 0x26, 0, 0]),
        "vdu_sprite_select_frame_packet": bytes([23, 27, 10, 0]),
        "vdu_sprite_activate_packet": bytes([23, 27, 7, 0]),
        "vdu_sprite_move_absolute_packet": bytes([23, 27, 13, 0, 0, 0, 0]),
        "vdu_sprite_show_packet": bytes([23, 27, 11]),
        "vdu_sprite_hide_packet": bytes([23, 27, 12]),
        "vdu_sprite_refresh_packet": bytes([23, 27, 15]),
        "vdu_sprite_reset_packet": bytes([23, 27, 17]),
        "vdu_sprite_make_hardware_packet": bytes([23, 27, 19]),
        "vdu_sprite_make_software_packet": bytes([23, 27, 20]),
        "vdu_hardware_sprites_enable_packet": bytes(
            [23, 0, 0xF8, 2, 0, 0, 0]
        ),
        "vdu_hardware_sprites_disable_packet": bytes([23, 0, 0xF9, 2, 0]),
        "vdu_hardware_sprite_preference_clear_packet": bytes(
            [23, 0, 0xF9, 0, 4]
        ),
        "vdu_sprite_bind_transform_packet": bytes(
            [23, 0, 0xF8, 0x12, 0x14, 0, 0]
        ),
        "vdu_sprite_clear_transform_packet": bytes(
            [23, 0, 0xF8, 0x12, 0x14, 0xFF, 0xFF]
        ),
        "vdu_affine_matrices_enable_packet": bytes(
            [23, 0, 0xF8, 1, 0, 0, 0]
        ),
        "vdu_affine_matrices_disable_packet": bytes([23, 0, 0xF9, 1, 0]),
        "vdu_sprite_affine_enable_packet": bytes([23, 0, 0xF8, 3, 0, 0, 0]),
        "vdu_sprite_affine_disable_packet": bytes([23, 0, 0xF9, 3, 0]),
        "vdu_affine_identity_packet": bytes([*affine, 0]),
        "vdu_affine_translate_8_4_packet": bytes(
            [*affine, 6, 0xC0, *u16(8), *u16(4)]
        ),
        "vdu_affine_scale_2_packet": bytes(
            [*affine, 5, 0xC0, *u16(2), *u16(2)]
        ),
        "vdu_affine_rotate_90_packet": bytes(
            [*affine, 2, 0xC0, *u16(90)]
        ),
        "vdu_affine_shear_negative_half_x_packet": bytes(
            [*affine, 8, 0xC8, *u16(-128), *u16(0)]
        ),
        "vdu_affine_reflect_x_packet": bytes(
            [*affine, 5, 0xC8, *u16(-256), *u16(256)]
        ),
        "vdu_affine_translate_negative_pivot_packet": bytes(
            [*affine, 6, 0xC0, *u16(-8), *u16(-8)]
        ),
        "vdu_affine_translate_positive_pivot_packet": bytes(
            [*affine, 6, 0xC0, *u16(8), *u16(8)]
        ),
        "vdu_affine_scale_singular_packet": bytes(
            [*affine, 5, 0xC0, *u16(0), *u16(1)]
        ),
    }

    if "torture_affine_alternate_identity_packet" in symbols:
        ship_id = symbols["torture_ship_buffer_id"]
        gate_args_id = symbols["torture_gate_args_buffer_id"]
        primary_id = symbols["torture_primary_transform_id"]
        alternate_id = symbols["torture_alternate_transform_id"]
        panel_matrix_id = symbols["torture_panel_transform_id"]
        lifetime_id = symbols["torture_lifetime_buffer_id"]
        capture_id = symbols["torture_capture_buffer_id"]
        probe_width = symbols["torture_probe_width"]
        probe_height = symbols["torture_probe_height"]
        probe_y = symbols["torture_probe_y"]
        select_lifetime = [23, 27, 0x20, *u16(lifetime_id)]
        create_red = [
            23,
            27,
            2,
            *u16(probe_width),
            *u16(probe_height),
            0xFF,
            0,
            0,
            0xFF,
        ]
        create_cyan = [
            23,
            27,
            2,
            *u16(probe_width),
            *u16(probe_height),
            0,
            0xFF,
            0xFF,
            0xFF,
        ]
        transform_off = [23, 0, 0x96, 1, 0xFF, 0xFF]
        transform_primary = [23, 0, 0x96, 1, *u16(primary_id)]

        def bitmap_plot(x: int, y: int) -> list[int]:
            return [23, 27, 3, *u16(x), *u16(y)]

        packets.update(
            {
                "torture_affine_alternate_identity_packet": bytes(
                    [23, 0, 0xA0, *u16(alternate_id), 0x20, 0]
                ),
                "torture_affine_alternate_rotate_90_packet": bytes(
                    [23, 0, 0xA0, *u16(alternate_id), 0x20, 2, 0xC0, *u16(90)]
                ),
                "torture_affine_panel_identity_packet": bytes(
                    [23, 0, 0xA0, *u16(panel_matrix_id), 0x20, 0]
                ),
                "torture_affine_panel_scale_8_packet": bytes(
                    [
                        23,
                        0,
                        0xA0,
                        *u16(panel_matrix_id),
                        0x20,
                        5,
                        0xC0,
                        *u16(8),
                        *u16(8),
                    ]
                ),
                "torture_affine_primary_scale_nan_packet": bytes(
                    [
                        23,
                        0,
                        0xA0,
                        *u16(primary_id),
                        0x20,
                        5,
                        0,
                        0,
                        0,
                        0xC0,
                        0x7F,
                        0,
                        0,
                        0x80,
                        0x3F,
                    ]
                ),
                "torture_affine_primary_scale_extreme_packet": bytes(
                    [
                        23,
                        0,
                        0xA0,
                        *u16(primary_id),
                        0x20,
                        5,
                        0xC0,
                        *u16(32767),
                        *u16(32767),
                    ]
                ),
                "torture_buffer_adjust_ship_packet": bytes(
                    [
                        23,
                        0,
                        0xA0,
                        *u16(ship_id),
                        5,
                        0x47,
                        *u16(0),
                        *u16(symbols["torture_ship_size"]),
                        0x3F,
                    ]
                ),
                "torture_queue_plot_lifetime_packet": bytes(
                    [
                        *select_lifetime,
                        *create_red,
                        *transform_off,
                        *bitmap_plot(
                            symbols["torture_queue_raw_old_x"], probe_y
                        ),
                        *create_cyan,
                        *bitmap_plot(
                            symbols["torture_queue_raw_new_x"], probe_y
                        ),
                        *create_red,
                        *transform_primary,
                        *bitmap_plot(
                            symbols["torture_queue_transform_old_x"], probe_y
                        ),
                        *create_cyan,
                        *bitmap_plot(
                            symbols["torture_queue_transform_new_x"], probe_y
                        ),
                        *transform_off,
                        23,
                        0,
                        0xCA,
                        7,
                    ]
                ),
                "torture_capture_source_packet": bytes(
                    [
                        *select_lifetime,
                        *create_red,
                        *transform_off,
                        *bitmap_plot(
                            symbols["torture_capture_source_old_x"], probe_y
                        ),
                        *create_cyan,
                        *bitmap_plot(
                            symbols["torture_capture_source_new_x"], probe_y
                        ),
                        23,
                        0,
                        0xCA,
                    ]
                ),
                "torture_capture_consume_packet": bytes(
                    [
                        25,
                        4,
                        *u16(symbols["torture_capture_source_old_x"]),
                        *u16(probe_y),
                        25,
                        4,
                        *u16(
                            symbols["torture_capture_source_new_x"]
                            + probe_width
                            - 1
                        ),
                        *u16(probe_y + probe_height - 1),
                        23,
                        27,
                        0x21,
                        *u16(capture_id),
                        *u16(0),
                        *transform_off,
                        23,
                        27,
                        0x20,
                        *u16(capture_id),
                        *bitmap_plot(symbols["torture_capture_raw_x"], probe_y),
                        23,
                        27,
                        4,
                        symbols["torture_capture_sprite_id"],
                        23,
                        27,
                        0x35,
                        *u16(capture_id),
                        23,
                        27,
                        15,
                    ]
                ),
                "torture_status_cond_call_packet": bytes(
                    [23, 0, 0xA0, 0, 0, 6, 0xC2, 0x13, 0x14, 0, 0]
                ),
                "torture_gate_affine_2d_packet": bytes(
                    [
                        23,
                        0,
                        0xA0,
                        *u16(symbols["torture_gate_affine_2d_target_id"]),
                        0x20,
                        0x45,
                        0xC0,
                        *u16(2),
                        0xC8,
                        *u16(0x100),
                    ]
                ),
                "torture_gate_affine_3d_packet": bytes(
                    [
                        23,
                        0,
                        0xA0,
                        *u16(symbols["torture_gate_affine_3d_target_id"]),
                        0x21,
                        0x75,
                        0xC0,
                        *u16(gate_args_id),
                        16,
                        0,
                        0,
                        0xC8,
                        *u16(gate_args_id),
                        18,
                        0,
                        0,
                        0,
                        *u16(gate_args_id),
                        20,
                        0,
                        0,
                    ]
                ),
                "torture_gate_matrix_packet": bytes(
                    [
                        23,
                        0,
                        0xA0,
                        *u16(symbols["torture_gate_matrix_target_id"]),
                        0x22,
                        0x30,
                        2,
                        2,
                        0xC0,
                        *u16(gate_args_id),
                        8,
                        0,
                        0,
                    ]
                ),
                "torture_gate_transform_bitmap_packet": bytes(
                    [
                        23,
                        0,
                        0xA0,
                        *u16(symbols["torture_gate_bitmap_target_id"]),
                        0x28,
                        7,
                        *u16(primary_id),
                        *u16(ship_id),
                        *u16(symbols["torture_ship_width"]),
                        *u16(symbols["torture_ship_height"]),
                    ]
                ),
                "torture_gate_transform_data_inline_packet": bytes(
                    [
                        23,
                        0,
                        0xA0,
                        *u16(symbols["torture_gate_data_inline_target_id"]),
                        0x29,
                        0x1F,
                        0xC0,
                        *u16(primary_id),
                        *u16(ship_id),
                        2,
                        0,
                        0,
                        0,
                        *u16(4),
                        *u16(1),
                    ]
                ),
                "torture_gate_transform_data_buffer_packet": bytes(
                    [
                        23,
                        0,
                        0xA0,
                        *u16(symbols["torture_gate_data_buffer_target_id"]),
                        0x29,
                        0x7F,
                        0xC0,
                        *u16(primary_id),
                        *u16(ship_id),
                        *u16(gate_args_id),
                        0,
                        0,
                        0,
                        *u16(gate_args_id),
                        1,
                        0,
                        0,
                        *u16(gate_args_id),
                        4,
                        0,
                        0,
                        *u16(gate_args_id),
                        6,
                        0,
                        0,
                    ]
                ),
                "torture_stream_sync_marker_packet": bytes(
                    [7, *b"PT SYNC PASS: gated tails consumed"]
                ),
            }
        )

    return packets


def slice_at(binary: bytes, address: int, size: int) -> bytes:
    offset = address - ORIGIN
    if offset < 0 or offset + size > len(binary):
        raise RuntimeError(
            f"Address {address:#08x} size {size} is outside the assembled binary"
        )
    return binary[offset : offset + size]


def audit_packets(binary_path: Path, symbols_path: Path) -> int:
    binary = binary_path.read_bytes()
    symbols = parse_symbols(symbols_path)
    transform_id = symbols["vdu_affine_transform_buffer_id"]
    expected = expected_packets(transform_id, symbols)
    emitted = {name for name in symbols if name.endswith("_packet")}
    expected_names = set(expected)
    if emitted != expected_names:
        missing = sorted(expected_names - emitted)
        extra = sorted(emitted - expected_names)
        raise RuntimeError(f"Packet label coverage mismatch: missing={missing}, extra={extra}")

    for label, expected_bytes in sorted(expected.items()):
        end_label = f"{label}_end"
        if end_label not in symbols:
            raise RuntimeError(f"Missing end label {end_label}")
        declared_size = symbols[end_label] - symbols[label]
        if declared_size != len(expected_bytes):
            raise RuntimeError(
                f"{label} length: expected {len(expected_bytes)}, got {declared_size}"
            )
        actual = slice_at(binary, symbols[label], declared_size)
        if actual != expected_bytes:
            raise RuntimeError(
                f"{label}: expected {expected_bytes.hex(' ')}, got {actual.hex(' ')}"
            )

    if "format_rgba2222_pixels" in symbols:
        format_constants = {
            "format_rgba2222_size": 16 * 16,
            "format_rgba8888_size": 12 * 8 * 4,
            "format_mask_size": 2 * 5,
            "format_mask_foreground_colour": 14,
            "format_sprite_count": 6,
        }
        for label, expected_value in format_constants.items():
            actual_value = symbols.get(label)
            if actual_value != expected_value:
                raise RuntimeError(
                    f"{label}: expected {expected_value}, got {actual_value}"
                )

        embedded_assets = {
            "format_rgba2222_pixels": PROJECT_ROOT
            / "assets/rgba2222/ship_1c.rgba2222",
            "format_rgba8888_pixels": PROJECT_ROOT
            / "assets/rgba8888/rgba8888_alpha_edge_12x8.rgba8888",
            "format_mask_pixels": PROJECT_ROOT / "assets/mask/mask_9x5_msb.mask",
        }
        for label, source in embedded_assets.items():
            source_bytes = source.read_bytes()
            actual = slice_at(binary, symbols[label], len(source_bytes))
            if actual != source_bytes:
                raise RuntimeError(f"Embedded payload {label} differs from {source}")

    if "torture_ship_pixels" in symbols:
        torture_constants = {
            "torture_ship_size": 16 * 16,
            "torture_laser_size": 5 * 13,
            "torture_mask_size": 2 * 5,
            "torture_panel_size": 352 * 48 * 4,
            "torture_panel_first_block_size": 65535,
            "torture_panel_tail_size": 2049,
            "torture_gate_args_size": 24,
            "torture_sprite_count": 4,
            "torture_capture_sprite_count": 5,
            "torture_probe_width": 8,
            "torture_probe_height": 8,
            "torture_sprite_transform_status_var": 0x1413,
        }
        for label, expected_value in torture_constants.items():
            actual_value = symbols.get(label)
            if actual_value != expected_value:
                raise RuntimeError(
                    f"{label}: expected {expected_value}, got {actual_value}"
                )

        if symbols["torture_panel_tail"] != (
            symbols["torture_panel_pixels"]
            + symbols["torture_panel_first_block_size"]
        ):
            raise RuntimeError("torture_panel_tail does not start at byte 65535")

        embedded_assets = {
            "torture_ship_pixels": PROJECT_ROOT
            / "assets/rgba2222/ship_1c.rgba2222",
            "torture_laser_pixels": PROJECT_ROOT
            / "assets/rgba2222/laser_a_5x13.rgba2222",
            "torture_mask_pixels": PROJECT_ROOT / "assets/mask/mask_9x5_msb.mask",
            "torture_panel_pixels": PROJECT_ROOT
            / "assets/rgba8888/ctl_panel_top_352x48.rgba8888",
        }
        for label, source in embedded_assets.items():
            source_bytes = source.read_bytes()
            actual = slice_at(binary, symbols[label], len(source_bytes))
            if actual != source_bytes:
                raise RuntimeError(f"Embedded payload {label} differs from {source}")

        expected_gate_args = bytes(
            [
                2,
                0,
                0,
                0,
                *u16(4),
                *u16(1),
                *u16(1),
                *u16(0),
                *u16(0),
                *u16(1),
                *u16(1),
                *u16(0x100),
                0,
                0,
                0x80,
                0x3F,
            ]
        )
        actual_gate_args = slice_at(
            binary, symbols["torture_gate_args"], len(expected_gate_args)
        )
        if actual_gate_args != expected_gate_args:
            raise RuntimeError("Embedded torture gate arguments changed")

    print(
        f"Audited {len(expected)} packet templates in {binary_path.name}; "
        f"transform={transform_id:#06x}"
    )
    return len(expected)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "pairs",
        nargs="*",
        type=Path,
        help="binary/symbol pairs (defaults to all project fixtures)",
    )
    args = parser.parse_args()
    if args.pairs and len(args.pairs) % 2:
        parser.error("paths must be supplied as binary/symbol pairs")

    if args.pairs:
        pairs = list(zip(args.pairs[::2], args.pairs[1::2], strict=True))
    else:
        pairs = [
            (
                PROJECT_ROOT / "build/sprite_affine_transforms.bin",
                PROJECT_ROOT / "src/app.symbols",
            ),
            (
                PROJECT_ROOT / "build/sprite_affine_formats.bin",
                PROJECT_ROOT / "src/formats.symbols",
            ),
            (
                PROJECT_ROOT / "build/sprite_affine_torture.bin",
                PROJECT_ROOT / "src/torture.symbols",
            ),
        ]

    total = sum(audit_packets(binary, symbols) for binary, symbols in pairs)
    print(f"Packet audit passed: {total} templates across {len(pairs)} binaries")


if __name__ == "__main__":
    main()
