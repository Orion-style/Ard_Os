#!/usr/bin/env bash
set -euo pipefail

iso="${1:-}"

if [[ -z "$iso" || ! -f "$iso" ]]; then
  echo "Usage: $0 out/FlasterOS.iso" >&2
  exit 2
fi

if ! command -v qemu-system-x86_64 >/dev/null 2>&1; then
  echo "qemu-system-x86_64 not found. Install qemu-desktop first." >&2
  exit 1
fi

ovmf_code=""
for candidate in \
  /usr/share/edk2/x64/OVMF_CODE.4m.fd \
  /usr/share/edk2/x64/OVMF_CODE.secboot.4m.fd \
  /usr/share/edk2/x64/OVMF_CODE.fd \
  /usr/share/edk2-ovmf/x64/OVMF_CODE.4m.fd \
  /usr/share/edk2-ovmf/x64/OVMF_CODE.secboot.4m.fd \
  /usr/share/edk2-ovmf/x64/OVMF_CODE.fd \
  /usr/share/OVMF/x64/OVMF_CODE.4m.fd \
  /usr/share/OVMF/x64/OVMF_CODE.fd \
  /usr/share/ovmf/x64/OVMF_CODE.4m.fd \
  /usr/share/ovmf/x64/OVMF_CODE.fd; do
  if [[ -f "$candidate" ]]; then
    ovmf_code="$candidate"
    break
  fi
done

if [[ -z "$ovmf_code" ]]; then
  echo "OVMF firmware not found. Install edk2-ovmf first." >&2
  exit 1
fi

qemu-system-x86_64 \
  -enable-kvm \
  -machine q35 \
  -m 4096 \
  -cpu host \
  -smp 4 \
  -drive if=pflash,format=raw,readonly=on,file="$ovmf_code" \
  -boot d \
  -cdrom "$iso" \
  -netdev user,id=net0 \
  -device virtio-net-pci,netdev=net0 \
  -display gtk
