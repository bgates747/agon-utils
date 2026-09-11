"""Faithful output offsets and a selected-character sampling preview."""

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
                  font_width_mod=6, font_height_mod=8, ascii_start=65, ascii_end=66,
                  chars_per_row=2, raster_type='quantized', position_units='output')
    glyph = Image.new('RGBA', (13, 17), (0, 0, 0, 255))
    draw = ImageDraw.Draw(glyph)
    draw.line((2, 14, 6, 2, 11, 14), fill='white', width=2)
    draw.line((4, 10, 9, 10), fill='white', width=2)
    atlas = Image.new('RGBA', (26, 17), (0, 0, 0, 255))
    atlas.paste(glyph, (0, 0))

    if scenario == 'position':
        before = atlas.tobytes()
        _, zero = fonts.resample_and_scale_image(config, atlas)
        unpositioned = zero.crop((0, 0, 6, 8))
        for mode in ('quantized', 'grayscale', 'threshold'):
            config['raster_type'] = mode
            _, baseline = fonts.resample_and_scale_image(config, atlas)
            for x, y in ((1, 0), (-1, 0), (0, 1), (0, -1), (2, -2), (8, 12)):
                changed = dict(config, offset_left=x, offset_top=y)
                _, actual = fonts.resample_and_scale_image(changed, atlas)
                expected = Image.new('RGBA', (6, 8), (0, 0, 0, 255))
                expected.paste(baseline.crop((0, 0, 6, 8)), (x, y))
                assert actual.crop((0, 0, 6, 8)).tobytes() == expected.tobytes()
                assert sampling.brightness(actual.crop((6, 0, 12, 8))) == 0
            assert fonts.resample_and_scale_image(config, atlas)[1].tobytes() == baseline.tobytes()
        assert atlas.tobytes() == before
        # A glyph wider than its output cell must not spill into the next row.
        cropped = dict(config, offset_width=-2, offset_height=-3, ascii_end=67)
        tall = Image.new('RGBA', (26, 34), (0, 0, 0, 255))
        tall.paste(glyph, (13, 0))
        _, result = fonts.resample_and_scale_image(cropped, tall)
        assert sampling.brightness(result.crop((0, 5, 8, 10))) == 0
        old = dict(config, position_units='source', offset_left=-5, offset_top=3)
        converted = sampling.convert_position_units(old, 'output')
        assert (converted['offset_left'], converted['offset_top']) == (-2, 1)
        assert old['offset_left'] == -5
        assert sampling.convert_position_units(converted, 'output') == converted
        return

    if scenario == 'search':
        before, pixels = config.copy(), glyph.tobytes()
        results = list(sampling.search_candidates(config, glyph))
        assert len(results) == 81
        assert results[-1][0:2] == (81, 81)
        scores = [item[3] for item in results]
        assert scores == sorted(scores)
        assert scores[-1] > scores[0], scores
        winner = results[-1]
        repeated = list(sampling.search_candidates(config, glyph))[-1]
        assert winner[2].tobytes() == repeated[2].tobytes()
        assert winner[3:] == repeated[3:]
        assert all(abs(value) <= 1 and value * 4 == int(value * 4) for value in winner[4])
        assert config == before and glyph.tobytes() == pixels
        blank = Image.new('RGBA', glyph.size, (0, 0, 0, 255))
        assert list(sampling.search_candidates(config, blank))[-1][4] == (0, 0)
        clipped = dict(config, offset_width=-2, offset_left=-1)
        best = list(sampling.search_candidates(clipped, glyph))[-1]
        baseline = fonts.rasterize_image(clipped, sampling.sample_glyph(clipped, glyph))
        sampled = fonts.rasterize_image(clipped, sampling.sample_glyph(clipped, glyph, best[4]))
        assert sampling.clipped_ink(clipped, sampled) <= sampling.clipped_ink(clipped, baseline)
        for changed in (dict(config, position_units='source'), dict(config, raster_type='palette'),
                        dict(config, bg_color='255,255,255,255')):
            try:
                list(sampling.search_candidates(changed, glyph))
            except ValueError:
                pass
            else:
                raise AssertionError('Unsupported search accepted')
        return

    import time
    import tkinter as tk
    from font_editor import FontEditor
    from resampling_preview import ResamplingPreview
    root = tk.Tk()
    root.withdraw()
    errors = []
    root.report_callback_exception = lambda *error: errors.append(str(error))
    app = FontEditor(root)
    source = project / 'source.png'
    atlas.save(source)
    config['original_font_path'] = str(source)
    metadata = project / 'recipe.xml'
    settings.save_font_metadata_to_xml(config, metadata)
    initial_metadata = metadata.read_bytes()
    files.open_file(app, str(metadata))
    display = app.image_display
    display.trigger_click_on_ascii_code(65)
    app.editor_window.withdraw()

    def preview():
        assert not hasattr(app.editor_widget, 'optimize_button')
        app.editor_widget.optimize_resampling()  # Retained code, intentionally hidden in UI.
        window = next(w for w in root.winfo_children() if isinstance(w, ResamplingPreview))
        window.withdraw()
        return window

    def finish(window):
        deadline = time.monotonic() + 10
        while window.apply_button.cget('state') != 'normal':
            root.update()
            if time.monotonic() > deadline:
                raise AssertionError(window.status.cget('text'))
            time.sleep(.002)

    try:
        original = display.working_image.tobytes()
        window = preview()
        window.close()  # Cancel during search, not just after completion.
        root.update()
        assert display.working_image.tobytes() == original
        window = preview()
        finish(window)
        candidate = window.result.copy()
        before_config = app.font_config_editor.get_config()
        window.apply_button.invoke()
        assert app.font_config_editor.get_config() == before_config
        assert display.get_char_img_ascii(65).convert('RGBA').tobytes() == candidate.tobytes()
        assert sampling.brightness(display.get_char_img_ascii(66)) == 0
        assert app.editor_widget.char_image.tobytes() == candidate.tobytes()
        assert metadata.read_bytes() == initial_metadata
        output = project / 'optimized.png'
        files.save_png_font(app, before_config, str(output))
        assert Image.open(output).tobytes() == display.working_image.tobytes()
        assert settings.load_font_metadata_from_xml(str(output) + '.xml') == before_config
        window = preview()
        finish(window)
        display.trigger_click_on_ascii_code(66)
        before = display.working_image.tobytes()
        window.apply_button.invoke()
        assert window.apply_button.cget('state') == 'disabled'
        assert display.working_image.tobytes() == before
        window.close()
        # Exercise the real unit-conversion event, including displayed offsets.
        controls = app.font_config_editor.controls
        controls['position_units'].value = 'source'
        controls['offset_left'].value = -5
        controls['offset_top'].value = 3
        controls['position_units'].combobox.set('output')
        controls['position_units']._handle_value_change()
        assert controls['offset_left'].value == -2
        assert controls['offset_top'].value == 1
        assert controls['position_units'].value == 'output'
        assert not errors, errors
    finally:
        root.destroy()


class GlyphResamplingTests(unittest.TestCase):
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

    def test_output_offsets_translate_without_changing_samples_or_neighbours(self):
        self.run_probe('position', headless=True)

    def test_bounded_search_is_repeatable_and_keeps_offsets(self):
        self.run_probe('search', headless=True)

    def test_preview_cancel_apply_stale_selection_and_png_save(self):
        self.run_probe('preview')


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--probe':
        probe(Path(sys.argv[2]), sys.argv[3])
    else:
        unittest.main()
