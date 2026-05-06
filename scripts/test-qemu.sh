#!/usr/bin/env bash
set -euo pipefail

iso="${1:-}"

if [[ -z "$iso" || ! -f "$iso" ]]; then
  echo "Usage: $0 out/ard-os-YYYY.MM.DD-x86_64.iso" >&2
  exit 2
fi

if ! command -v qemu-system-x86_64 >/dev/null 2>&1; then
  echo "qemu-system-x86_64 not found. Install qemu-desktop first." >&2
  exit 1
fi

qemu-system-x86_64 \
  -enable-kvm \
  -m 4096 \
  -cpu host \
  -smp 4 \
  -boot d \
  -cdrom "$iso" \
  -netdev user,id=net0 \
  -device virtio-net-pci,netdev=net0 \
  -display gtk
