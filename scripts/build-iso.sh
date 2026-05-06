#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
profile="$repo_root/profiles/ard-base"
work_dir="$repo_root/work"
out_dir="$repo_root/out"

if ! command -v mkarchiso >/dev/null 2>&1; then
  echo "mkarchiso not found. Install archiso first: sudo pacman -S archiso" >&2
  exit 1
fi

mkdir -p "$work_dir" "$out_dir"
sudo mkarchiso -v -w "$work_dir" -o "$out_dir" "$profile"
