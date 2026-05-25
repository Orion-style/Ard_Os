# FlasterOS 0.1.0 Release Notes

## Status

Initial release candidate.

Do not publish as final until Stage 24 release validation passes on real hardware.

## Included

- Arch Linux base.
- KDE Plasma desktop.
- Guided graphical installer.
- FlasterOS launcher.
- Wine and Steam/Proton path.
- Per-game folders, prefixes, configs, and logs.
- Settings Center for network, sound, display, performance, updates, and system actions.
- Diagnostics report generation.
- Graphical update workflow.
- Btrfs pre-update snapshots and rollback.
- GameMode, zram, shader cache defaults, MangoHud support.
- Bluetooth and Steam device rules.
- Security checks for normal-user game launches, trusted updates, and redacted logs.

## Known Issues

- NVIDIA Wayland may be unstable on some hardware; use the X11-compatible session if needed.
- Some Wi-Fi and Bluetooth adapters may need firmware not included in the base image.
- Anti-cheat protected Windows games may not work through Wine or Proton.
- Game compatibility depends on the current Wine/Proton and graphics driver stack.

## Upgrade Notes

Use Settings Center:

```text
System -> Check Updates -> Install Updates
```

A pre-update snapshot should be created before package installation.

## Recovery

If an update breaks boot, graphics, launcher, Wine/Proton, or the desktop:

1. Reboot.
2. Select **FlasterOS Previous Version**.
3. Confirm the system works.
4. Run `sudo ard-snapshot rollback latest`.

## Release Validation

Release is accepted only when:

- ISO checksum verifies.
- USB boot works.
- Guided install works.
- Installed system boots after reboot.
- Network works.
- Sound works.
- GPU and Vulkan work or a documented hardware limitation exists.
- Launcher starts.
- One Windows game starts.
- Diagnostics report is created.
- Updates work.
- Rollback works.
