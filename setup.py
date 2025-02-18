import sys
import subprocess
from setuptools import setup, Extension

# Function to get compiler flags using pkg-config
def get_pkg_config_flags(packages):
    try:
        cflags = subprocess.check_output(["pkg-config", "--cflags"] + packages).decode().strip().split()
        libs = subprocess.check_output(["pkg-config", "--libs"] + packages).decode().strip().split()
        return cflags, libs
    except subprocess.CalledProcessError:
        print(f"Warning: pkg-config failed for {packages}. Check if they are installed.")
        return [], []

# List of required libraries
ffmpeg_packages = ["libavformat", "libavcodec", "libswscale", "libavutil", "libpng"]

# Get flags from pkg-config
include_dirs, extra_link_args = get_pkg_config_flags(ffmpeg_packages)

# Set library directories dynamically for macOS and Linux
if sys.platform == "darwin":  # macOS
    library_dirs = ["/usr/local/lib", "/opt/homebrew/lib"]
    include_dirs += ["/usr/local/include", "/opt/homebrew/include"]
elif sys.platform == "linux":
    library_dirs = ["/usr/lib/x86_64-linux-gnu", "/lib/x86_64-linux-gnu"]
    include_dirs += ["/usr/include", "/usr/include/ffmpeg"]

module = Extension(
    'agonutils',
    sources=['src/agonutils.c', 'src/images.c', 'src/agm.c', 'src/rle.c', 'src/simz.c'],
    libraries=['avformat', 'avcodec', 'swscale', 'avutil', 'png16'],
    library_dirs=library_dirs,
    include_dirs=include_dirs,
    extra_link_args=extra_link_args
)

setup(
    name='agonutils',
    version='1.0',
    description='A Python library written in C for Agon utilities',
    ext_modules=[module],
)
