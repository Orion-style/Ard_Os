# FlasterOS / Ard OS Base System

FlasterOS / Ard OS is an Arch-based gaming distribution. It is not a standalone operating system with its own kernel. The project uses the Linux kernel, Arch Linux packages, systemd, KDE Plasma, Wine/Proton, and gaming tools to build a focused installable gaming system.

Current naming note: `FlasterOS` is the public ISO/branding name. Some internal tools and paths still use the older `ard-*` prefix. This must be cleaned up before a polished public release.

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
- `docs/gaming-mode-checklist.md`: Stage 10 Gaming Mode session validation.
- `docs/settings-center-checklist.md`: Stage 11 Settings Center validation.
- `docs/diagnostics-checklist.md`: Stage 12 diagnostics and report validation.
- `docs/updates-checklist.md`: Stage 13 graphical update validation.
- `docs/snapshots-rollback-checklist.md`: Stage 14 snapshot and rollback validation.
- `docs/iso-creation-checklist.md`: Stage 15 ISO creation and boot validation.
- `docs/installer-checklist.md`: Stage 16 guided installer validation.
- `docs/design-checklist.md`: Stage 17 FlasterOS design validation.
- `docs/performance-checklist.md`: Stage 18 performance validation.
- `docs/hardware-support-checklist.md`: Stage 19 hardware support validation.
- `docs/game-compatibility-table.md`: Stage 20 game compatibility table.
- `docs/hoyoverse-compatibility.md`: explicit Hoyoverse compatibility status.
- `docs/security-checklist.md`: Stage 21 security validation.
- `docs/mvp-checklist.md`: Stage 22 MVP validation.
- `docs/beta-checklist.md`: Stage 23 beta validation.
- `docs/beta-user-guide.md`: beta tester installation, game, and log instructions.
- `docs/beta-bug-list.md`: beta bug tracking template and issue list.
- `docs/release-checklist.md`: Stage 24 release validation.
- `docs/download-page.md`: release download page draft.
- `docs/release-notes.md`: release changelog, known issues, and recovery notes.

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

The stable install image path is:

```text
out/FlasterOS.iso
```

Release builds also create a versioned ISO and checksum using `VERSION`:

```text
out/FlasterOS-0.1.0.iso
out/FlasterOS-0.1.0.iso.sha256
```

## Test The ISO

```bash
bash scripts/test-qemu.sh out/FlasterOS.iso
```

Expected result:

- The ISO boots.
- The `ard` live user logs into KDE Plasma automatically.
- NetworkManager is active.
- The Install FlasterOS desktop icon starts the guided installer.

## Install To Disk

From the live desktop, open **Install FlasterOS**.

The guided installer asks for language, target disk, username, password, and computer name. It is destructive and asks for confirmation before touching the selected disk.

The installed system uses a FAT32 EFI partition, a btrfs root partition, and a separate btrfs `/home` partition. The root partition keeps separate system subvolumes for games, logs, and snapshots. System rollback does not include personal files in `/home`.

The guided installer targets gaming storage, not tiny desktop tests. It requires at least a 256 GiB target disk, with 512 GiB recommended for testing Genshin Impact, Honkai: Star Rail, and Zenless Zone Zero together.

After install and reboot:

- systemd-boot starts the installed FlasterOS system.
- The Linux kernel starts from the installed root filesystem.
- systemd reaches the graphical target.
- KDE Plasma starts through SDDM.
- NetworkManager manages internet access.
- The created user can use `sudo`.
- The created user is the normal account for work, games, and launchers.

## User Model

Ard OS uses `root` only for administration. Daily work, games, launchers, browsers, and the desktop session run as the normal user created by the installer.

The default suggested installed user is `ard`, but the guided installer lets the user choose another name. That user has a home directory, a login shell, and `sudo` access through the `wheel` group.

Games must not be launched as root.

## Boot Chain

Ard OS is not ready until the full boot chain succeeds:

```text
BIOS/UEFI -> systemd-boot -> Linux kernel -> systemd -> SDDM login screen -> KDE Plasma desktop
```

The installer configures this chain by creating an EFI system partition, installing systemd-boot, writing a FlasterOS entry to `/boot/loader/entries/ard-os.conf`, using the root filesystem UUID and btrfs `@` subvolume in the kernel command line, and enabling `sddm.service`.

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

Important compatibility limit: FlasterOS can run some Windows games through Wine or Proton, but that does not prove Hoyoverse compatibility. Genshin Impact, Honkai: Star Rail, and Zenless Zone Zero may fail because of anti-cheat, launcher behavior, or Wine/Proton regressions. Do not claim Hoyoverse support until the specific game is tested on an installed system and recorded in `docs/hoyoverse-compatibility.md`.

Fresh installs do not guarantee Proton until Steam downloads a compatibility tool. Prepare or verify Proton with:

```bash
ard-prepare-proton
```

Plain Wine DirectX 9/10/11 games need DXVK inside the selected Wine prefix. For a FlasterOS game config, use:

```bash
ard-setup-wine-dxvk /games/GameName/config.json
```

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

## Gaming Mode

Stage 10 adds a separate login session:

```text
login manager -> gamescope session -> launcher -> game
```

SDDM shows `Ard Desktop Mode` for the normal KDE Plasma desktop and `Ard Gaming Mode` for the launcher-first session. Gaming Mode runs `ard-gaming-session`, which starts `gamescope -f -- ard-launcher`.

The launcher includes Exit Session, Reboot, and Shutdown buttons. Emergency exit shortcuts are `Ctrl+Alt+Backspace` and `Ctrl+Alt+B`.

## Settings Center

Stage 11 adds a graphical settings interface:

```bash
ard-settings-center
```

The Settings Center is available from the desktop and from the launcher. It covers Wi-Fi, Ethernet status, IP address, sound output and microphone selection, volume, sound test, display resolution, refresh rate, scaling, main monitor, performance mode, FPS limit, MangoHud, Gamemode, updates, logs, reboot, shutdown, and OS version.

Normal users should not need terminal commands for internet, sound, display, or gaming performance basics. The interface uses system tools such as NetworkManager, PipeWire/PulseAudio, xrandr, powerprofilesctl, pacman, journalctl, and systemctl, and shows visible errors when a required tool or permission is missing.

## Diagnostics

Stage 12 adds a system diagnostics tool:

```bash
ard-check-system
```

The launcher and Settings Center expose the same tool through **Check System**. Pressing **Create report** writes:

```text
~/ard-diagnostics/report.txt
```

The report covers OS and kernel version, CPU, GPU and driver, Vulkan, OpenGL, Wine, Proton, DXVK, VKD3D, network reachability, disk usage, prefix sizes, and recent game launch logs. Reports are bounded and redact common password, token, authorization, and cookie fields before saving.

## Updates

Stage 13 makes system updates a Settings Center workflow instead of a terminal workflow.

Open:

```bash
ard-settings-center
```

In the **System** tab, press **Check Updates** to review available updates before installing them. The update list shows package name, update area, current version, new version, approximate download size, and whether a reboot is expected. The check covers system packages, kernel, drivers, Wine, Proton or Steam-managed compatibility packages available through system packages, DXVK, VKD3D, launcher packages when packaged, and desktop theme packages.

Press **Install Updates** only after the list is visible. The Settings Center writes update output to:

```text
/var/log/flasteros/update.log
```

Driver, kernel, Wine/Proton, DXVK/VKD3D, Vulkan, and graphics stack updates are treated as reboot-risk updates because they can affect display stability and game compatibility. Stage 13 passes when update check, install, log creation, error handling, and post-reboot operation all work through the interface. Move to Stage 14 rollback work only after this path is reliable.

## Snapshots And Rollback

Stage 14 makes updates recoverable. New Ard OS installs use a btrfs root partition, a separate btrfs `/home` partition, and these root subvolumes:

```text
@           system root
@games      installed games and game data
@var_log    logs
@snapshots  system restore points
```

Before the Settings Center installs updates, it runs `ard-snapshot pre-update`. This creates a labeled system snapshot, saves matching boot files under `/boot/ard-snapshots/`, updates the bootloader's **FlasterOS Previous Version** entry, keeps a **FlasterOS Recovery** entry, and prunes old pre-update snapshots after the newest five.

If an update breaks the desktop, graphics driver, Wine/Proton, DXVK/VKD3D, or the launcher, select **FlasterOS Previous Version** in the bootloader. After confirming the previous snapshot works, make it permanent with:

```bash
sudo ard-snapshot rollback latest
```

The broken root is preserved as `@broken-YYYYMMDD-HHMMSS` for inspection. Move to Stage 15 only after a deliberately failed update can be recovered by booting a previous snapshot.

## ISO Creation

Stage 15 turns the profile into an installable FlasterOS ISO:

```bash
bash scripts/build-iso.sh
```

The archiso profile includes the package list, NetworkManager, PipeWire, KDE graphical sessions, launcher desktop entries, Settings Center, diagnostics, update/snapshot tooling, VM guest packages for QEMU and VirtualBox, and baseline KDE user settings. The profile metadata produces FlasterOS-labeled archiso output, and the build script copies the latest dated artifact to:

```text
out/FlasterOS.iso
```

Validate the ISO in QEMU with:

```bash
bash scripts/test-qemu.sh out/FlasterOS.iso
```

Stage 15 passes when the ISO boots on UEFI, starts the live graphical system, reaches the internet, has working graphics/audio basics, shows the launcher and Settings Center, and does not contain personal passwords.

## Installer

Stage 16 makes installation a guided desktop workflow. The live desktop contains **Install FlasterOS**, which opens a graphical installer with English and Russian language choices, disk selection with a destructive warning, user creation, and a final confirmation before erasing the disk.

The installer creates:

```text
EFI     FAT32, mounted at /boot
/       btrfs root partition
/home   btrfs home partition
```

After copying the system, the installer creates the selected user, locks the root account, installs `systemd-boot` to the new EFI partition, and writes the default FlasterOS boot entry. Stage 16 passes when a clean disk install reboots into the installed system without using terminal commands.

## Design

Stage 17 makes FlasterOS visually distinct from a default Arch/KDE install. The profile includes a FlasterOS logo, wallpaper, application icon, SDDM login theme, Plymouth boot screen, dark KDE defaults, and matching launcher and Settings Center headers.

The default visual direction is restrained: dark neutral surfaces, teal and blue accents, Breeze-compatible controls/icons/cursor, Noto Sans fonts, and no heavy animations. Stage 17 passes when boot, login, desktop wallpaper, launcher, and settings all show one consistent FlasterOS identity.

## Performance

Stage 18 keeps system overhead low while preserving the services that make the gaming system usable. VM guest services are enabled only for matching virtualized installs, while bare-metal installs keep them disabled. NetworkManager, SDDM, PipeWire, WirePlumber, updates, snapshots, graphics drivers, and power profile controls must remain intact.

Game launches use GameMode automatically by default when `gamemoderun` is installed. The Settings Center can still turn this off through `~/.config/ard-os/performance.json`.

The profile installs `zram-generator` and configures `/etc/systemd/zram-generator.conf` so zram swap is created at boot. Launcher and `ard-run-game` starts keep DXVK and Mesa shader caches enabled to reduce repeated stutter.

Validate Stage 18 with:

```bash
systemctl --type=service --state=running
gamemoded -t
zramctl
swapon --show
ard-run-game /games/GameName/config.json
```

Do not move to Stage 19 until games start quickly, background load is low, FPS is stable, frametime is smooth, and sound, network, updates, rollback, and graphics still work.

## Hardware Support

Stage 19 proves that FlasterOS works beyond one development PC. Test at least NVIDIA, AMD, and Intel GPUs, plus a desktop PC, a laptop, and a laptop with hybrid graphics.

The profile includes firmware, NetworkManager, PipeWire/WirePlumber, SOF firmware, Bluetooth support through BlueZ and Bluedevil, and Steam device rules for common controller access. Bluetooth is enabled by default because wireless controllers and headsets are part of the target gaming hardware.

Validate each machine with:

```bash
lspci -nnk | grep -EA4 'VGA|3D|Display'
glxinfo -B
vulkaninfo --summary
nmcli device status
bluetoothctl list
wpctl status
ard-check-system --report
```

Stage 19 passes when the OS boots on several hardware configurations, network works, sound and microphone work, graphics pass Vulkan/OpenGL checks, devices are detected, and games start from the launcher.

## Security

Stage 21 protects the system from accidental damage during normal use. Games and the launcher run as the normal user, game files stay under `/games`, and system folders such as `/bin`, `/usr`, `/etc`, and `/boot` remain root-owned.

The launcher and `ard-run-game` refuse root game launches and block game configs, executables, and Wine prefixes outside `/games`. Update installation checks that pacman requires package signatures and that only the expected base repositories are enabled before running `pacman -Syu`.

Launch logs and diagnostics redact common password, token, cookie, authorization, API key, access key, secret key, SSH key, and private key patterns before support reports are sent.

Validate Stage 21 with:

```bash
test "$(id -u)" -ne 0
sudo ard-run-game /games/GameName/config.json
grep -E '^(SigLevel|\[core\]|\[extra\]|\[multilib\])' /etc/pacman.conf
ard-check-system --report
```

Do not move to Stage 22 until normal play, launcher use, update checks, logs, network, sound, and display setup do not require a root desktop session.

## MVP

Stage 22 is the first product gate. It does not add polish; it proves the core path works end to end:

```text
USB install -> first boot -> launcher -> Windows game -> error report -> update -> reboot
```

The MVP must boot, install, open the interface, connect to the internet, play sound, detect the GPU, start the launcher, run at least one Windows game, create an error report, and update through the Settings Center.

Do not block MVP on an app store, complex design, custom browser, custom file manager, many games, complex animations, or advanced library management. Move to beta only when another person can install FlasterOS and launch a game without help.

## Beta

Stage 23 is the first external test version. It is for finding bugs on other hardware, not for pretending the system is final.

The launcher, Settings Center, and Diagnostics show:

```text
Beta test version. Errors are possible.
```

Beta testers use `docs/beta-user-guide.md` to download the ISO, write it to a USB drive, install, start a game, and send logs. The main report path is:

```text
~/ard-diagnostics/report.txt
```

Beta bugs are tracked in `docs/beta-bug-list.md` with user hardware, what failed, error logs, fix status, and retest result. Move to release only when critical errors are fixed.

## Release

Stage 24 is the normal distribution gate. A release must have a final ISO name, version, checksum, installation instruction, changelog, download page, system requirements, known issues, supported games list, updates, and rollback.

The release build path is:

```bash
bash scripts/build-iso.sh
sha256sum -c out/FlasterOS-0.1.0.iso.sha256
```

Release materials:

- `VERSION`
- `docs/release-checklist.md`
- `docs/download-page.md`
- `docs/release-notes.md`
- `docs/game-compatibility-table.md`

Main release checkpoint:

```text
ISO -> installation -> system launch -> launcher launch -> one game launch -> log collection -> reboot -> everything still works
```

Do not move to advanced design, an app store, or complex features until this checkpoint works.

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
- Proton preparation and Wine-prefix DXVK setup helpers
- structured game directories, per-game configs, prefixes, and logs
- graphical game launcher
- per-game launch profiles
- Gaming Mode login session
- graphical Settings Center for network, sound, display, performance, and system actions
- diagnostics tool with safe report generation for graphics, Wine/Proton, DXVK/VKD3D, network, disk, and launch logs
- graphical update checks and installs with `/var/log/flasteros/update.log`
- btrfs system snapshots before updates and bootloader rollback entries
- installable FlasterOS archiso output at `out/FlasterOS.iso`
- guided graphical installer with English and Russian language choices
- FlasterOS logo, wallpaper, login theme, boot splash, app icon, and dark theme defaults
- performance defaults for GameMode, zram, shader cache, and frametime validation
- hardware support coverage for Bluetooth and Steam controller device rules
- security checks for normal-user game launches, trusted updates, and redacted logs
- MVP validation path for USB install, launcher, Windows game, report, update, and reboot
- beta warning, tester guide, log collection path, and bug tracking template
- release artifacts for versioned ISO, checksum, download page, release notes, and compatibility table
- Firefox
- Installer backend for UEFI systems

Deferred:

- GPU vendor tuning
- Secure Boot signing
- custom package repository
