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
- `docs/graphics-drivers-checklist.md`: Stage 5 graphics and driver validation.
- `docs/gaming-compatibility-checklist.md`: Stage 6 Wine and Windows compatibility validation.

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
- The Linux kernel starts from the installed root filesystem.
- systemd reaches the graphical target.
- KDE Plasma starts through SDDM.
- NetworkManager manages internet access.
- The created user can use `sudo`.
- The created user is the normal account for work, games, and launchers.

## User Model

Ard OS uses `root` only for administration. Daily work, games, launchers, browsers, and the desktop session run as the normal user created by the installer.

The default installed user is `ard` unless another name is passed with `--username`. That user has a home directory, a login shell, and `sudo` access through the `wheel` group.

Games must not be launched as root.

## Boot Chain

Ard OS is not ready until the full boot chain succeeds:

```text
BIOS/UEFI -> systemd-boot -> Linux kernel -> systemd -> SDDM login screen -> KDE Plasma desktop
```

The installer configures this chain by creating an EFI system partition, installing systemd-boot, writing `/boot/loader/entries/ard-os.conf`, using the root filesystem UUID in the kernel command line, and enabling `sddm.service`.

## Basic Work Check

At the end of Stage 4, Ard OS should be a normal working Linux system. The PC should turn on, show the bootloader, load the system, open the login screen, log into the normal user account, open the desktop, reach the internet, play sound, install packages, and keep doing the same after reboot.

Do not work on custom launchers, custom design, games, Proton, Wine, or release ISO creation in this stage. Do not move to Stage 5 until the basic checks still pass after several reboots.

## Graphics And Drivers

Stage 5 starts by identifying the installed graphics card. Run:

```bash
lspci -nnk | grep -EA3 'VGA|3D|Display'
```

Record whether the system uses NVIDIA, AMD, Intel, or hybrid graphics before choosing drivers. Gaming work should not start until GPU, Vulkan, OpenGL, resolution, refresh rate, and hardware acceleration are verified.

For AMD and Intel systems, the base install includes Mesa, Vulkan loader/drivers, and validation tools. For NVIDIA systems, identify the exact GPU first, then install the NVIDIA driver set:

```bash
sudo ard-install-gpu-drivers --vendor nvidia
```

Vulkan must pass before Proton work:

```text
Windows game -> DirectX -> DXVK/VKD3D -> Vulkan -> graphics card
```

Validate it with:

```bash
vulkaninfo --summary
```

The reported GPU must be the real NVIDIA, AMD, or Intel device, not a software renderer.

OpenGL must also report the real GPU:

```bash
glxinfo -B
```

This covers older games, desktop components, interfaces, and graphics tests.

Display validation must also pass: correct resolution, correct refresh rate, multiple monitors if connected, working screen after sleep, no black screen after reboot, and 3D applications starting. Move to Stage 6 only when Vulkan and OpenGL work without errors and the display is stable after sleep and reboot.

## Gaming Compatibility Layer

Stage 6 adds basic Windows program support through Wine:

```text
.exe game -> Wine/Proton -> DXVK/VKD3D -> Vulkan -> Linux -> graphics card
```

Install or refresh the base Wine set with:

```bash
sudo ard-install-gaming-compat
```

Run Wine as the normal user, not root. Do not continue to Proton, DXVK, VKD3D, or launchers until `wine --version`, `wineboot --init`, and `winecfg` work.

## Current Scope

Included:

- Arch Linux base
- Linux kernel
- systemd boot flow
- disk, USB, and firmware support through Arch base packages
- KDE Plasma desktop
- Wayland and X11-compatible display stack
- SDDM display manager
- NetworkManager
- PipeWire audio with WirePlumber
- GPU identification tools
- AMD/Intel Mesa and Vulkan driver packages
- Wine base compatibility packages
- Firefox
- Installer script for UEFI systems

Deferred:

- Proton
- Steam or game launcher
- custom launcher
- GPU vendor tuning
- Ard OS theme and branding
- Secure Boot signing
- release ISO creation workflow
- Calamares or a graphical installer
- custom package repository
