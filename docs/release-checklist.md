# Release Checklist

Use this checklist for Stage 24 validation.

Release is the version that can be distributed normally. It must be stable, installable, understandable for the user, updateable without reinstalling, and recoverable if an update breaks the system.

## 24.1 Prepare The ISO

Required release artifacts:

- Final ISO name.
- Version.
- SHA256 checksum.
- Source archive without `.git`.
- Installation instruction.
- Changelog.

Version source:

```text
VERSION
```

Build:

```bash
bash scripts/build-iso.sh
```

Expected output:

```text
out/FlasterOS.iso
out/FlasterOS-0.1.0.iso
out/FlasterOS-0.1.0.iso.sha256
out/FlasterOS-source-0.1.0.tar.gz
```

Use `FLASTEROS_VERSION=... bash scripts/build-iso.sh` only when building a specific release candidate outside the checked-in `VERSION`.

Validation:

```bash
sha256sum -c out/FlasterOS-0.1.0.iso.sha256
bash scripts/archive-source.sh
```

The release must include:

- `docs/beta-user-guide.md` or a final installation guide.
- `docs/release-notes.md`.
- `docs/download-page.md`.
- `docs/game-compatibility-table.md`.
- `docs/hoyoverse-compatibility.md`.

Do not send project archives containing `.git`. Use `scripts/archive-source.sh` for source snapshots.

## 24.2 Prepare The Download Page

The download page should include:

- Download ISO.
- SHA256 checksum.
- Installation guide.
- System requirements.
- Known issues.
- Supported games list.
- Recovery note.
- Beta/release status.

Draft page:

```text
docs/download-page.md
```

Do not publish a release page that omits known critical issues.

## 24.3 Prepare Updates

Users must receive updates without reinstalling the OS.

Validation:

```bash
ard-settings-center
```

In Settings Center:

1. Open **System**.
2. Press **Check Updates**.
3. Review package list.
4. Press **Install Updates**.
5. Reboot if requested.

Expected result:

- Updates use trusted pacman repositories.
- A pre-update snapshot is created.
- `/var/log/flasteros/update.log` is written.
- After reboot, desktop, launcher, network, sound, graphics, and the tested game still work.

## 24.4 Prepare Recovery

Rollback must exist if an update breaks the system.

Required bootloader entries:

- **FlasterOS**
- **FlasterOS Previous Version**
- **FlasterOS Recovery**

Validation:

```bash
sudo ard-snapshot pre-update
bootctl list
```

Recovery acceptance test:

1. Create a pre-update snapshot.
2. Confirm **FlasterOS Previous Version** appears in the boot menu.
3. Boot the previous version.
4. Confirm desktop, launcher, graphics, and game path still work.
5. If needed, run `sudo ard-snapshot rollback latest`.

## Main Control Sequence

Move forward only when the previous stage actually works:

- Stage 4: The system boots and works.
- Stage 5: GPU and Vulkan work.
- Stage 6: Windows games start through Wine or Proton.
- Stage 7: Games are separated into folders and prefixes.
- Stage 8: Launcher starts games.
- Stage 9: Each game has a profile.
- Stage 10: Gaming Mode exists.
- Stage 11: Settings are available without terminal.
- Stage 12: Diagnostics exist.
- Stage 13: Updates exist.
- Stage 14: Rollback exists.
- Stage 15: ISO exists.
- Stage 16: Installer exists.
- Stage 17: Custom design exists.
- Stage 18: Optimization exists.
- Stage 19: Tests on different hardware exist.
- Stage 20: Game compatibility table exists.
- Stage 21: Permissions and security are correct.
- Stage 22: MVP exists.
- Stage 23: Beta test exists.
- Stage 24: Release exists.

Most important checkpoint:

```text
ISO -> installation -> system launch -> launcher launch -> one game launch -> log collection -> reboot -> everything still works
```

Until this works, do not move to advanced design, an app store, or complex features.

## Stage 24 Result

Stage 24 passes when:

- A person downloads the ISO.
- They verify the checksum.
- They install the OS.
- They connect to the internet.
- They open the launcher.
- They start a game.
- They receive updates without reinstalling.
- They can roll back after an error.

Pay attention to:

- Stability.
- Clear installation.
- Updates.
- Rollback.
- Game compatibility.
- Security.

Move beyond release only after critical errors are fixed and the release checkpoint passes on real hardware.
