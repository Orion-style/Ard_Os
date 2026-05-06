# Base System Checklist

Use this checklist for Stage 4 validation.

## Live ISO

- Boots on UEFI firmware.
- Boots on BIOS firmware where supported by the host.
- Reaches SDDM.
- Logs into Plasma as the `ard` live user.
- `nmcli general status` shows NetworkManager running.
- Wired networking works automatically.
- Wi-Fi networks are visible in Plasma NetworkManager.
- Firefox launches.
- Konsole launches.
- `sudo ard-install --help` works.

## Installed System

- Installer refuses to run without an explicit target disk.
- Installer asks for destructive confirmation.
- Installer creates an EFI partition and root partition.
- `pacstrap` completes.
- systemd-boot entry is created.
- First reboot starts Ard OS from disk.
- SDDM starts.
- Plasma login works for the created user.
- NetworkManager starts after reboot.
- User can run `sudo`.

## Deferred Until Later Stages

- Steam
- Proton
- controller support tuning
- Gamescope
- MangoHud
- custom theme
- graphical installer
- package repository
