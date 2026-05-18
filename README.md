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
- `docs/gaming-os-structure-checklist.md`: Stage 7 game folder, prefix, config, and log structure.
- `docs/game-launcher-checklist.md`: Stage 8 launcher validation.
- `docs/game-profiles-checklist.md`: Stage 9 per-game launch profile validation.

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

Steam is the first Proton path. Proton supplies the gaming Wine runtime plus DXVK for DirectX 9/10/11 and VKD3D-Proton for DirectX 12:

```text
DirectX 11 -> DXVK -> Vulkan
DirectX 12 -> VKD3D-Proton -> Vulkan
```

Stage 6 passes when `.exe` files start, a Wine prefix is created, Steam starts, a simple Windows game starts through Wine or Proton, and MangoHud can show FPS. Do not bypass anti-cheat; anti-cheat failure is a compatibility limitation.

## Gaming OS Structure

Stage 7 separates OS files from game files:

```text
/opt/ard-os/       OS programs
/games/            installed games and per-game runtime data
/var/log/ard-os/   OS logs
/home/user/        user files
```

Each game gets its own folder, Wine prefix, `config.json`, and logs:

```bash
ard-create-game --id GameName --name "Game Name" --exe /games/GameName/game.exe
ard-run-game /games/GameName/config.json
```

Do not store games in system folders, do not run games as root, do not use one Wine prefix for all games, and do not mix logs between games.

## Game Launcher

Stage 8 adds the main launcher interface:

```bash
ard-launcher
```

The launcher scans `/games/*/config.json`, lists games, launches through the configured runner, writes logs, and shows specific errors such as missing executables, missing prefixes, missing runners, permission problems, and Wine launch failures.

Stage 8 passes when the launcher opens, games appear in the list, Play launches a game, errors are visible in the interface, logs are saved, and at least 2-3 different programs can start from configs.

## Game Profiles

Stage 9 makes each game's launch method configurable in its own `config.json`. Profiles support Wine, Proton, Proton Experimental, custom runners, per-game environment variables, launch arguments, Gamescope settings, and MangoHud toggles.

Settings remain per game. Do not use one global profile for all games, and do not edit launcher code just to change one game's launch method.

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
- Steam, Proton path, DXVK/VKD3D validation, and gaming helper tools
- structured game directories, per-game configs, prefixes, and logs
- graphical game launcher
- per-game launch profiles
- Firefox
- Installer script for UEFI systems

Deferred:

- GPU vendor tuning
- Ard OS theme and branding
- Secure Boot signing
- release ISO creation workflow
- Calamares or a graphical installer
- custom package repository
