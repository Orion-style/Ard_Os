#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
version_file="$repo_root/VERSION"
version="${FLASTEROS_VERSION:-}"

if [[ -z "$version" && -f "$version_file" ]]; then
  version="$(tr -d '[:space:]' < "$version_file")"
fi
if [[ -z "$version" ]]; then
  version="$(date +%Y.%m.%d)"
fi

out_dir="$repo_root/out"
archive="$out_dir/FlasterOS-source-$version.tar.gz"
mkdir -p "$out_dir"

tar \
  --exclude='.git' \
  --exclude='work' \
  --exclude='out' \
  --exclude='*.pyc' \
  --exclude='__pycache__' \
  -C "$repo_root" \
  -czf "$archive" .

echo "Source archive ready: $archive"
