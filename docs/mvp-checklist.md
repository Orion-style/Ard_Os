# MVP Checklist

Use this checklist for Stage 22 validation.

MVP means minimum viable product. It does not have to be beautiful or perfect. It must perform the main task:

```text
installation -> launch -> game -> error log
```

Do not add non-essential features before this path works for another person.

## 22.1 Build And Write The ISO

Build:

```bash
bash scripts/build-iso.sh
```

Expected output:

```text
out/FlasterOS.iso
```

Write the ISO to a USB drive with a trusted imaging tool. Verify the target drive before writing.

Validation:

- ISO file exists.
- ISO boots from USB on a real PC.
- Live desktop opens.
- Installer icon is visible.

## 22.2 Install On A PC

From the live desktop:

1. Open **Install FlasterOS**.
2. Choose language.
3. Select the target disk.
4. Confirm the destructive warning.
5. Create the user.
6. Install.
7. Reboot without the USB drive.

Validation:

- Installed system reaches the bootloader.
- Installed system reaches SDDM.
- Created user can log in.
- Desktop opens after login.
- The same boot still works after another reboot.

## 22.3 Open The Interface

The installed system must expose the main user interfaces without terminal commands:

- Launcher.
- Settings Center.
- Diagnostics.

Validation:

```bash
ard-launcher
ard-settings-center
ard-check-system --report
```

Manual validation:

- Launcher opens.
- Settings Center opens.
- Diagnostics can create `~/ard-diagnostics/report.txt`.

## 22.4 Check Basic System Function

Required MVP checks:

- Connect to internet.
- Play sound.
- Detect GPU.
- Confirm Vulkan or record why it fails.
- Confirm OpenGL or record why it fails.

Validation:

```bash
nmcli device status
ping -c 3 archlinux.org
wpctl status
speaker-test -c 2 -t wav
lspci -nnk | grep -EA4 'VGA|3D|Display'
glxinfo -B
vulkaninfo --summary
```

If a command fails, create a diagnostics report before changing anything.

## 22.5 Run One Windows Game

Minimum game requirement:

- One Windows game or simple Windows test program starts from the launcher.
- It runs as the normal user.
- It uses a game folder under `/games`.
- It writes a launch log.

Example setup:

```bash
ard-create-game --id MVPGame --name "MVP Game" --exe /games/MVPGame/game.exe
ard-launcher
```

Validation:

- Game appears in the launcher.
- Pressing Play starts the game.
- Closing the game returns to the launcher.
- `/games/MVPGame/logs/last-launch.log` exists.

## 22.6 Create An Error Report

The MVP must help debug failures.

Validation:

```bash
ard-check-system --report
test -f ~/ard-diagnostics/report.txt
```

The report must include:

- OS and kernel.
- CPU and GPU.
- Vulkan and OpenGL results.
- Wine and Proton status.
- DXVK and VKD3D status.
- Network status.
- Disk and `/games` status.
- Recent game launch logs.
- Security checks.

The report must redact common secrets before it is sent.

## 22.7 Update

Updates must work through the graphical Settings Center.

Validation:

1. Open `ard-settings-center`.
2. Open **System**.
3. Press **Check Updates**.
4. Review the update list.
5. Press **Install Updates**.
6. Reboot if requested.

Expected result:

- Update list is visible before install.
- A pre-update snapshot is created.
- `/var/log/flasteros/update.log` is written.
- After reboot, desktop, launcher, internet, sound, graphics, and the tested game still work.

## MVP Result

Stage 22 passes when:

- ISO was written to a USB drive.
- OS installed on a PC.
- Installed system booted.
- Launcher opened.
- Internet worked.
- Sound worked.
- GPU was detected.
- At least one Windows game started from the launcher.
- An error report was created.
- Updates worked.
- After reboot, the system still opened and the launcher still worked.

## Not Needed Yet

Do not block MVP on:

- App store.
- Complex design.
- Custom browser.
- Custom file manager.
- Many games.
- Complex animations.
- Advanced game library management.
- Large hardware certification matrix.

## Move To Beta

Move to beta when another person can install FlasterOS and launch a game without your help.
