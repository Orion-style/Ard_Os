# Beta Checklist

Use this checklist for Stage 23 validation.

Beta is a test version for other people. The goal is to find bugs on hardware that is not the developer's own PC.

## 23.1 Add A Warning

Users must see that this is not the final release.

Required warning:

```text
Beta test version. Errors are possible.
```

The warning appears in:

- Launcher.
- Settings Center.
- Diagnostics.

Validation:

- Boot the installed system.
- Open the launcher.
- Open Settings Center.
- Open Diagnostics.
- Confirm the beta warning is visible.

Do not describe beta builds as final, stable, production, or release-ready.

## 23.2 Add Log Collection

The user must be able to send a useful report without manually collecting many files.

Primary report command:

```bash
ard-check-system --report
```

Graphical path:

```text
Launcher -> Check System -> Create report
```

Report path:

```text
~/ard-diagnostics/report.txt
```

Ask beta users to send:

- `~/ard-diagnostics/report.txt`
- `/games/GameName/logs/last-launch.log` if a specific game failed
- `/var/log/flasteros/update.log` if update failed
- hardware model
- GPU model
- what they clicked before the problem
- whether the issue happens after reboot

Validation:

```bash
ard-check-system --report
test -f ~/ard-diagnostics/report.txt
```

Do not fix bugs blindly. Every beta bug should have a hardware description and a relevant log or report.

## 23.3 Write Instructions

Beta testers need a short instruction that explains:

- How to download the ISO.
- How to write it to a USB drive.
- How to install the OS.
- How to start a game.
- How to send a log.

Instruction file:

```text
docs/beta-user-guide.md
```

Validation:

- Give the guide to a tester.
- Do not explain extra steps verbally.
- Confirm they can install and start a game using only the guide.

## 23.4 Keep A Bug List

Keep beta reports in:

```text
docs/beta-bug-list.md
```

Each bug entry must record:

- Bug ID.
- Date.
- Status.
- User hardware.
- GPU.
- Network adapter if relevant.
- What does not work.
- Steps to reproduce.
- Error log/report path.
- Fix status.
- Retest result.

Status values:

- `new`
- `needs-info`
- `confirmed`
- `fixed`
- `wont-fix`

## Stage 23 Result

Stage 23 passes when:

- Several people installed the OS.
- You received bug reports with logs.
- Major problems were fixed.
- The system became more stable on different hardware.

Pay attention to:

- Do not pretend beta is the final version.
- Collect specific logs.
- Do not fix bugs blindly.
- Test on different hardware.
- Track fix and retest status.

Move to release when critical errors are fixed.
