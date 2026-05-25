# ISO Creation Checklist

Use this checklist for Stage 15 validation.

At this stage, FlasterOS must be an installable `.iso` image that can be written to a USB drive and booted separately from the development machine.

## 15.1 Archiso Profile

The archiso profile is:

```text
profiles/ard-base
```

It must contain:

- Package list: `packages.x86_64`.
- System configs: `airootfs/etc`.
- User defaults and theme settings: `airootfs/etc/skel`.
- Launcher and tools: `airootfs/opt/ard-os` and `airootfs/usr/local/bin`.
- Desktop entries and sessions: `airootfs/usr/share`.
- Service setup: `airootfs/root/customize_airootfs.sh`.

Validation:

- `profiledef.sh` uses FlasterOS ISO metadata.
- File permissions mark launcher, settings, diagnostics, installer, and snapshot tools executable.
- The live user is created by the profile, not copied from a personal machine.

## 15.2 Packages

The package list must include:

- Kernel and firmware.
- Graphics stack and Vulkan tools.
- AMD and Intel Vulkan drivers.
- Sound stack with PipeWire and WirePlumber.
- NetworkManager.
- KDE Plasma graphical session.
- Launcher runtime dependencies.
- Wine, Steam, DXVK/VKD3D-related packages, Gamescope, MangoHud, and Gamemode.
- Diagnostic tools such as `pciutils`, `vulkan-tools`, `mesa-utils`, `curl`, and `jq`.
- VM guest packages for QEMU and VirtualBox.
- Proton preparation helper: `ard-prepare-proton`.
- Wine-prefix DXVK helper: `ard-setup-wine-dxvk`.

Validation:

- `mkarchiso` resolves the package list.
- QEMU and VirtualBox guest services are enabled with best-effort `systemctl enable ... || true`.

## 15.3 Configs

The ISO must already configure:

- NetworkManager.
- PipeWire audio.
- SDDM graphical login.
- KDE desktop session.
- FlasterOS Gaming Mode session.
- Launcher desktop icon.
- Settings Center desktop icon.
- Diagnostics desktop icon.
- Diagnostics command and Python backend installed into the target system.
- FlasterOS `/etc/os-release` copied into the installed system.
- Baseline KDE theme/user settings.

Validation:

- Live boot reaches the graphical desktop.
- NetworkManager is active.
- PipeWire and WirePlumber are active.
- Launcher opens from the desktop.
- Settings Center opens from the desktop.
- No personal passwords or private machine files are present.

## 15.4 Build The ISO

Build:

```bash
bash scripts/build-iso.sh
```

Expected stable output:

```text
out/FlasterOS.iso
```

QEMU test:

```bash
bash scripts/test-qemu.sh out/FlasterOS.iso
```

Validation:

- ISO boots in QEMU.
- ISO boots in VirtualBox.
- ISO boots from a USB drive on UEFI hardware.
- Live system opens.
- Internet works.
- Graphics work.
- Launcher is present.
- Settings Center is present.
- Installer is present.

## Stage 15 Result

Stage 15 passes when:

- `out/FlasterOS.iso` is created.
- The ISO boots stably in a virtual machine.
- The ISO boots from a USB drive.
- The live system opens without a terminal-only recovery path.
- Internet, graphics, launcher, Settings Center, and installer are usable.

Move to Stage 16 only when the ISO boots stably.
