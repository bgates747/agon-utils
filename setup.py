# setup.py
from setuptools import setup, Extension
import subprocess

def get_libpng_flags():
    """Helper function to fetch compiler/linker flags via pkg-config."""
    cflags = subprocess.check_output(['pkg-config', '--cflags', 'libpng']).decode().strip().split()
    libs = subprocess.check_output(['pkg-config', '--libs', 'libpng']).decode().strip().split()
    return cflags, libs

cflags, libs = get_libpng_flags()

module = Extension(
    'agonutils',
    sources=['src/agonutils.c', 'src/images.c'],
    include_dirs=['src'],
    extra_compile_args=cflags,
    extra_link_args=libs
)

setup(
    name='agonutils',
    version='1.0',
    description='A Python library written in C with libpng support',
    ext_modules=[module],
    zip_safe=False,  # Try to discourage egg creation
    options={"bdist_egg": {"enabled": False}} # *Really* discourage egg creation
)
