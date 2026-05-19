# Updates Checklist

Use this checklist for Stage 13 validation.

Normal users should not update Ard OS manually through a terminal. Updates must be checked, reviewed, installed, logged, and rebooted from the graphical Settings Center.

Command:

```bash
ard-settings-center
```

Open the **System** tab and use the **Updates** panel.

## 13.1 Check For Updates

Press **Check Updates**.

The Settings Center must check:

- System packages.
- Kernel.
- Drivers.
- Wine.
- Proton or Steam-managed compatibility packages available from system packages.
- DXVK packages when present.
- VKD3D packages.
- Launcher packages when Ard OS launcher updates are packaged.
- Theme and desktop packages.

Validation:

- The check runs without requiring a terminal.
- Missing update tooling is shown as a clear interface error.
- No packages are installed during the check step.

## 13.2 Show Update List

The user must see:

- Package name.
- Update area.
- Current version.
- New version.
- Approximate download size when available.
- Whether a reboot is expected.

Validation:

- Kernel, firmware, graphics, Wine, Proton, DXVK, VKD3D, launcher, and theme-related packages are categorized.
- Driver, kernel, graphics stack, Wine, Proton, and desktop stack updates are marked as reboot-risk updates.
- If no updates are available, the interface says the system is up to date.

## 13.3 Install Updates

Press **Install Updates** after the update list is visible.

Process:

- Create `/var/log/flasteros`.
- Append an update session header to `/var/log/flasteros/update.log`.
- Start the system update through graphical authorization when available.
- Install packages.
- Append pacman output and the exit code to the log.
- Show errors in the interface if the update fails.
- Offer reboot when the checked update set requires it.

Validation:

- The update starts from the interface.
- Authentication is handled by `pkexec` when available, otherwise `sudo`.
- The update does not silently hide package manager errors.
- After success, pressing reboot restarts the system.

## 13.4 Update Log

After updating, this file must exist:

```text
/var/log/flasteros/update.log
```

Validation:

- The log contains the update start time.
- The log contains package manager output.
- The log contains the final exit code.

## Stage 13 Result

Stage 13 passes when:

- The Settings Center opens.
- The user presses **Check Updates**.
- The update list appears with versions, size, and reboot information.
- The user presses **Install Updates**.
- The system updates without opening a terminal.
- `/var/log/flasteros/update.log` is created.
- After reboot, the desktop, graphics, launcher, Wine/Proton path, DXVK/VKD3D path, and Settings Center still work.

Pay attention to:

- Updates can break graphics drivers.
- Updates can break Wine or Proton.
- Updates can break DXVK, VKD3D, Vulkan, or the desktop graphics stack.

Move to Stage 14 only when updates work through the interface.
