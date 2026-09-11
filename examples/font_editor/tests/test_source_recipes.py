"""Original-source recipes and exported pixels have distinct reopen paths."""

import os
from pathlib import Path
import shutil
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
    source = project / ("original.ttf" if scenario == "ttf" else "original.png")
    if source.suffix == ".png":
        image = Image.new("RGB", (128, 128))
        for y in range(128):
            for x in range(128):
                shade = (x * 31 + y * 17) % 256
                image.putpixel((x, y), (shade,) * 3)
        image.save(source)
    original_bytes = source.read_bytes()
    config.update(original_font_path=str(source), raster_type="quantized",
                  point_size=12, offset_left=1, offset_top=-1,
                  scale_width=1, scale_height=2, offset_width=1)
    config, expected = fonts.read_font(str(source), config)
    config.update(font_width_mod=expected.width // 16,
                  font_height_mod=expected.height // 16)

    if scenario in {"png", "ttf"}:
        edited = expected.copy()
        shade = 85 if edited.getpixel((0, 0))[0] != 85 else 170
        edited.putpixel((0, 0), (shade, shade, shade, 255))
        app = SimpleNamespace(image_display=SimpleNamespace(working_image=edited))
        for extension, save in (("font", files.save_agon_font), ("png", files.save_png_font)):
            output = project / f"saved.{extension}"
            save(app, config, str(output))
            xml = str(output) + ".xml"
            recipe = settings.load_font_metadata_from_xml(xml)
            assert recipe == config, (extension, recipe, config)
            loaded, regenerated = fonts.read_font(xml, {})
            assert loaded["original_font_path"] == str(source)
            assert regenerated.size == expected.size
            assert regenerated.tobytes() == expected.tobytes(), extension
            # These are recipe files, not snapshots of hand-edited pixels.
            assert regenerated.tobytes() != edited.tobytes()
        xml_only = project / "settings.xml"
        files.save_font_xml(config, str(xml_only))
        assert settings.load_font_metadata_from_xml(xml_only) == config
        assert settings.load_font_metadata_from_xml(xml_only, bitmap=True) is None
        assert source.read_bytes() == original_bytes
        return

    import tkinter as tk
    from font_editor import FontEditor
    root = tk.Tk()
    root.withdraw()
    errors = []
    root.report_callback_exception = lambda *error: errors.append(str(error))
    app = FontEditor(root)
    try:
        recipe_path = project / "initial.xml"
        settings.save_font_metadata_to_xml(config, recipe_path)
        assert files.open_file(app, str(recipe_path))
        assert app.current_font_file == str(source)
        before = app.font_config_editor.get_config()
        output = project / "saved.font"
        with patch.object(files.filedialog, "asksaveasfilename", return_value=str(output)):
            files.save_file(app)
        assert app.font_config_editor.get_config() == before
        assert app.current_font_file == str(source)
        assert settings.get_app_config_value("most_recent_file") == str(output) + ".xml"
        app.destroy()
        app = FontEditor(root)  # Actual startup reads the saved recent-file preference.
        assert app.current_font_file == str(source)
        assert app.font_config_editor.get_config() == before
        assert app.image_display.working_image.tobytes() == expected.convert("RGB").tobytes()

        # Save must not replace the source artwork with its downsampled output.
        recent = Path("src/python/app_config.xml").read_bytes()
        with patch.object(files.filedialog, "asksaveasfilename", return_value=str(source)), \
             patch.object(files.messagebox, "showerror") as error:
            files.save_file(app)
            error.assert_called_once()
        assert source.read_bytes() == original_bytes
        assert Path("src/python/app_config.xml").read_bytes() == recent
        assert not Path(str(source) + ".xml").exists()

        # XML with missing source fails without replacing the working document.
        source.rename(project / "hidden.png")
        image_bytes = app.image_display.working_image.tobytes()
        recent = Path("src/python/app_config.xml").read_bytes()
        with patch.object(files.filedialog, "askopenfilename", return_value=str(output) + ".xml"), \
             patch.object(files.messagebox, "showerror") as error:
            files.get_open_filename(app)
            error.assert_called_once()
        assert app.current_font_file == str(source)
        assert app.image_display.working_image.tobytes() == image_bytes
        assert Path("src/python/app_config.xml").read_bytes() == recent

        # The exported bitmap remains openable independently of its source.
        assert files.open_file(app, str(output))
        assert app.current_font_file == str(output)
        width, height = app.image_display.working_image.size
        controls = app.font_config_editor.controls
        controls["scale_width"].increment_button.invoke()
        assert app.image_display.working_image.size == (width + 16, height)
        controls["raster_type"].combobox.set("quantized")
        controls["raster_type"].combobox.event_generate("<<ComboboxSelected>>")
        root.update()
        assert app.font_config_editor.get_config()["raster_type"] == "quantized"
        levels = set(app.image_display.working_image.convert("L").getdata())
        assert levels & {85, 170}, levels

        # Legacy raw FONT sidecars must not lock the controls either.
        assert files.open_file(app, str(project / "fixture.font"))
        controls["scale_width"].increment_button.invoke()
        controls["raster_type"].value = "quantized"
        app.image_display.render_font()
        assert app.image_display.working_image.size == (144, 128)
        assert controls["raster_type"].value == "quantized"
        # Resolve relative recipe paths against the XML, not the launch folder.
        directory = project / "recipes"
        directory.mkdir()
        relative = directory / "relative.xml"
        settings.save_font_metadata_to_xml(
            dict(config, original_font_path="../hidden.png"), relative)
        assert files.open_file(app, str(relative))
        assert app.current_font_file == str(project / "hidden.png")
        assert app.image_display.working_image.tobytes() == expected.convert("RGB").tobytes()

        # Bad source chains must fail through the regular open error path.
        cyclic = directory / "cycle.xml"
        settings.save_font_metadata_to_xml(
            dict(config, original_font_path="cycle.xml"), cyclic)
        with patch.object(files.filedialog, "askopenfilename", return_value=str(cyclic)), \
             patch.object(files.messagebox, "showerror") as error:
            files.get_open_filename(app)
            error.assert_called_once()
        assert app.current_font_file == str(project / "hidden.png")
        assert not errors, errors
    finally:
        root.destroy()


class SourceRecipeTests(unittest.TestCase):
    def setUp(self):
        fixtures.DocumentIntegrityTests.setUp(self)
        source = Path(__file__).resolve().parents[1] / "src/fonts/net/ttf/ubuntu/UbuntuMono-R.ttf"
        shutil.copy2(source, self.project / "original.ttf")

    def run_probe(self, scenario, headless=False):
        environment = os.environ.copy()
        environment["PYTHONDONTWRITEBYTECODE"] = "1"
        if headless:
            environment.pop("DISPLAY", None)
            environment.pop("WAYLAND_DISPLAY", None)
        result = subprocess.run([sys.executable, str(Path(__file__).resolve()), "--probe",
                                 str(self.project), scenario], capture_output=True,
                                text=True, timeout=30, env=environment)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_png_recipe_preserves_original_source_and_transforms(self):
        self.run_probe("png", headless=True)

    def test_ttf_recipe_preserves_original_source_and_transforms(self):
        self.run_probe("ttf", headless=True)

    def test_restart_missing_source_and_bitmap_render_controls(self):
        self.run_probe("application")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--probe":
        probe(Path(sys.argv[2]), sys.argv[3])
    else:
        unittest.main()
