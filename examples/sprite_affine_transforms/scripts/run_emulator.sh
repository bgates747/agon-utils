#!/usr/bin/env bash
set -euo pipefail

project_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
profile="${project_dir}/emulator"
module_name="vdp_sprite_affine_transforms.so"

if [[ "$(< "${profile}/.bespoke-vdp-profile")" != "${module_name}" ]]; then
    printf 'Invalid or missing bespoke VDP marker\n' >&2
    exit 1
fi

for input in fab-agon-emulator mos_console8.bin mos_console8.map "${module_name}" sdcard; do
    if [[ ! -e "${profile}/${input}" ]]; then
        printf 'Missing bespoke emulator input: %s\n' "${profile}/${input}" >&2
        exit 1
    fi
done

fab_bin="$(readlink -f "${profile}/fab-agon-emulator")"
mos_bin="$(readlink -f "${profile}/mos_console8.bin")"
vdp_module="$(readlink -f "${profile}/${module_name}")"
sdcard_dir="$(readlink -f "${profile}/sdcard")"
run_root="$(mktemp -d "${TMPDIR:-/tmp}/fab-sprite-affine.XXXXXX")"
trap 'rmdir -- "${run_root}"' EXIT

if [[ -f "${HOME}/.local/lib/libSDL3.so.0" ]]; then
    export LD_LIBRARY_PATH="${HOME}/.local/lib${LD_LIBRARY_PATH:+:${LD_LIBRARY_PATH}}"
fi

cd "${run_root}"
(
    SDL_VIDEODRIVER=wayland "${fab_bin}" \
        --renderer sw \
        --firmware console8 \
        --mos "${mos_bin}" \
        --vdp "${vdp_module}" \
        --sdcard "${sdcard_dir}" \
        --verbose -z
)
