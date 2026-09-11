"""GUI regression checks; run with the repository .venv and a display available.

Each probe uses a fresh interpreter and a temporary app copy because the legacy
editor writes configuration and preview files while opening and exporting fonts.
"""

import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET


PROJECT = Path(__file__).resolve().parents[1]


def probe(project, scale, save_preference=False):
    import os
    os.chdir(project)
    sys.path.insert(0, str(project / "src/python"))
    import tkinter as tk
    from tkinter import font
    from agon_font import write_agon_font
    from font_editor import FontEditor
    from config_editor_dialog import ConfigEditorDialog
    from ui_scaling import PreferencesDialog

    config_path = project / "src/python/app_config.xml"
    tree = ET.parse(config_path)
    if scale != "saved":
        tree.find("ui_scale").text = scale
        tree.write(config_path)
    root = tk.Tk()
    root.withdraw()
    errors = []
    root.report_callback_exception = lambda *error: errors.append(str(error))
    initial_scale = float(root.tk.call("tk", "scaling"))
    app = FontEditor(root)
    root.update_idletasks()
    display = app.image_display
    config = app.font_config_editor.get_config()
    before = display.working_image.tobytes()
    dimensions = display.working_image.size
    display.change_zoom(display.zoom_levels.index(200))
    display.on_click(type("Click", (), {"x": 20, "y": 20})())
    selected = display.current_ascii_code
    assert display.image.size == tuple(v * 2 for v in dimensions)
    assert display.working_image.tobytes() == before
    font_path = project / "export.font"
    write_agon_font(config, display.working_image, str(font_path))
    delta = app.font_config_editor.controls["point_size"].increment_button
    combo = app.font_config_editor.controls["raster_type"].combobox
    # Deliberately constrain the viewport: the bottom row must still be reachable.
    app.config_scroll.canvas.configure(height=100)
    root.update_idletasks()
    app.config_scroll.canvas.yview_moveto(1)
    root.update_idletasks()
    bottom_visible = app.config_scroll.canvas.yview()[1]
    dialog = ConfigEditorDialog(app, "src/python/batch_convert_dialog.xml", app)
    dialog.withdraw()
    root.update_idletasks()
    dialog_form_width = dialog.editor.winfo_reqwidth()
    dialog_canvas_width = dialog.form_scroll.canvas.winfo_reqwidth()
    dialog.destroy()
    prefs = PreferencesDialog(root)
    prefs.withdraw()
    if save_preference:
        prefs.scale.set("150%")
        prefs.save()
        assert "Saved" in prefs.status.cget("text")
    prefs.destroy()
    result = {
        "scale": root.ui_scale,
        "tk_scale": float(root.tk.call("tk", "scaling")),
        "initial_scale": initial_scale,
        "font_height": font.nametofont("TkDefaultFont").metrics("linespace"),
        "button_height": delta.winfo_reqheight(),
        "combo_height": combo.winfo_reqheight(),
        "scrollbar_width": app.config_scroll.scrollbar.winfo_reqwidth(),
        "bottom_visible": bottom_visible,
        "dialog_fits": dialog_canvas_width >= dialog_form_width,
        "dimensions": dimensions,
        "selected": selected,
        "font_bytes": font_path.read_bytes().hex(),
        "errors": errors,
    }
    root.destroy()
    print(json.dumps(result))


class UIScalingTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.project = Path(self.temp.name)
        shutil.copytree(PROJECT / "src/python", self.project / "src/python",
                        ignore=shutil.ignore_patterns("__pycache__"))
        fixture = PROJECT / "fontapp/fonts/Lat15-VGA8_8x8.font"
        shutil.copy2(fixture, self.project / "fixture.font")
        shutil.copy2(str(fixture) + ".xml", self.project / "fixture.font.xml")
        settings = ET.Element("settings")
        for key, value in {
            "most_recent_file": str(self.project / "fixture.font"),
            "most_recent_open_directory": str(self.project),
            "most_recent_save_directory": str(self.project),
            "default_zoom_level": "100",
            "ui_scale": "Auto",
        }.items():
            ET.SubElement(settings, key).text = value
        ET.ElementTree(settings).write(self.project / "src/python/app_config.xml")

    def run_probe(self, scale, save=False):
        result = subprocess.run(
            [sys.executable, str(Path(__file__).resolve()), "--probe", str(self.project), scale, str(int(save))],
            capture_output=True, text=True, timeout=30,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        data = json.loads(result.stdout.splitlines()[-1])
        self.assertEqual(data["errors"], [])
        self.assertEqual(data["bottom_visible"], 1.0)
        self.assertTrue(data["dialog_fits"])
        return data

    def test_controls_grow_without_changing_artwork_or_exports(self):
        results = [self.run_probe(scale) for scale in ("100%", "150%", "200%", "250%")]
        for previous, current in zip(results, results[1:]):
            for metric in ("font_height", "button_height", "combo_height", "scrollbar_width"):
                self.assertGreater(current[metric], previous[metric], metric)
        for result in results:
            self.assertEqual(result["font_bytes"], (self.project / "fixture.font").read_bytes().hex())
            self.assertEqual(result["selected"], 17)
            for field in ("dimensions", "selected", "font_bytes"):
                self.assertEqual(result[field], results[0][field], field)
            expected = int(result["scale"].rstrip("%")) / 100 * 96 / 72
            self.assertAlmostEqual(result["tk_scale"], expected, delta=0.01)
        print("UI metrics:", [{key: value for key, value in result.items()
                               if key in ("scale", "font_height", "button_height", "combo_height")}
                              for result in results])

    def test_auto_and_invalid_preference_preserve_tk_detection(self):
        for scale in ("Auto", "invalid", ""):
            result = self.run_probe(scale)
            self.assertEqual(result["scale"], "Auto")
            self.assertEqual(result["tk_scale"], result["initial_scale"])

    def test_preference_persists_and_only_applies_on_restart(self):
        original = ET.parse(self.project / "src/python/app_config.xml")
        running = self.run_probe("200%", save=True)
        self.assertEqual(running["scale"], "200%")
        saved = ET.parse(self.project / "src/python/app_config.xml")
        self.assertEqual(saved.findtext("ui_scale"), "150%")
        for node in original.getroot():
            if node.tag != "ui_scale":
                self.assertEqual(saved.findtext(node.tag), node.text)
        restarted = self.run_probe("saved")
        self.assertEqual(restarted["scale"], "150%")
        self.assertLess(restarted["font_height"], running["font_height"])


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--probe":
        probe(Path(sys.argv[2]), sys.argv[3], sys.argv[4] == "1")
    else:
        unittest.main()
