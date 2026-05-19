# Design Checklist

Use this checklist for Stage 17 validation.

Stage 17 makes the system look like FlasterOS instead of a plain Arch/KDE install. The style should be consistent, readable, and light enough for low-end gaming PCs.

## Name

The product name is:

```text
FlasterOS
```

Use FlasterOS in visible user-facing surfaces. Keep Ard names only for internal command compatibility where renaming would break scripts.

## Logo Placement

The FlasterOS logo or wordmark must appear in:

- boot screen
- bootloader entries
- login screen
- Settings Center
- launcher
- wallpapers
- desktop application icons where practical

Do not leave standard Arch logos on primary user-facing screens.

## Theme

The default theme uses:

- dark neutral background
- teal and blue accents
- Breeze Dark base widgets for stability
- Breeze cursor and icon compatibility
- Noto Sans readable UI fonts
- FlasterOS wallpaper from `/usr/share/flasteros/branding`

Validation:

- buttons and text remain readable
- accent colors are consistent
- windows do not rely on heavy animation
- launcher and Settings Center use the same product name
- login and desktop wallpaper match the brand

## Boot Screen

The installed system must boot with `quiet splash` and Plymouth using the FlasterOS theme.

Validation:

- normal boot shows a branded screen
- kernel and systemd technical lines are hidden during normal boot
- boot failures can still be debugged by editing the boot entry

## Stage 17 Result

Stage 17 passes when:

- the PC turns on
- FlasterOS is visible during boot
- the FlasterOS login screen opens
- the FlasterOS launcher opens
- Settings Center shows FlasterOS identity
- wallpaper, colors, icon, boot screen, login screen, and apps feel like one product

## Move To Stage 18

Move to Stage 18 when the system visually looks like a separate product, not a default Arch/KDE desktop.
