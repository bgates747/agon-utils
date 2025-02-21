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
cflags, libs = get_pkg_config_flags(ffmpeg_packages)

# Set library directories dynamically for macOS and Linux
library_dirs = []
if sys.platform == "darwin":  # macOS
    library_dirs = ["/usr/local/lib", "/opt/homebrew/lib"]
    cflags += ["-I/usr/local/include", "-I/opt/homebrew/include"]
elif sys.platform == "linux":
    library_dirs = ["/usr/lib/x86_64-linux-gnu", "/lib/x86_64-linux-gnu"]
    cflags += ["-I/usr/include", "-I/usr/include/ffmpeg"]

module = Extension(
    'agonutils',
    sources=['src/agonutils.c', 'src/images.c', 'src/agm.c', 'src/rle.c', 'src/simz.c'],
    libraries=['avformat', 'avcodec', 'swscale', 'avutil', 'png16'],
    library_dirs=library_dirs,
    include_dirs=['src'],  # Keeping 'src' in include_dirs
    extra_compile_args=cflags,
    extra_link_args=libs
)

setup(
    name='agonutils',
    version='1.0',
    description='A Python library written in C with libpng and FFmpeg support',
    ext_modules=[module],
    zip_safe=False,  # Discourage egg creation
    options={"bdist_egg": {"enabled": False}}  # Strongly discourage egg creation
)
