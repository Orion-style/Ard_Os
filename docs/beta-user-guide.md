# FlasterOS Beta User Guide

This is a beta test version. Errors are possible.

Use a test PC or a disk you are ready to erase. The installer deletes the selected disk.

## Download The ISO

Download:

```text
FlasterOS.iso
```

If a checksum is provided with the download, verify it before writing the USB drive.

## Write The USB Drive

Use a trusted imaging tool such as Fedora Media Writer, Balena Etcher, Rufus in DD mode, or `dd` on Linux.

Linux example:

```bash
sudo dd if=FlasterOS.iso of=/dev/sdX bs=4M status=progress oflag=sync
```

Replace `/dev/sdX` with the USB drive device. Choosing the wrong drive can delete data.

## Install FlasterOS

1. Boot from the USB drive.
2. Wait for the live desktop.
3. Open **Install FlasterOS**.
4. Choose language.
5. Select the target disk.
6. Confirm the destructive warning.
7. Create your user.
8. Wait for installation to finish.
9. Reboot and remove the USB drive.

## Start A Game

1. Log in as your normal user.
2. Open **FlasterOS Launcher**.
3. Add or select a game.
4. Check that the game files are under `/games`.
5. Press **Play**.

If the game fails, open **Logs** in the launcher.

## Send A Log

Open diagnostics:

```text
Launcher -> Check System -> Create report
```

Or run:

```bash
ard-check-system --report
```

Send:

- `~/ard-diagnostics/report.txt`
- `/games/GameName/logs/last-launch.log` if a game failed
- `/var/log/flasteros/update.log` if an update failed
- your PC or laptop model
- GPU model
- Wi-Fi adapter model if network failed
- what you clicked before the problem
- whether the problem still happens after reboot

Do not send passwords, personal files, screenshots with private information, or game account tokens.
