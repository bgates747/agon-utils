#!/usr/bin/env bash
set -euo pipefail

project_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
workspace_dir="$(cd "${project_dir}/../../.." && pwd)"
vdp_root="${workspace_dir}/agon-vdp-sprite-transforms"
renderer_root="${workspace_dir}/vdp-gl-sprite-transforms"
config_file="${project_dir}/scripts/platformio-sprite-affine.ini"
platformio_bin="${PLATFORMIO_BIN:-${HOME}/.platformio/penv/bin/pio}"

for repository in "${vdp_root}" "${renderer_root}"; do
    if [[ ! -d "${repository}/.git" ]]; then
        printf 'Missing dedicated Git checkout: %s\n' "${repository}" >&2
        exit 1
    fi
done

if [[ ! -x "${platformio_bin}" ]]; then
    printf 'Missing PlatformIO executable: %s\n' "${platformio_bin}" >&2
    exit 1
fi

if ! rg -q 'trySetSprites' "${renderer_root}/src/displaycontroller.h" || \
   ! rg -q 'waitForSpritesRetired' "${renderer_root}/src/displaycontroller.h"; then
    printf 'Dedicated renderer lacks the checked sprite publication API\n' >&2
    exit 1
fi

repository_fingerprint() {
    local repository="$1"
    {
        git -C "${repository}" rev-parse HEAD
        git -C "${repository}" diff --binary HEAD --
        while IFS= read -r -d '' untracked_file; do
            sha256sum "${repository}/${untracked_file}"
        done < <(git -C "${repository}" ls-files --others --exclude-standard -z)
    } | sha256sum | cut -d ' ' -f 1
}

vdp_fingerprint="$(repository_fingerprint "${vdp_root}")"
renderer_fingerprint="$(repository_fingerprint "${renderer_root}")"
config_fingerprint="$(sha256sum "${config_file}" | cut -d ' ' -f 1)"
build_key="$(printf '%s\n%s\n%s\n' \
    "${vdp_fingerprint}" \
    "${renderer_fingerprint}" \
    "${config_fingerprint}" | sha256sum | cut -c 1-16)"
build_root="${project_dir}/build/platformio-${build_key}"

export SPRITE_AFFINE_PIO_BUILD_DIR="${build_root}/build"
export SPRITE_AFFINE_PIO_LIBDEPS_DIR="${build_root}/libdeps"
export SPRITE_AFFINE_RENDERER_ROOT="${renderer_root}"

printf 'Sprite-affine source fingerprint: %s\n' "${build_key}"
"${platformio_bin}" run \
    -d "${vdp_root}" \
    -c "${config_file}" \
    -e esp32dev \
    -j 2 \
    "$@"

installed_renderer="${SPRITE_AFFINE_PIO_LIBDEPS_DIR}/esp32dev/vdp-gl/src"
if [[ ! -d "${installed_renderer}" ]]; then
    printf 'PlatformIO did not install the expected local renderer: %s\n' \
        "${installed_renderer}" >&2
    exit 1
fi
if ! diff -qr "${renderer_root}/src" "${installed_renderer}"; then
    printf 'PlatformIO renderer copy differs from the dedicated checkout\n' >&2
    exit 1
fi

firmware_bin="${SPRITE_AFFINE_PIO_BUILD_DIR}/esp32dev/firmware.bin"
if [[ -f "${firmware_bin}" ]]; then
    sha256sum "${firmware_bin}"
    printf 'Verified firmware: %s\n' "${firmware_bin}"
fi
