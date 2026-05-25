# FlasterOS Download Page Draft

## Download

Current release:

```text
FlasterOS 0.1.0
```

Files:

```text
FlasterOS-0.1.0.iso
FlasterOS-0.1.0.iso.sha256
```

Verify:

```bash
sha256sum -c FlasterOS-0.1.0.iso.sha256
```

## System Requirements

Minimum:

- x86_64 PC.
- UEFI firmware.
- 4 GB RAM.
- 256 GB SSD storage.
- AMD, Intel, or NVIDIA GPU with Vulkan-capable driver support.
- USB drive for installation.
- Internet connection for updates and game downloads.

Recommended:

- 8 GB RAM or more.
- 512 GB SSD storage for Genshin Impact + Honkai: Star Rail + Zenless Zone Zero testing.
- AMD or Intel GPU for the simplest open-driver path.
- Wired Ethernet during installation if Wi-Fi hardware is unknown.

## Installation Guide

Use:

```text
docs/beta-user-guide.md
```

Release installation summary:

1. Download the ISO.
2. Verify the SHA256 checksum.
3. Write the ISO to USB.
4. Boot from USB.
5. Open **Install FlasterOS**.
6. Select target disk.
7. Create user.
8. Install and reboot.
9. Open launcher.
10. Start a game.

## Known Issues

See:

```text
docs/release-notes.md
```

Do not publish a release with unresolved critical boot, installer, update, rollback, or launcher failures.

## Supported Games

See:

```text
docs/game-compatibility-table.md
docs/hoyoverse-compatibility.md
```

Compatibility depends on GPU drivers, Wine/Proton version, anti-cheat, and game updates.

## Recovery

Before updates, FlasterOS creates a btrfs snapshot. If an update breaks the system, reboot and select:

```text
FlasterOS Previous Version
```

If that version works, make rollback permanent:

```bash
sudo ard-snapshot rollback latest
```
