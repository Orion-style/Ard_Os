# Installer Checklist

Use this checklist for Stage 16 validation.

Stage 16 replaces terminal-driven installation with a guided installer. A normal user should boot the USB drive, start the installer from the desktop, answer the prompts, and reboot into the installed system without typing installation commands.

## Language Selection

The installer must offer at least:

- English
- Russian

The selected language controls the installer text and the installed system locale:

- English uses `en_US.UTF-8`.
- Russian uses `ru_RU.UTF-8`.

## Disk Selection

The installer must show available block disks with device path, size, model, and removable flag.

Before installation starts, it must show a destructive warning and require confirmation for the exact selected disk. The installer must not start if no disk is selected.

High-risk checks:

- Do not select the USB installer drive.
- Confirm the disk size and model before erasing.
- Re-scan disks after adding or removing storage.

## Disk Partitioning

The installed disk must use this minimum scheme:

```text
EFI     FAT32, mounted at /boot
/       btrfs, mounted as the system root
/home   btrfs, mounted as user data
```

The root partition also contains Ard OS system subvolumes for games, logs, and snapshots. `/home` is a separate btrfs partition so user data is not part of system rollback.

Storage requirements for gaming:

- Minimum target disk: 256 GiB SSD.
- Recommended for Genshin Impact + Honkai: Star Rail + Zenless Zone Zero: 512 GiB SSD.
- `/games` lives on the root btrfs partition and should have at least 200-300 GiB available for serious testing.

The installer must reject disks smaller than 256 GiB.

## User Creation

The user enters:

- username
- password
- computer name

The installer validates the username and computer name before starting. The created user is added to `wheel` for administration through `sudo`. The root account is locked after installation; daily work, games, launchers, and the desktop use the created normal user.

## Installed Branding And Tools

The installed system must receive FlasterOS identity and tools from the live profile, not fall back to plain Arch defaults for user-facing identity.

Required installed files:

```text
/etc/os-release
/usr/local/bin/ard-check-system
/opt/ard-os/diagnostics/ard-diagnostics.py
/usr/share/applications/ard-diagnostics.desktop
/etc/pacman.conf
```

Validation after installation:

```bash
grep -E '^(NAME|PRETTY_NAME|ID)=' /etc/os-release
test -x /usr/local/bin/ard-check-system
test -x /opt/ard-os/diagnostics/ard-diagnostics.py
test -f /usr/share/applications/ard-diagnostics.desktop
grep -A1 '^\[multilib\]' /etc/pacman.conf
ard-check-system --report
```

## Bootloader Installation

The installer installs `systemd-boot` to the new EFI partition and writes a `FlasterOS` boot entry.

The boot entry must:

- load the installed Linux kernel and initramfs from `/boot`
- use the installed root filesystem UUID
- mount the btrfs `@` subvolume as `/`
- boot automatically by default

## Stage 16 Result

Stage 16 passes when this full path works:

- booted from USB drive
- started installer from the desktop
- selected language
- selected disk
- confirmed destructive install warning
- created user
- installed OS
- rebooted
- system started from disk
- logged in as the created user

## Dangerous Areas

Most dangerous areas:

- accidentally deleting the wrong disk
- selecting the USB drive instead of the target disk
- writing boot files to the wrong EFI partition
- failing to create a valid `/home` mount
- bootloader not installed
- system not found after reboot

## Move To Stage 17

Move to Stage 17 when Ard OS installs on a clean disk and boots from that disk without terminal commands.
