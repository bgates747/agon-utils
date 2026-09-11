"""Global optimization uses individual winners and applies results together."""

import os
from pathlib import Path
import subprocess
import sys
import unittest

import test_document_integrity as fixtures


def probe(project, scenario):
    os.chdir(project)
    sys.path.insert(0, str(project / 'src/python'))
    from PIL import Image, ImageDraw
    import agon_font as fonts
    import config_manager as settings
    import glyph_resampling as sampling
    import file_manager as files

    config = settings.load_font_metadata_from_xml('fixture.font.xml')
    config.update(font_width=13, font_height=17, scale_width=-7, scale_height=-9,
                  offset_width=0, offset_height=0, offset_left=0, offset_top=0,
                  font_width_mod=6, font_height_mod=8, ascii_start=65, ascii_end=69,
                  chars_per_row=3, raster_type='quantized', position_units='output')
    source = Image.new('RGBA', (39, 34), (0, 0, 0, 255))
    for i in range(5):
        glyph = Image.new('RGBA', (13, 17), (0, 0, 0, 255))
        draw = ImageDraw.Draw(glyph)
        draw.line((2, 14, 6, 2, 11, 14), fill='white', width=2)
        draw.line((4, 8 + i, 9, 8 + i), fill='white', width=2)
        source.paste(glyph, (i % 3 * 13, i // 3 * 17))
    current = sampling.render_atlas(config, source).convert('RGB')
    current.paste((23, 23, 23), (12, 8, 18, 16))  # Unused partial-row cell.

    def finish_generator(search):
        progress = []
        while True:
            try:
                progress.append(next(search))
            except StopIteration as done:
                return done.value, progress

    if scenario == 'pixels':
        before = config.copy(), source.tobytes(), current.tobytes()
        result, progress = finish_generator(sampling.optimize_atlas(config, source, current))
        assert len(progress) == 5 * 81
        assert [p[0] for p in progress] == list(range(1, 406))
        assert progress[-1] == (405, 405, 69)
        for i, code in enumerate(range(65, 70)):
            single = list(sampling.search_candidates(config, sampling.source_glyph(config, source, code)))[-1][2]
            x, y = i % 3 * 6, i // 3 * 8
            assert result.crop((x, y, x + 6, y + 8)).tobytes() == single.convert('RGB').tobytes()
        assert result.crop((12, 8, 18, 16)).tobytes() == current.crop((12, 8, 18, 16)).tobytes()
        assert (config, source.tobytes(), current.tobytes()) == before
        assert finish_generator(sampling.optimize_atlas(config, source, current))[0].tobytes() == result.tobytes()
        return

    import time
    import tkinter as tk
    from unittest.mock import patch
    from font_editor import FontEditor
    import atlas_resampling

    root = tk.Tk()
    root.withdraw()
    errors = []
    root.report_callback_exception = lambda *error: errors.append(str(error))
    app = FontEditor(root)
    path = project / 'original.png'
    source.save(path)
    config['original_font_path'] = str(path)
    metadata = project / 'source.xml'
    settings.save_font_metadata_to_xml(config, metadata)
    files.open_file(app, str(metadata))
    display = app.image_display
    display.working_image = current.copy()
    display.trigger_click_on_ascii_code(65)
    app.editor_window.withdraw()
    original_metadata = metadata.read_bytes()
    before = display.working_image.tobytes()
    original_settings = app.font_config_editor.get_config()

    def launch():
        display.optimize_all_button.invoke()
        window = app.optimization_window
        window.withdraw()
        return window

    def finish(window):
        deadline = time.monotonic() + 10
        while window.pending is not None:
            root.update()
            if time.monotonic() > deadline:
                raise AssertionError(window.status.cget('text'))
            time.sleep(.002)

    try:
        assert not hasattr(app.editor_widget, 'optimize_button')
        assert callable(app.editor_widget.optimize_resampling)
        window = launch()
        display.optimize_all_button.invoke()
        assert app.optimization_window is window, 'Duplicate run created'
        for _ in range(82):
            next(window.search)  # At least one winner exists in the private atlas.
        assert display.working_image.tobytes() == before
        window.close()
        root.update()
        assert display.working_image.tobytes() == before

        window = launch()
        display.update_pixel(0, 0, (85, 85, 85, 255))
        edited = display.working_image.tobytes()
        finish(window)
        assert not window.completed
        assert 'document changed' in window.status.cget('text')
        assert display.working_image.tobytes() == edited
        window.close()
        display.working_image = current.copy()

        real_search = sampling.optimize_atlas
        def broken(*args):
            search = real_search(*args)
            for _ in range(82):
                yield next(search)
            raise ValueError('Injected search failure')
        with patch.object(atlas_resampling, 'optimize_atlas', side_effect=broken):
            window = launch()
            finish(window)
        assert not window.completed
        assert 'Injected search failure' in window.status.cget('text')
        assert display.working_image.tobytes() == before
        window.close()

        window = launch()
        finish(window)
        assert window.completed, window.status.cget('text')
        expected, _ = finish_generator(sampling.optimize_atlas(config, source, current))
        assert display.working_image.tobytes() == expected.tobytes()
        assert display.current_ascii_code == 65
        assert app.editor_widget.char_image.convert('RGB').tobytes() == display.get_char_img_ascii(65).tobytes()
        assert app.font_config_editor.get_config() == original_settings
        assert metadata.read_bytes() == original_metadata
        saved = project / 'optimized.png'
        files.save_png_font(app, original_settings, str(saved))
        assert Image.open(saved).tobytes() == expected.tobytes()
        assert settings.load_font_metadata_from_xml(str(saved) + '.xml') == original_settings
        display.render_font()
        baseline = sampling.render_atlas(config, source).convert('RGB')
        assert display.working_image.tobytes() == baseline.tobytes()
        assert not errors, errors
    finally:
        root.destroy()


class AtlasResamplingTests(unittest.TestCase):
    setUp = fixtures.DocumentIntegrityTests.setUp

    def run_probe(self, scenario, headless=False):
        environment = os.environ.copy()
        environment['PYTHONDONTWRITEBYTECODE'] = '1'
        if headless:
            environment.pop('DISPLAY', None)
            environment.pop('WAYLAND_DISPLAY', None)
        result = subprocess.run([sys.executable, str(Path(__file__).resolve()), '--probe',
                                 str(self.project), scenario], capture_output=True, text=True,
                                timeout=30, env=environment)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_global_results_match_individual_searches(self):
        self.run_probe('pixels', headless=True)

    def test_global_command_cancel_error_stale_edit_apply_save_and_rerender(self):
        self.run_probe('application')


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--probe':
        probe(Path(sys.argv[2]), sys.argv[3])
    else:
        unittest.main()
