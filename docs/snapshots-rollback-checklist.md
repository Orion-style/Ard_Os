# Snapshots And Rollback Checklist

Use this checklist for Stage 14 validation.

Updates can break graphics drivers, Wine, Proton, DXVK, VKD3D, the desktop, or the launcher. Ard OS must create a restore point before updating and give the user a bootloader path back to the previous working system.

## 14.1 Use btrfs

New installs must use btrfs for the root partition and for `/home`.

Required root subvolumes:

- `@`: system root.
- `@games`: installed games, prefixes, and game data.
- `@var_log`: system logs.
- `@snapshots`: system restore points.

Validation:

- `/` is mounted from btrfs subvolume `@`.
- `/home` is mounted from a separate btrfs home partition.
- `/games` is mounted from `@games`.
- `/var/log` is mounted from `@var_log`.
- `/.snapshots` is mounted from `@snapshots`.
- Personal files and game data are not included in system root rollback.

## 14.2 Create A Snapshot Before Updating

When the user presses **Install Updates** in the Settings Center:

- `/usr/local/bin/ard-snapshot pre-update` runs before `pacman -Syu`.
- A snapshot named `pre-update-YYYYMMDD-HHMMSS` is created.
- Matching boot files are copied to `/boot/ard-snapshots/SNAPSHOT_NAME`.
- `/boot/loader/entries/ard-os-previous.conf` points to the newest snapshot.
- `/boot/loader/entries/ard-os-recovery.conf` exists.
- Snapshot creation and update output are appended to `/var/log/flasteros/update.log`.

Validation:

- If snapshot creation fails, the update does not start.
- A failed update still leaves the pre-update snapshot available.
- Old pre-update snapshots are pruned so only the newest five remain.
- Snapshot names are clear enough to identify when they were created.

## 14.3 Add Recovery Menu

The systemd-boot menu must offer:

- **FlasterOS**: normal system.
- **FlasterOS Previous Version**: newest pre-update snapshot.
- **FlasterOS Recovery**: rescue target on the normal root.

Validation:

- Normal boot starts the current `@` system.
- Previous Version boots the newest snapshot.
- Recovery starts rescue mode.
- Previous Version uses the boot files saved with that snapshot.

## 14.4 Permanent Rollback

If the updated system is broken:

1. Reboot.
2. Select **FlasterOS Previous Version**.
3. Confirm the desktop, graphics, launcher, and compatibility stack work.
4. Run:

```bash
sudo ard-snapshot rollback latest
```

Validation:

- The previous snapshot becomes the normal `@` root.
- The broken root is preserved as `@broken-YYYYMMDD-HHMMSS`.
- Matching boot files are restored from `/boot/ard-snapshots/SNAPSHOT_NAME`.
- The next normal boot starts the restored system.

## Stage 14 Result

Stage 14 passes when:

- A btrfs Ard OS install creates the required subvolumes.
- Installing updates from the Settings Center creates a pre-update snapshot first.
- The bootloader shows normal, previous version, and recovery entries.
- A deliberately broken update can be recovered by booting the previous snapshot.
- Permanent rollback makes that snapshot the normal boot target.

Move to Stage 15 only when rollback works after a failed update.
