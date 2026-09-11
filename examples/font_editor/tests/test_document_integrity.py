"""BUG-001 regressions: synthetic files plus real Tk state on a virtual display.

The bitmap tests run with DISPLAY unset. GUI probes use isolated application
copies and a fresh interpreter, as do the existing editor/scaling checks.
"""

import os
from pathlib import Path
import subprocess
import sys
import unittest
import xml.etree.ElementTree as ET

import test_ui_scaling as fixtures


def probe(project, scenario):
    os.chdir(project)
    sys.path.insert(0, str(project / "src/python"))
    from types import SimpleNamespace
    from unittest.mock import patch
    from PIL import Image
    import agon_font as fonts
    import config_manager as settings
    import file_manager as files

    if scenario == "bitmap":
        config = settings.load_font_metadata_from_xml("fixture.font.xml")
        config.update(font_width=5, font_height=3, ascii_start=32, ascii_end=49,
                      chars_per_row=7, raster_type="none", threshold=127)
        # Distinct glyphs, a partial final row, and widths crossing byte padding.
        source = Image.new("RGB", (35, 9))
        for code in range(32, 50):
            col, row = (code - 32) % 7, (code - 32) // 7
            for y in range(3):
                for x in range(5):
                    value = (code * 19 + x * 43 + y * 79) % 256
                    source.putpixel((col * 5 + x, row * 3 + y), (value,) * 3)
        source_path = project / "original.png"
        source.save(source_path)
        config["original_font_path"] = str(source_path)
        variants = (
            dict(offset_left=0, offset_top=0, offset_width=0, offset_height=0,
                 scale_width=0, scale_height=0),
            dict(offset_left=1, offset_top=-1, offset_width=2, offset_height=1,
                 scale_width=0, scale_height=0),
            dict(offset_left=-1, offset_top=1, offset_width=1, offset_height=2,
                 scale_width=3, scale_height=1),
        )
        for number, variant in enumerate(variants):
            current = dict(config, **variant)
            current["font_width_mod"] = 5 + current["offset_width"] + current["scale_width"]
            current["font_height_mod"] = 3 + current["offset_height"] + current["scale_height"]
            _, image = fonts.resample_and_scale_image(current, source)
            image.putpixel((0, 0), (255, 255, 255, 255))  # A hand edit after rendering.
            expected = image.convert("L").point(lambda p: 255 if p > 127 else 0).convert("RGB")
            # Empty cells in the final atlas row are not part of the binary font.
            w, h = current["font_width_mod"], current["font_height_mod"]
            for index in range(18, 21):
                expected.paste((0, 0, 0), (index % 7 * w, index // 7 * h,
                                         (index % 7 + 1) * w, (index // 7 + 1) * h))
            saved = project / f"bitmap-{number}.font"
            before = current.copy()
            app = SimpleNamespace(image_display=SimpleNamespace(working_image=image))
            files.save_agon_font(app, current, str(saved))
            metadata_path = str(saved) + ".xml"
            bitmap = settings.load_font_metadata_from_xml(metadata_path, bitmap=True)
            for path in (saved,):
                loaded, actual = fonts.read_font(str(path), bitmap.copy())
                assert actual.size == expected.size, (number, path, actual.size, expected.size)
                assert actual.convert("RGB").tobytes() == expected.tobytes(), (number, path, "pixels changed")
                output = project / "again.font"
                fonts.write_agon_font(loaded, actual, str(output))
                assert output.read_bytes() == saved.read_bytes(), (number, path, "bytes changed")
            recipe, regenerated = fonts.read_font(metadata_path, {})
            _, expected_source = fonts.resample_and_scale_image(current, source)
            assert recipe == current
            assert regenerated.tobytes() == expected_source.tobytes()
            assert current == before, "Export mutated caller render settings"
        return

    import tkinter as tk
    from font_editor import FontEditor
    from batch_convert_dialog import BatchConvertDialog
    root = tk.Tk()
    root.withdraw()
    errors = []
    root.report_callback_exception = lambda *error: errors.append(str(error))
    app = FontEditor(root)
    root.update_idletasks()
    display = app.image_display
    display.trigger_click_on_ascii_code(65)
    app.editor_window.withdraw()
    display.update_pixel(0, 0, (255, 255, 255, 255))
    app.refresh_character_editor()

    def snapshot():
        return (app.current_font_file, app.current_font_xml_file, root.title(),
                app.font_config_editor.get_config(), display.working_image.size,
                display.working_image.tobytes(), display.current_ascii_code,
                app.editor_window, app.editor_window.title(),
                app.editor_widget.char_image.tobytes(),
                Path("src/python/app_config.xml").read_bytes())

    try:
        if scenario == "failed_open":
            bad = project / "broken.ttf"
            bad.write_bytes(b"not a font")
            unsupported = project / "unsupported.rgba2"
            unsupported.write_bytes(b"unsupported")
            malformed = project / "malformed.xml"
            malformed.write_text("<settings>")
            missing_source = project / "missing-source.xml"
            config = app.font_config_editor.get_config()
            settings.save_font_metadata_to_xml(dict(config, original_font_path=str(project / "missing.ttf")), missing_source)
            invalid_color = project / "invalid-color.font"
            invalid_color.write_bytes(Path("fixture.font").read_bytes())
            settings.save_font_metadata_to_xml(dict(config, fg_color="nope"), str(invalid_color) + ".xml")
            cases = [bad, unsupported, malformed, missing_source, invalid_color, project / "missing.ttf"]
            for path in cases:
                before = snapshot()
                metadata = {p: p.read_bytes() for p in project.rglob("*.xml")}
                with patch.object(files.filedialog, "askopenfilename", return_value=str(path)), \
                     patch.object(files.messagebox, "showerror") as show_error:
                    files.get_open_filename(app)
                    show_error.assert_called_once()
                assert snapshot() == before, (path, "Failed open changed the document")
                assert all(p.read_bytes() == data for p, data in metadata.items()), (path, "Metadata changed")
            # Repeat an invalid decoder with an existing sidecar; it must remain read-only.
            settings.save_font_metadata_to_xml(config, str(bad) + ".xml")
            sidecar = Path(str(bad) + ".xml")
            sidecar.write_text(sidecar.read_text().replace("<settings>", "<settings><!-- keep this comment -->"))
            before = snapshot()
            original = sidecar.read_bytes()
            try:
                files.open_file(app, str(bad))
            except OSError:
                pass
            assert snapshot() == before
            assert sidecar.read_bytes() == original

        elif scenario == "successful_open":
            original_defaults = Path("src/python/font_config.xml").read_bytes()
            # A valid PNG uses the default configuration, without an existing sidecar.
            image = Image.new("RGB", (128, 128))
            image.putpixel((0, 0), (255, 255, 255))
            path = project / "new.png"
            image.save(path)
            files.open_file(app, str(path))
            assert app.current_font_file == str(path)
            assert app.current_font_xml_file is None
            assert root.title().endswith("new.png")
            assert settings.get_app_config_value("most_recent_file") == str(path)
            assert Path("src/python/font_config.xml").read_bytes() == original_defaults
            assert not Path(str(path) + ".xml").exists()
            assert display.working_image.convert("RGB").tobytes() == image.tobytes()
            # Explicit main-form callback still regenerates artwork with new dimensions.
            app.font_config_editor.controls["offset_width"].increment_button.invoke()
            assert display.working_image.width == 144
            assert app.editor_widget.char_image.width == 9
            fixture = project / "fixture.font"
            sidecar = Path(str(fixture) + ".xml")
            sidecar.write_text(sidecar.read_text().replace("<settings>", "<settings><!-- preserve me -->"))
            original = sidecar.read_bytes()
            files.open_file(app, str(fixture))
            assert app.current_font_xml_file == str(sidecar)
            assert sidecar.read_bytes() == original

        elif scenario == "batch":
            before = snapshot()
            values = settings.xml_defaults_to_dict("src/python/batch_convert_dialog.xml")
            path = project / "batch-values.xml"
            dialog = BatchConvertDialog(app, "src/python/batch_convert_dialog.xml", app, values, str(path))
            # Map the controls so Tk delivers the color button's virtual event.
            # Keep them offscreen when a developer runs without Xvfb.
            root.geometry("900x650+20000+20000")
            root.deiconify()
            dialog.geometry("+22000+22000")
            root.update()
            # Actual commands/virtual events, including the color-change event
            # while substituting only the currently broken picker itself.
            controls = dialog.editor.controls
            controls["point_size"].increment_button.invoke()
            assert controls["point_size"].value == values["point_size"] + 1
            controls["offset_width"].increment_button.invoke()
            controls["raster_type"].combobox.set("none")
            controls["raster_type"].combobox.event_generate("<<ComboboxSelected>>")
            with patch("font_config_widget.AgonColorPicker.askcolor", return_value=((20, 40, 60), "#14283c")), \
                 patch.object(dialog.editor, "request_redraw", wraps=dialog.editor.request_redraw) as redraw:
                controls["fg_color"].choose_color()
                redraw.assert_called_once()
            assert controls["fg_color"].value.startswith("20,40,60,")
            assert snapshot() == before, "Batch controls changed the main document"
            dialog.on_set()
            persisted = settings.xml_values_to_dict("src/python/batch_convert_dialog.xml", str(path))
            assert persisted["point_size"] == values["point_size"] + 1
            assert persisted["offset_width"] == values["offset_width"] + 1
            assert persisted["raster_type"] == "none"
            dialog.on_cancel()
            assert root.grab_current() is None
            assert snapshot() == before, "Batch Set/Cancel changed the main document"

        elif scenario == "save_live_settings":
            config = app.font_config_editor.get_config()
            config.update(offset_width=1, scale_height=1, font_width_mod=9, font_height_mod=9)
            _, transformed = fonts.resample_and_scale_image(config, display.working_image)
            app.font_config_editor.set_controls_from_config(config)
            display.load_image(transformed.convert("RGB"))
            before = app.font_config_editor.get_config()
            source_path = app.current_font_file
            image_bytes = display.working_image.tobytes()
            target = project / "edited.font"
            with patch.object(files.filedialog, "asksaveasfilename", return_value=str(target)):
                files.save_file(app)
            assert app.font_config_editor.get_config() == before, "Save replaced live render settings"
            assert app.current_font_file == source_path
            assert display.working_image.tobytes() == image_bytes
            files.open_file(app, str(target))
            assert app.current_font_file == str(target)
            assert app.current_font_xml_file == str(target) + ".xml"
            assert display.working_image.tobytes() == image_bytes
            assert app.editor_widget.char_image.size == (9, 9)
            files.open_file(app, str(target) + ".xml")
            assert app.current_font_file == source_path
            assert app.font_config_editor.get_config() == before
            _, regenerated = fonts.read_font(source_path, before)
            assert display.working_image.tobytes() == regenerated.convert("RGB").tobytes()
        else:
            raise AssertionError(scenario)
        root.update_idletasks()
        assert errors == [], errors
    finally:
        root.destroy()


class DocumentIntegrityTests(unittest.TestCase):
    def setUp(self):
        fixtures.UIScalingTests.setUp(self)
        # Keep both the recipe path and default settings inside the fixture;
        # expectations must not depend on the author's working font/config.
        sidecar = self.project / "fixture.font.xml"
        tree = ET.parse(sidecar)
        tree.find("./setting[@name='original_font_path']").set(
            "value", str(self.project / "fixture.font"))
        tree.write(sidecar)
        tree.write(self.project / "src/python/font_config.xml")

    def run_probe(self, scenario, without_display=False):
        environment = os.environ.copy()
        environment["PYTHONDONTWRITEBYTECODE"] = "1"
        if without_display:
            environment.pop("DISPLAY", None)
            environment.pop("WAYLAND_DISPLAY", None)
        result = subprocess.run(
            [sys.executable, str(Path(__file__).resolve()), "--probe", str(self.project), scenario],
            capture_output=True, text=True, timeout=30, env=environment,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_bitmap_export_roundtrip_without_display(self):
        self.run_probe("bitmap", without_display=True)

    def test_failed_open_preserves_edited_document_and_metadata(self):
        self.run_probe("failed_open")

    def test_successful_open_is_read_only_and_main_form_still_renders(self):
        self.run_probe("successful_open")

    def test_batch_controls_set_and_cancel_are_isolated(self):
        self.run_probe("batch")

    def test_save_preserves_live_settings_and_distinguishes_recipe_from_export(self):
        self.run_probe("save_live_settings")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--probe":
        probe(Path(sys.argv[2]), sys.argv[3])
    else:
        unittest.main()
