"""Isolated glyph sampling, integer positioning, and an experimental phase search."""

from PIL import Image, ImageChops
import math

from agon_font import parse_rgba_color, rasterize_image


def dimensions(config):
    scaled = (config['font_width'] + config['scale_width'],
              config['font_height'] + config['scale_height'])
    cell = (scaled[0] + config['offset_width'], scaled[1] + config['offset_height'])
    if min(*scaled, *cell) <= 0:
        raise ValueError('Scaled glyph and output cell dimensions must be positive')
    return scaled, cell


def convert_position_units(config, units):
    """An explicit conversion; search and rendering never change these values."""
    result = config.copy()
    previous = config.get('position_units', 'source')
    if units not in {'source', 'output'}:
        raise ValueError('Position units must be source or output')
    if previous != units:
        scaled, _ = dimensions(config)
        for key, old_size, new_size in zip(
                ('offset_left', 'offset_top'),
                (config['font_width'], config['font_height']), scaled):
            ratio = new_size / old_size
            result[key] = round(config[key] * ratio if units == 'output' else config[key] / ratio)
    result['position_units'] = units
    return result


def source_glyph(config, atlas, code):
    if not config['ascii_start'] <= code <= config['ascii_end']:
        raise ValueError('Select a character in the current font')
    index = code - config['ascii_start']
    x = index % config['chars_per_row'] * config['font_width']
    y = index // config['chars_per_row'] * config['font_height']
    return atlas.crop((x, y, x + config['font_width'], y + config['font_height'])).convert('RGBA')


def sample_glyph(config, glyph, phase=(0, 0)):
    scaled, _ = dimensions(config)
    if phase == (0, 0) and scaled == glyph.size:
        return glyph.copy()
    # Padding supplies background outside this character, never a neighbour.
    pad = math.ceil(2 * max(glyph.width / scaled[0], glyph.height / scaled[1])) + 2
    padded = Image.new('RGBA', (glyph.width + 2 * pad, glyph.height + 2 * pad),
                       parse_rgba_color(config['bg_color']))
    padded.paste(glyph, (pad, pad))
    dx, dy = phase
    return padded.resize(scaled, Image.Resampling.BICUBIC,
                         box=(pad + dx, pad + dy, pad + dx + glyph.width, pad + dy + glyph.height))


def position_glyph(config, sampled):
    """Translate by exactly the specified integer offsets and clip to one cell."""
    _, cell = dimensions(config)
    output = Image.new('RGBA', cell, parse_rgba_color(config['bg_color']))
    output.paste(sampled, (config['offset_left'], config['offset_top']))
    return output


def render_atlas(config, source):
    scaled, cell = dimensions(config)
    columns = config['chars_per_row']
    count = config['ascii_end'] - config['ascii_start'] + 1
    rows = (count + columns - 1) // columns
    background = parse_rgba_color(config['bg_color'])
    sampled = Image.new('RGBA', (columns * scaled[0], rows * scaled[1]), background)
    for index in range(count):
        glyph = source_glyph(config, source, config['ascii_start'] + index)
        sampled.paste(sample_glyph(config, glyph),
                      (index % columns * scaled[0], index // columns * scaled[1]))
    # Convert once, including palette mode, before any positioning or clipping.
    sampled = rasterize_image(config, sampled)
    output = Image.new('RGBA', (columns * cell[0], rows * cell[1]), background)
    for index in range(count):
        x, y = index % columns * scaled[0], index // columns * scaled[1]
        glyph = sampled.crop((x, y, x + scaled[0], y + scaled[1]))
        output.paste(position_glyph(config, glyph),
                     (index % columns * cell[0], index // columns * cell[1]))
    return output


def brightness(image):
    return sum(value * count for value, count in enumerate(image.convert('L').histogram()))


def clipped_ink(config, sampled):
    _, (width, height) = dimensions(config)
    x, y = config['offset_left'], config['offset_top']
    mask = Image.new('L', sampled.size, 255)
    left, top = max(0, -x), max(0, -y)
    right, bottom = min(sampled.width, width - x), min(sampled.height, height - y)
    if left < right and top < bottom:
        mask.paste(0, (left, top, right, bottom))
    return brightness(ImageChops.multiply(sampled.convert('L'), mask))


def search_candidates(config, glyph):
    """Yield progress and best pixels; a stable 81-candidate search, no mutation."""
    if config.get('position_units') != 'output':
        raise ValueError('Set Position Units to output before optimizing a character')
    if config['raster_type'] not in {'quantized', 'grayscale', 'threshold'}:
        raise ValueError('Choose quantized, grayscale or threshold rendering')
    if (parse_rgba_color(config['fg_color']) != (255, 255, 255, 255)
            or parse_rgba_color(config['bg_color']) != (0, 0, 0, 255)):
        raise ValueError('Brightness search currently needs white on opaque black')
    phases = sorted(((x / 4, y / 4) for x in range(-4, 5) for y in range(-4, 5)),
                    key=lambda p: (p[0] ** 2 + p[1] ** 2, p[1], p[0]))
    baseline = rasterize_image(config, sample_glyph(config, glyph))
    max_loss = clipped_ink(config, baseline)
    best = position_glyph(config, baseline)
    best_score, best_phase = brightness(best), (0, 0)
    for index, phase in enumerate(phases):
        sampled = rasterize_image(config, sample_glyph(config, glyph, phase))
        candidate = position_glyph(config, sampled)
        score = brightness(candidate)
        if clipped_ink(config, sampled) <= max_loss and score > best_score:
            best, best_score, best_phase = candidate, score, phase
        yield index + 1, len(phases), best, best_score, best_phase


def optimize_atlas(config, source, current):
    """Search each glyph independently; return a complete atlas without mutation.

    Yields (completed phase count, total phase count, character code) so callers
    can keep their UI responsive. The final image is the generator's return value.
    Unused cells in a partial final row retain their working pixels.
    """
    _, (width, height) = dimensions(config)
    columns = config['chars_per_row']
    count = config['ascii_end'] - config['ascii_start'] + 1
    if columns <= 0 or count <= 0:
        raise ValueError('The character grid must have a positive size')
    rows = (count + columns - 1) // columns
    if current.size != (columns * width, rows * height):
        raise ValueError('The working image does not match the configured character grid')
    result = current.copy()
    for index, code in enumerate(range(config['ascii_start'], config['ascii_end'] + 1)):
        glyph = source_glyph(config, source, code)
        for done, total, best, score, phase in search_candidates(config, glyph):
            yield index * total + done, count * total, code
        result.paste(best.convert(result.mode), (index % columns * width, index // columns * height))
    return result
