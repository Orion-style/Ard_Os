# Ard OS Base System

This repository starts Ard OS as an Arch Linux based distribution foundation.

Stage 4 is intentionally narrow: boot a live ISO, load a graphical desktop, connect to the internet, install to disk, and keep working after reboot. It does not include Proton, a game launcher, game libraries, or custom branding beyond the minimum Ard OS identity.

## Base Choice

Ard OS v0 uses Arch Linux as the base.

Reasons:

- Arch is flexible and small enough to shape into a custom distribution.
- `archiso` is the standard tool for building bootable Arch-based images.
- The Linux kernel and Arch package repositories let this stage focus on system integration instead of kernel development.

## What This Contains

- `profiles/ard-base`: an `archiso` profile for the Ard OS base live ISO.
- `profiles/ard-base/packages.x86_64`: packages included in the live environment.
- `profiles/ard-base/airootfs`: files copied into the live ISO root filesystem.
- `scripts/build-iso.sh`: build helper for Linux hosts.
- `scripts/test-qemu.sh`: QEMU boot test helper.

## Build Requirements

Build from an Arch Linux system or Arch container with:

```bash
sudo pacman -Syu archiso qemu-desktop edk2-ovmf
```

Then run:

```bash
bash scripts/build-iso.sh
```

The ISO will be written to `out/`.

## Test The ISO

```bash
bash scripts/test-qemu.sh out/ard-os-YYYY.MM.DD-x86_64.iso
```

Expected result:

- The ISO boots.
- The `ard` live user logs into KDE Plasma automatically.
- NetworkManager is active.
- The installer command exists at `/usr/local/bin/ard-install`.

## Install To Disk

From the live desktop, open Konsole and run:

```bash
sudo ard-install --disk /dev/nvme0n1 --hostname ard-os --username ard
```

The installer is destructive and asks for confirmation before touching the target disk.

After install and reboot:

- systemd-boot starts the installed Ard OS system.
- KDE Plasma starts through SDDM.
- NetworkManager manages internet access.
- The created user can use `sudo`.

## Current Scope

Included:

- Arch Linux base
- Linux kernel
- systemd boot flow
- KDE Plasma desktop
- SDDM display manager
- NetworkManager
- Firefox
- Installer script for UEFI systems

Deferred:

- Proton
- Steam or game launcher
- GPU vendor tuning
- Ard OS theme and branding
- Secure Boot signing
- Calamares or a graphical installer
- custom package repository
