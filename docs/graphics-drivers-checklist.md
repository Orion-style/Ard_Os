# Graphics And Drivers Checklist

Use this checklist for Stage 5 validation.

Gaming work starts only after the graphics stack is known and working. The system must be able to use the GPU, Vulkan, OpenGL, correct screen resolution, correct monitor refresh rate, and hardware acceleration.

## 5.1 Identify The Graphics Card

First identify the installed GPU vendor. Driver choices depend on whether the machine uses NVIDIA, AMD, Intel, or hybrid graphics.

Required command:

```bash
lspci -nnk | grep -EA3 'VGA|3D|Display'
```

Optional detail commands, if available:

```bash
inxi -Gxx
lsmod | grep -E 'nvidia|amdgpu|i915|xe|nouveau'
```

Record this result before installing or tuning graphics drivers:

```text
GPU vendor:
GPU model:
Kernel driver in use:
Hybrid graphics: yes/no
Display server: Wayland/X11
```

Vendor guide:

- NVIDIA: look for `NVIDIA Corporation`; kernel driver is usually `nvidia` or `nouveau`.
- AMD: look for `Advanced Micro Devices, Inc. [AMD/ATI]`; kernel driver should usually be `amdgpu`.
- Intel: look for `Intel Corporation`; kernel driver is usually `i915` or `xe`.

Do not continue to Vulkan, OpenGL, refresh-rate, or gaming checks until the GPU vendor and active kernel driver are known.

## 5.2 Install Drivers

Install driver packages only after the GPU vendor is known.

AMD package set:

```bash
sudo pacman -Syu --needed mesa mesa-utils vulkan-icd-loader vulkan-radeon vulkan-tools
```

Intel package set:

```bash
sudo pacman -Syu --needed mesa mesa-utils vulkan-icd-loader vulkan-intel vulkan-tools
```

NVIDIA package set for current supported NVIDIA hardware:

```bash
sudo pacman -Syu --needed nvidia-open nvidia-utils nvidia-settings vulkan-icd-loader vulkan-tools mesa-utils
```

The installed system also includes a helper:

```bash
sudo ard-install-gpu-drivers --vendor amd
sudo ard-install-gpu-drivers --vendor intel
sudo ard-install-gpu-drivers --vendor nvidia
```

Notes:

- `mesa` provides open-source OpenGL drivers.
- `vulkan-radeon` provides Vulkan for AMD GPUs.
- `vulkan-intel` provides Vulkan for Intel GPUs.
- `nvidia-utils` provides NVIDIA user-space OpenGL and Vulkan support.
- `nvidia-settings` provides the NVIDIA configuration tool.
- Reboot after installing NVIDIA drivers before validating the graphics stack.
- Older NVIDIA GPUs may require a different legacy driver package; identify the exact GPU model before installing.

Driver validation commands:

```bash
lspci -nnk | grep -EA3 'VGA|3D|Display'
glxinfo -B
vulkaninfo --summary
```

## 5.3 Check Vulkan

Vulkan is required before Proton, DXVK, or VKD3D work makes sense.

The Windows game graphics path is:

```text
Windows game -> DirectX -> DXVK/VKD3D -> Vulkan -> graphics card
```

If Vulkan does not work on the real GPU, most Windows games through Proton will not work properly.

Required command:

```bash
vulkaninfo --summary
```

Pass criteria:

- `vulkaninfo --summary` completes without loader or ICD errors.
- The reported GPU matches the expected NVIDIA, AMD, or Intel device.
- The reported driver is not a software renderer such as `llvmpipe` unless testing inside a VM.
- Vulkan still works after reboot.

Useful troubleshooting commands:

```bash
ls /usr/share/vulkan/icd.d/
pacman -Qs 'vulkan|nvidia|mesa'
lspci -nnk | grep -EA3 'VGA|3D|Display'
```

Vendor-specific Vulkan packages:

- AMD: `vulkan-radeon`
- Intel: `vulkan-intel`
- NVIDIA: `nvidia-utils`

Do not start Proton, Wine, DXVK, VKD3D, or launcher work until this Vulkan check passes.

## 5.4 Check OpenGL

OpenGL is required for some programs, older games, desktop interfaces, and graphics tests.

Required command:

```bash
glxinfo -B
```

Pass criteria:

- `glxinfo -B` completes without errors.
- `direct rendering` is `Yes`.
- `OpenGL renderer string` shows the real NVIDIA, AMD, or Intel GPU.
- The renderer is not a software renderer such as `llvmpipe` unless testing inside a VM.
- OpenGL still works after reboot.

Useful focused commands:

```bash
glxinfo -B | grep -E 'direct rendering|OpenGL vendor|OpenGL renderer|OpenGL core profile version'
glxgears
```

Vendor-specific OpenGL packages:

- AMD/Intel: `mesa`
- NVIDIA: `nvidia-utils`

Do not continue graphics validation if OpenGL reports the wrong GPU, software rendering, or missing direct rendering.

## 5.5 Check The Display

The display must prove that the system is using the graphics card correctly.

Check:

- Correct screen resolution.
- Correct monitor refresh rate.
- Multiple monitors, if available.
- Screen wakes correctly after sleep mode.
- No black screen after reboot.
- 3D applications start.

Wayland/KDE commands:

```bash
kscreen-doctor -o
loginctl show-session "$XDG_SESSION_ID" -p Type -p Desktop
```

X11 commands:

```bash
xrandr --query
glxgears
```

Sleep and reboot checks:

```bash
systemctl suspend
systemctl reboot
```

Expected result:

```text
GPU is detected.
Vulkan works.
OpenGL works.
Screen uses the correct resolution.
Screen uses the correct refresh rate.
Multiple monitors work if connected.
System wakes from sleep with the screen working.
No black screen appears after reboot.
3D applications start.
```

Pay close attention to:

- NVIDIA with Wayland.
- Laptops with two GPUs.
- Hybrid graphics.
- Old graphics cards.
- Wrong driver version.

If this stage is unstable, games will also be unstable later.

Move to Stage 6 only when Vulkan and OpenGL work without errors and the display remains stable after sleep and reboot.

## Stage 5 Exit Criteria

Move forward only when:

- GPU vendor and model are recorded.
- Correct kernel driver is active.
- Desktop uses the expected GPU.
- OpenGL works on the real GPU.
- Vulkan works on the real GPU.
- Screen resolution is correct.
- Monitor refresh rate is correct.
- Multiple monitors work if available.
- Screen works after sleep.
- No black screen appears after reboot.
- 3D applications start.
- Hardware acceleration works.
- The same checks still pass after reboot.
