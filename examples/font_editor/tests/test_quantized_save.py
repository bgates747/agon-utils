"""Quantized rendering and lossless saves, with display-free pixel regressions."""

import os
from pathlib import Path
import subprocess
import sys
import unittest

import test_document_integrity as fixtures


def probe(project, scenario):
    os.chdir(project)
    sys.path.insert(0, str(project / "src/python"))
    from types import SimpleNamespace
    from unittest.mock import patch
    from PIL import Image
    import agon_font as fonts
    import config_manager as settings
    import file_manager as files

    config = settings.load_font_metadata_from_xml("fixture.font.xml")
    if scenario == "raster":
        samples = [0, 12, 42, 43, 84, 85, 127, 128, 169, 170, 212, 213, 240, 255]
        image = Image.new("RGB", (len(samples), 1))
        image.putdata([(v, v, v) for v in samples])
        config.update(font_width=len(samples), font_height=1, chars_per_row=1,
                      ascii_start=0, ascii_end=0, raster_type="quantized")
        _, actual = fonts.resample_and_scale_image(config, image)
        expected = [0, 0, 0, 85, 85, 85, 85, 170, 170, 170, 170, 255, 255, 255]
        assert [actual.getpixel((x, 0))[0] for x in range(len(samples))] == expected
        _, repeated = fonts.resample_and_scale_image(config, actual)
        assert repeated.tobytes() == actual.tobytes()
        config["raster_type"] = "grayscale"
        image.paste((255, 0, 0), (0, 0, len(samples), 1))
        _, gray = fonts.resample_and_scale_image(config, image)
        assert gray.convert("RGB").getpixel((0, 0)) == (76, 76, 76)
        return

    if scenario == "png":
        config.update(font_width=8, font_height=8, font_width_mod=3, font_height_mod=4,
                      offset_left=1, offset_top=-1, offset_width=-5, offset_height=-4,
                      ascii_start=32, ascii_end=49, chars_per_row=7, raster_type="quantized")
        atlas = Image.new("RGB", (21, 12))
        for index in range(18):
            for y in range(4):
                for x in range(3):
                    value = ((index + x + y) % 4) * 85
                    atlas.putpixel((index % 7 * 3 + x, index // 7 * 4 + y), (value,) * 3)
        atlas.putpixel((0, 0), (170, 170, 170))  # A pixel edit after rendering.
        current = config.copy()
        editor = SimpleNamespace(get_config=lambda: current.copy(),
                                 set_controls_from_config=lambda values: current.update(values))
        app = SimpleNamespace(font_config_editor=editor,
                              image_display=SimpleNamespace(working_image=atlas))
        target = project / "quantized.png"
        with patch.object(files, "get_save_filename", return_value=(config.copy(), str(target), "png")):
            files.save_file(app)
        assert current == config, "Saving changed live settings"
        assert Image.open(target).convert("RGB").tobytes() == atlas.tobytes()
        metadata = settings.load_font_metadata_from_xml(str(target) + ".xml")
        assert metadata["raster_type"] == "quantized"
        assert metadata == config
        bitmap = settings.load_font_metadata_from_xml(str(target) + ".xml", bitmap=True)
        assert (bitmap["font_width"], bitmap["font_height"]) == (3, 4)
        for source in (str(target),):
            _, reopened = fonts.read_font(source, bitmap.copy())
            assert reopened.size == atlas.size
            assert reopened.convert("RGB").tobytes() == atlas.tobytes(), source
        # A range narrower than one row must reopen too.
        one = dict(bitmap, ascii_end=32)
        path = project / "one.png"
        atlas.crop((0, 0, 21, 4)).save(path)
        returned, image = fonts.read_png_font(str(path), one)
        assert returned["font_height"] == 4
        return

    import tkinter as tk
    from font_editor import FontEditor
    root = tk.Tk()
    root.withdraw()
    app = FontEditor(root)
    try:
        control = app.font_config_editor.controls["raster_type"]
        if scenario == "native_dialog":
            # Exercise Tk's actual Linux file chooser: a fixed default extension
            # can override a newly selected filter even when mocked tests pass.
            control.value = "quantized"
            errors = []

            def submit():
                try:
                    menu = root.tk.globalgetvar("::tk::dialog::file::__tk_filedialog(typeMenu)")
                    root.tk.call(menu, "invoke", 1)  # Explicit monochrome filter.
                    entry = root.tk.globalgetvar("::tk::dialog::file::__tk_filedialog(ent)")
                    root.tk.call(entry, "delete", 0, "end")
                    root.tk.call(entry, "insert", 0, "native-mono")
                    button = root.tk.globalgetvar("::tk::dialog::file::__tk_filedialog(okBtn)")
                    root.tk.call(button, "invoke")
                except Exception as error:
                    errors.append(str(error))
                    root.tk.globalsetvar("::tk::Priv(selectFilePath)", "")

            root.after(100, submit)
            _, path, kind = files.get_save_filename(app)
            assert not errors, errors
            assert (path, kind) == (str(project / "native-mono.font"), "font"), (path, kind)
            return
        for mode, expected_extension in (("quantized", ".png"), ("grayscale", ".png"),
                                         ("palette", ".png"), ("threshold", ".font")):
            control.value = mode

            def choose(**options):
                assert options["defaultextension"] == ""
                assert options["filetypes"][0][1] == "*" + expected_extension
                return str(project / "extensionless")

            with patch.object(files.filedialog, "asksaveasfilename", side_effect=choose):
                _, path, kind = files.get_save_filename(app)
            assert path.endswith(expected_extension), (mode, path)
            assert kind == expected_extension.lstrip(".")

        control.value = "quantized"

        def choose_mono(**options):
            label = next(label for label, pattern in options["filetypes"] if pattern == "*.font")
            assert "monochrome" in label.lower()
            options["typevariable"].set(label)
            return str(project / "explicit-mono")

        with patch.object(files.filedialog, "asksaveasfilename", side_effect=choose_mono):
            _, path, kind = files.get_save_filename(app)
        assert (path, kind) == (str(project / "explicit-mono.font"), "font")
        with patch.object(files.filedialog, "asksaveasfilename", return_value=str(project / "explicit.FONT")):
            _, path, kind = files.get_save_filename(app)
        assert path.endswith(".FONT") and kind == "font"
        with patch.object(files.filedialog, "asksaveasfilename", return_value=""):
            assert files.get_save_filename(app) == (None, None, None)

        # Save/open through the real application, retaining the quantized mode.
        cfg = app.font_config_editor.get_config()
        image = Image.new("RGB", (128, 128))
        for x, shade in enumerate((0, 85, 170, 255)):
            image.putpixel((x, 0), (shade,) * 3)
        app.image_display.load_image(image)
        target = project / "saved.png"
        with patch.object(files.filedialog, "asksaveasfilename", return_value=str(target)):
            files.save_file(app)
        assert app.font_config_editor.get_config() == cfg
        for source in (str(target),):
            files.open_file(app, source)
            assert control.value == "quantized"
            assert app.image_display.working_image.tobytes() == image.tobytes()
        files.open_file(app, str(target) + ".xml")
        assert app.current_font_file == cfg["original_font_path"]
        assert control.value == "quantized"
        _, regenerated = fonts.read_font(cfg["original_font_path"], cfg)
        assert app.image_display.working_image.tobytes() == regenerated.convert("RGB").tobytes()
    finally:
        root.destroy()


class QuantizedSaveTests(unittest.TestCase):
    setUp = fixtures.DocumentIntegrityTests.setUp

    def run_probe(self, scenario, headless=False):
        environment = os.environ.copy()
        environment["PYTHONDONTWRITEBYTECODE"] = "1"
        if headless:
            environment.pop("DISPLAY", None)
            environment.pop("WAYLAND_DISPLAY", None)
        result = subprocess.run([sys.executable, str(Path(__file__).resolve()), "--probe",
                                 str(self.project), scenario], capture_output=True, text=True,
                                timeout=30, env=environment)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_quantized_and_grayscale_rendering_without_display(self):
        self.run_probe("raster", headless=True)

    def test_png_preserves_quantized_pixels_geometry_and_metadata_without_display(self):
        self.run_probe("png", headless=True)

    def test_save_format_selection_and_application_roundtrip(self):
        self.run_probe("dialog")

    def test_native_save_dialog_honors_a_changed_file_type(self):
        self.run_probe("native_dialog")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--probe":
        probe(Path(sys.argv[2]), sys.argv[3])
    else:
        unittest.main()
