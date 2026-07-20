# agonutils

A native Python extension providing image, palette, AGM, RLE, and SIMZ utilities
for Agon development tools.

## Native prerequisites

The extension requires a C compiler, `pkg-config`, FFmpeg development libraries,
and libpng development headers.

On Debian or Ubuntu:

```bash
sudo apt install \
  build-essential pkg-config ffmpeg \
  libavformat-dev libavcodec-dev libswscale-dev libavutil-dev libpng-dev
```

On macOS with Homebrew:

```bash
brew install pkg-config ffmpeg libpng
```

## Installation

Install a fixed copy into the active Python environment with:

```bash
python -m pip install .
```

For development, use an editable installation:

```bash
python -m pip install -e .
```

Always invoke pip through the intended Python interpreter. For example, a
consumer project with a `.venv` and an `external/agon-utils` submodule should
run:

```bash
.venv/bin/python -m pip install -e external/agon-utils
```

## Usage

```python
import agonutils

agonutils.hello()
compressed = agonutils.simz_encode_bytes(b"Agon")
assert agonutils.simz_decode_bytes(compressed) == b"Agon"
```
