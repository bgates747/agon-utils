"""Exercise real Tk click bindings, editor lifetime, atlas scrolling and zoom."""

import json
from pathlib import Path
import subprocess
import sys
import unittest

import test_ui_scaling as scaling_tests


def probe(project, scenario):
    import os
    import tkinter as tk
    from types import SimpleNamespace
    from PIL import Image
    os.chdir(project)
    sys.path.insert(0, str(project / "src/python"))
    from font_editor import FontEditor
    from file_manager import save_agon_font

    root = tk.Tk()
    # Exercise mapped widgets without placing the automated fixture on the
    # author's working desktop. No global input injection is used.
    root.overrideredirect(True)
    root.geometry("900x650+20000+20000")
    app = FontEditor(root)
    root.title("Font Editor automated check")
    root.update()
    errors = []
    root.report_callback_exception = lambda *error: errors.append(str(error))
    display = app.image_display

    def click_code(code):
        column, row = display.ascii_to_coordinates(code)
        config = app.font_config_editor.get_config()
        sx, sy = display._display_scale()
        x = (column + 0.5) * config['font_width_mod'] * sx - display.canvas.canvasx(0)
        y = (row + 0.5) * config['font_height_mod'] * sy - display.canvas.canvasy(0)
        display.canvas.event_generate("<Button-1>", x=round(x), y=round(y))
        root.update()
        assert display.current_ascii_code == code, (display.current_ascii_code, code)
        assert app.editor_window is not None

    if scenario == "editor":
        assert app.editor_window is None
        click_code(65)
        window = app.editor_window
        assert root.grab_current() is None
        assert app.editor_widget.char_image.tobytes() == display.get_char_img_ascii(65).convert("RGBA").tobytes()
        before = display.working_image.copy()
        # A's top-left pixel is background in this fixture; toggle it once.
        editor = app.editor_widget
        original = editor.char_image.getpixel((0, 0))
        editor.canvas.event_generate("<Button-1>", x=editor.pixel_size // 2, y=editor.pixel_size // 2)
        root.update()
        edited = editor.char_image.getpixel((0, 0))
        assert edited != original
        column, row = display.ascii_to_coordinates(65)
        assert display.working_image.getpixel((column * 8, row * 8)) == edited[:3]
        assert len(editor.canvas.find_all()) == 64
        click_code(66)
        assert app.editor_window is window
        assert display.get_char_img_ascii(66).tobytes() == before.crop((16, 32, 24, 40)).tobytes()
        click_code(65)
        assert app.editor_widget.char_image.getpixel((0, 0)) == edited
        target = project / "edited.font"
        save_agon_font(app, app.font_config_editor.get_config(), str(target))
        expected = bytearray((project / "fixture.font").read_bytes())
        expected[65 * 8] ^= 0x80
        assert target.read_bytes() == expected
        root.tk.call(app.editor_window.protocol("WM_DELETE_WINDOW"))
        assert app.editor_window is None and app.editor_widget is None
        click_code(65)
        assert app.editor_window is not window
        assert app.editor_widget.char_image.getpixel((0, 0)) == edited
        app.close_character_editor()
        # Clicking the margin must neither alias another row nor open a window.
        display.canvas.event_generate("<Button-1>", x=display.image.width + 20, y=4)
        root.update()
        assert app.editor_window is None

    elif scenario == "zoom":
        original = display.working_image.tobytes()
        dimensions = display.working_image.size
        requested = (display.canvas.winfo_reqwidth(), display.canvas.winfo_reqheight())
        for zoom in (500, 600, 700, 800):
            display.zoom_control.zoom_var.set(f"{zoom}%")
            display.zoom_control._on_dropdown_change(f"{zoom}%")
            root.update()
            assert display.image.size == tuple(v * zoom // 100 for v in dimensions)
            assert display.working_image.tobytes() == original
            assert (display.canvas.winfo_reqwidth(), display.canvas.winfo_reqheight()) == requested
        display.zoom_control.zoom_in()
        assert display.zoom_levels[display.current_zoom_index] == 800
        display.zoom_control.zoom_out()
        assert display.zoom_levels[display.current_zoom_index] == 700
        display.change_zoom(display.zoom_levels.index(800))
        display.canvas.xview_moveto(1)
        display.canvas.yview_moveto(1)
        root.update()
        assert display.canvas.canvasx(0) > 0 and display.canvas.canvasy(0) > 0
        click_code(255)
        box = display.canvas.coords("selection_box")
        assert box == [960.0, 960.0, 1024.0, 1024.0], box
        target = project / "zoomed.font"
        save_agon_font(app, app.font_config_editor.get_config(), str(target))
        assert target.read_bytes() == (project / "fixture.font").read_bytes()

    elif scenario == "redraw":
        click_code(65)
        display.toggle_grid(True)
        count = len(display.canvas.find_all())
        for i in range(100):
            display.change_zoom(display.zoom_levels.index(800 if i % 2 else 100))
            click_code(65 + i % 2)
            editor = app.editor_widget
            editor.canvas.event_generate("<Button-1>", x=editor.pixel_size // 2, y=editor.pixel_size // 2)
            root.update()
            assert len(editor.canvas.find_all()) == 64
            assert len(display.canvas.find_all()) == count
            assert len(display.canvas.find_withtag("atlas")) == 1
        # Include a partial final row and glyphs smaller than four source pixels:
        # fractional zoom must not produce a zero grid-line step or row aliasing.
        config = app.font_config_editor.get_config()
        config.update(font_width=3, font_height=3, font_width_mod=3, font_height_mod=3,
                      ascii_start=32, ascii_end=42, chars_per_row=7)
        app.font_config_editor.set_controls_from_config(config)
        display.load_image(Image.new("RGB", (21, 6)))
        for zoom in (25, 50, 100, 800):
            display.change_zoom(display.zoom_levels.index(zoom))
            root.update()
            assert len(display.canvas.find_withtag("gridline")) == 11
        click_code(40)
        assert display.ascii_to_coordinates(40) == (1, 1)
        # Blank cell 6 of the final row maps beyond ascii_end and is ignored.
        code = display.current_ascii_code
        display.on_click(SimpleNamespace(x=6 * 3 * 8 + 2, y=3 * 8 + 2))
        assert display.current_ascii_code == code
        assert app.editor_widget.char_image.size == (3, 3)

    heartbeat = []
    root.after(0, lambda: heartbeat.append(True))
    root.update()
    assert heartbeat and not errors, errors
    result = {"scenario": scenario, "canvas_items": len(display.canvas.find_all()), "responsive": True}
    root.destroy()
    print(json.dumps(result))


class CharacterEditorTests(unittest.TestCase):
    setUp = scaling_tests.UIScalingTests.setUp

    def run_scenario(self, scenario):
        result = subprocess.run(
            [sys.executable, str(Path(__file__).resolve()), "--probe", str(self.project), scenario],
            capture_output=True, text=True, timeout=30,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertTrue(json.loads(result.stdout.splitlines()[-1])["responsive"])

    def test_click_edit_export_and_window_lifetime(self):
        self.run_scenario("editor")

    def test_zoom_to_800_and_scrolled_selection(self):
        self.run_scenario("zoom")

    def test_redraw_stress_and_narrow_partial_rows(self):
        self.run_scenario("redraw")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--probe":
        probe(Path(sys.argv[2]), sys.argv[3])
    else:
        unittest.main()
