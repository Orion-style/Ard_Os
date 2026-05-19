# Diagnostics Checklist

Use this checklist for Stage 12 validation.

Diagnostics are used when a game does not start. The user should press **Check System** or **Create report** and get a clear report that explains where the problem is likely located.

Command:

```bash
ard-check-system
```

CLI report generation:

```bash
ard-check-system --report
```

The report is saved to:

```text
~/ard-diagnostics/report.txt
```

## 12.1 Graphics Check

The report must show:

- Graphics card detected through `lspci`.
- Kernel driver in use.
- Vulkan result from `vulkaninfo --summary`.
- OpenGL result from `glxinfo -B`.
- PASS or FAIL status for GPU detection, Vulkan, and OpenGL.

## 12.2 Wine And Proton Check

The report must show:

- Wine installed and version.
- Proton executable discovered from Steam compatibility paths or `PATH`.
- Temporary Wine prefix creation result.
- Test Windows command start result through `wine cmd /c ver`.

The temporary prefix must be created outside the user's game prefixes and removed after the check.

## 12.3 DXVK And VKD3D Check

The report must show:

- DXVK availability.
- VKD3D package availability.
- Whether the runtime can see Vulkan.

## 12.4 Network Check

The report must show:

- Internet reachability.
- DNS resolution.
- Update server reachability.

## 12.5 Disk Space Check

The report must show:

- Free space.
- `/games` size.
- `/var/log/ard-os` size.
- Per-game Wine prefix sizes.

## 12.6 Report Generation

The report must include:

- OS version.
- Kernel version.
- CPU.
- GPU.
- Driver.
- Vulkan version or Vulkan failure.
- Wine and Proton version/status.
- Last launch error.
- Recent game logs.

## Stage 12 Result

Stage 12 passes when:

- Pressing **Check System** opens diagnostics and runs checks.
- Pressing **Create report** creates `~/ard-diagnostics/report.txt`.
- The report makes graphics, Wine/Proton, DXVK/VKD3D, network, disk, and last launch failures understandable.
- The report can be sent to a developer.

Pay attention to:

- Do not save passwords.
- Do not save tokens.
- Do not save user personal files.
- Keep command output and logs bounded so the report does not become huge.

Move to Stage 13 when the report actually helps identify errors.
