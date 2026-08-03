#!/usr/bin/env bash
set -euo pipefail

readonly mount_root="/media/smith/AGON"
readonly target_relative="mystuff/tests/sprite_xfrms"
readonly project_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
readonly target_dir="${mount_root}/${target_relative}"

if (( $# != 0 )); then
    printf 'Usage: %s\n' "$0" >&2
    exit 2
fi

fail() {
    printf 'Sprite fixture deployment refused: %s\n' "$*" >&2
    exit 1
}

[[ -d "${mount_root}" ]] || fail "mount root is missing: ${mount_root}"
[[ ! -L "${mount_root}" ]] || fail "mount root is a symlink: ${mount_root}"
mountpoint -q -- "${mount_root}" || fail "not a mount point: ${mount_root}"

resolved_mount="$(readlink -f -- "${mount_root}")"
[[ -n "${resolved_mount}" && "${resolved_mount}" == "${mount_root}" ]] ||
    fail "unexpected mount-root resolution: ${resolved_mount:-<empty>}"
[[ "${target_dir}" == "${mount_root}/"* ]] ||
    fail "target escaped the mount root: ${target_dir}"

declare -A expected_sha=(
    [sprite_affine_transforms.bin]=9d51d861a625cdb242a3259cf9c1ff1484a588fb6508d54afbb531a318472fc2
    [sprite_affine_formats.bin]=a9a558c49360ce02796f051934f48e8c18dac67bbf76d65a81d200306a4bc285
    [sprite_affine_torture.bin]=c7c1ca74dea30b15cab1d99ccf6af780e5aaa159a1126e8c610bb10e9dcbb99c
)

readonly -a fixture_names=(
    sprite_affine_transforms.bin
    sprite_affine_formats.bin
    sprite_affine_torture.bin
)

for name in "${fixture_names[@]}"; do
    source_file="${project_dir}/build/${name}"
    [[ -f "${source_file}" && ! -L "${source_file}" ]] ||
        fail "fixture is not a regular file: ${source_file}"
    actual_sha="$(sha256sum -- "${source_file}")"
    actual_sha="${actual_sha%% *}"
    [[ "${actual_sha}" == "${expected_sha[${name}]}" ]] ||
        fail "fixture checksum mismatch: ${source_file}"
done

current_path="${mount_root}"
for component in mystuff tests sprite_xfrms; do
    next_path="${current_path}/${component}"
    [[ ! -L "${next_path}" ]] || fail "refusing symlinked path: ${next_path}"
    if [[ -e "${next_path}" && ! -d "${next_path}" ]]; then
        fail "path exists but is not a directory: ${next_path}"
    fi
    current_path="${next_path}"
done

mkdir -p -- "${target_dir}"
resolved_target="$(readlink -f -- "${target_dir}")"
[[ -n "${resolved_target}" && "${resolved_target}" == "${target_dir}" ]] ||
    fail "unexpected target resolution: ${resolved_target:-<empty>}"

if ! unsafe_entry="$(find -P "${target_dir}" -mindepth 1 \
    ! -type f ! -type d -print -quit)"; then
    fail "could not inspect existing destination contents"
fi
[[ -z "${unsafe_entry}" ]] ||
    fail "destination contains a symlink or special entry: ${unsafe_entry}"

printf 'Replacing contents of %s\n' "${target_dir}"
find -P "${target_dir}" -mindepth 1 -depth -delete

for name in "${fixture_names[@]}"; do
    source_file="${project_dir}/build/${name}"
    destination_file="${target_dir}/${name}"
    cp -- "${source_file}" "${destination_file}"
    copied_sha="$(sha256sum -- "${destination_file}")"
    copied_sha="${copied_sha%% *}"
    [[ "${copied_sha}" == "${expected_sha[${name}]}" ]] ||
        fail "copied fixture checksum mismatch: ${destination_file}"
done

sync -- "${target_dir}"

printf 'Deployed accepted SpriteAffine fixtures:\n'
for name in "${fixture_names[@]}"; do
    printf '  %s  %s\n' "${expected_sha[${name}]}" "${target_dir}/${name}"
done
