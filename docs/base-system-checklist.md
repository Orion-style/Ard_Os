# Base System Checklist

Use this checklist for Stage 4 validation.

## Live ISO

- Linux kernel package is present.
- systemd is present through the base system.
- Disk, USB, and network firmware packages are present.
- Boots on UEFI firmware.
- Boots on BIOS firmware where supported by the host.
- Reaches SDDM.
- Logs into Plasma as the `ard` live user.
- `nmcli general status` shows NetworkManager running.
- Wired networking works automatically.
- Wi-Fi networks are visible in Plasma NetworkManager.
- PipeWire and WirePlumber user services are available for sound.
- Plasma offers Wayland and X11-compatible sessions.
- Firefox launches.
- Konsole launches.
- `sudo ard-install --help` works.

## Installed System

- Installer refuses to run without an explicit target disk.
- Installer asks for destructive confirmation.
- Installer creates an EFI partition and root partition.
- `pacstrap` completes.
- systemd-boot entry is created.
- Firmware loads the systemd-boot entry from the EFI system partition.
- systemd-boot loads the Linux kernel and initramfs.
- Kernel command line points at the installed root filesystem UUID.
- First reboot starts Ard OS from disk.
- systemd reaches the graphical target.
- SDDM starts.
- Plasma login works for the created user.
- Plasma desktop session opens after login.
- NetworkManager starts after reboot.
- PipeWire audio starts for the created user.
- Root has a password and is reserved for administration.
- A normal user exists with a home directory and login shell.
- User can run `sudo`.
- Games and launcher processes are started from the normal user, not root.

## User Model

The installed system must have two distinct roles:

```text
root -> administration only
normal user -> work, games, and launchers
```

Validation commands after first boot:

```bash
id "$USER"
getent passwd "$USER"
test -d "$HOME"
sudo -l
test "$(id -u)" -ne 0
```

Do not launch games, launchers, browsers, or the desktop session as root.

## Boot Chain

The installed OS is ready only when this complete chain works:

```text
BIOS/UEFI -> systemd-boot -> Linux kernel -> systemd -> SDDM -> Plasma desktop
```

Validation commands after first boot:

```bash
bootctl status
cat /proc/cmdline
systemctl is-system-running
systemctl status sddm.service
loginctl show-session "$XDG_SESSION_ID" -p Type -p Desktop
```

Failure at any step blocks Stage 4 readiness.

## Basic Work

Stage 4 passes only when the installed system works as a normal Linux desktop:

- PC powers on and reaches the bootloader.
- Bootloader starts Ard OS.
- Login screen opens.
- Normal user can log in.
- Desktop opens.
- Keyboard input works.
- Mouse or touchpad input works.
- Terminal opens.
- Internet works.
- Sound output works.
- Packages can be installed with `pacman`.
- Reboot works.
- The same checks still pass after several reboots.

Suggested validation commands:

```bash
systemctl reboot
systemctl is-system-running
nmcli general status
ping -c 3 archlinux.org
wpctl status
speaker-test -c 2 -t wav
konsole
sudo pacman -Syu --needed tree
```

Expected manual result:

```text
PC turns on.
Bootloader appears.
System loads.
Login screen opens.
Normal user logs in.
Desktop opens.
Internet works.
Sound works.
After reboot, everything still works.
```

Pay most attention to boot process, drivers, internet, user account, permissions, and stability after reboot.

Do not work on custom launchers, custom design, games, Proton, Wine, or release ISO creation in this stage.

Move to Stage 5 only after the system works stably after several reboots.

## Deferred Until Later Stages

- Steam
- Proton
- Wine
- custom launcher
- controller support tuning
- Gamescope
- MangoHud
- custom theme
- release ISO creation workflow
- graphical installer
- package repository
