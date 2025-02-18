from setuptools import setup, Extension

module = Extension(
    'agonutils',
    sources=['src/agonutils.c', 'src/images.c', 'src/agm.c', 'src/rle.c'],
    libraries=['avformat', 'avcodec', 'swscale', 'avutil', 'png16'],
    library_dirs=['/lib/x86_64-linux-gnu', '/usr/lib/x86_64-linux-gnu'],
    include_dirs=['/usr/include', '/usr/include/ffmpeg'],
)

setup(
    name='agonutils',
    version='1.0',
    description='A Python library written in C for Agon utilities',
    ext_modules=[module],
)
