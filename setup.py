from setuptools import setup, Extension
import platform
import sys

module = Extension(
    'agonutils',
    sources=['src/agonutils.c', 'src/images.c'],
    libraries=['png16'],  # Explicitly link libpng16
    library_dirs=['/lib/x86_64-linux-gnu'],  # Ensure correct path
    include_dirs=['/usr/include']
)

setup(
    name='agonutils',
    version='1.0',
    description='A Python library written in C',
    ext_modules=[module],
    platforms=sys.platform,
)
