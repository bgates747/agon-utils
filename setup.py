import shlex
import subprocess

from setuptools import Extension, setup


REQUIRED_NATIVE_PACKAGES = [
    "libavformat",
    "libavcodec",
    "libswscale",
    "libavutil",
    "libpng",
]


def get_pkg_config_flags(packages):
    """Return portable compiler and linker flags for the native dependencies."""
    try:
        cflags = subprocess.check_output(
            ["pkg-config", "--cflags", *packages], text=True
        )
        libs = subprocess.check_output(
            ["pkg-config", "--libs", *packages], text=True
        )
    except FileNotFoundError as exc:
        raise RuntimeError(
            "pkg-config is required to build agonutils. Install pkg-config and "
            "the FFmpeg/libpng development packages."
        ) from exc
    except subprocess.CalledProcessError:
        package_list = ", ".join(packages)
        raise RuntimeError(
            f"Missing native build dependencies: {package_list}. Install the "
            "corresponding FFmpeg and libpng development packages."
        ) from None

    return shlex.split(cflags), shlex.split(libs)


cflags, libs = get_pkg_config_flags(REQUIRED_NATIVE_PACKAGES)

module = Extension(
    "agonutils",
    sources=[
        "src/agonutils.c",
        "src/images.c",
        "src/agm.c",
        "src/rle.c",
        "src/simz.c",
    ],
    include_dirs=["src"],
    define_macros=[("PY_SSIZE_T_CLEAN", None)],
    extra_compile_args=cflags,
    extra_link_args=libs,
)

setup(
    name="agonutils",
    version="1.1.0",
    description="Native image, palette, AGM, RLE, and SIMZ utilities for Agon tooling",
    python_requires=">=3.10",
    ext_modules=[module],
    zip_safe=False,
)
