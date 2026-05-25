# Security Checklist

Use this checklist for Stage 21 validation.

The system should protect itself from accidental damage. Normal gaming, launching, browsing, network setup, sound setup, and update checks should not require a root desktop session.

## 21.1 Run Games As A Normal User

Rules:

- Do not run games as root.
- Do not run the launcher as root.
- Do not store games in `/bin`, `/usr`, `/etc`, `/boot`, `/opt`, or other system folders.
- Store game executables, prefixes, configs, and logs under `/games`.

Implementation:

- `ard-run-game` exits if `id -u` is `0`.
- `ard-launcher` exits if started as root.
- Launcher validation blocks configs, executables, and Wine prefixes outside `/games`.
- `ard-run-game` also blocks configs, executables, and Wine prefixes outside `/games`.

Validation:

```bash
test "$(id -u)" -ne 0
ard-launcher
ard-run-game /games/GameName/config.json
sudo ard-run-game /games/GameName/config.json
```

The `sudo ard-run-game ...` command must fail with a clear "Do not run games as root" message.

## 21.2 Protect System Folders

System folders must remain root-owned and not writable by the normal user:

```text
/bin
/usr
/etc
/boot
```

Validation:

```bash
for path in /bin /usr /etc /boot; do
  stat -c '%U %G %A %n' "$path"
  test ! -w "$path"
done
```

The normal user can use `/games` for game data and `$HOME` for personal files. The user should not need write access to system folders for normal play.

## 21.3 Verify Updates

Updates must come from trusted package sources.

Required pacman policy:

```text
SigLevel = Required DatabaseOptional
```

Allowed base repositories:

- `core`
- `extra`
- `multilib`

The Settings Center refuses to install updates if pacman signature verification is not required or if an unknown repository is enabled. Update installation still requires administrator authorization and creates a pre-update snapshot first.

Validation:

```bash
grep -E '^(SigLevel|\\[core\\]|\\[extra\\]|\\[multilib\\])' /etc/pacman.conf
ard-settings-center
```

Open **System**, press **Check Updates**, then press **Install Updates** only after the update list is visible.

## 21.4 Do Not Store Secrets In Logs

Logs must be safe to send for support.

Do not store:

- Passwords.
- Tokens.
- Authorization headers.
- Cookies.
- API keys.
- Private keys.
- Unrelated personal file contents.

Implementation:

- Diagnostics reports redact common password, token, cookie, authorization, API key, access key, secret key, SSH key, and private key patterns.
- Diagnostics replace the home path with `$HOME`.
- Diagnostics include a security section for pacman trust settings, system folder permissions, and `/games`.
- Launcher and `ard-run-game` redact common secret patterns from game launch output before writing launch logs.
- Diagnostics read only bounded system command output and bounded game launch logs.

Validation:

```bash
ard-check-system --report
grep -Ei 'password|token|authorization|cookie|private_key|secret_key' ~/ard-diagnostics/report.txt || true
grep -Ei 'password|token|authorization|cookie|private_key|secret_key' /games/GameName/logs/last-launch.log || true
```

Any remaining match must be reviewed before sending the log.

## Stage 21 Result

Stage 21 passes when:

- User can play games without root.
- Launcher and game runner refuse root game launches.
- Games, prefixes, configs, and logs stay under `/games`.
- The normal user cannot accidentally write to `/bin`, `/usr`, `/etc`, or `/boot`.
- Updates use required package signatures and known repositories.
- Logs and diagnostic reports redact common secrets.

Pay attention to:

- Permissions.
- Sudo usage.
- Logs.
- Updates.
- Game isolation.

Move to Stage 22 when the system does not require root for normal use.
