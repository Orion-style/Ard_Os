#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
profile="$repo_root/profiles/ard-base"
work_dir="$repo_root/work"
out_dir="$repo_root/out"
stable_iso="$out_dir/FlasterOS.iso"

if ! command -v mkarchiso >/dev/null 2>&1; then
  echo "mkarchiso not found. Install archiso first: sudo pacman -S archiso" >&2
  exit 1
fi

mkdir -p "$work_dir" "$out_dir"
sudo mkarchiso -v -w "$work_dir" -o "$out_dir" "$profile"

latest_iso="$(find "$out_dir" -maxdepth 1 -type f -name 'FlasterOS-*.iso' -print0 | xargs -0 -r ls -t 2>/dev/null | head -n 1)"
if [[ -z "$latest_iso" ]]; then
  echo "Build finished, but no FlasterOS ISO was found in $out_dir." >&2
  exit 1
fi

cp -f "$latest_iso" "$stable_iso"
echo "ISO ready: $stable_iso"
