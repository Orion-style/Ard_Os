# Hardware Support Checklist

Use this checklist for Stage 19 validation.

Ard OS must work on more than one development PC. This stage proves that boot, graphics, network, sound, input devices, and games work across common gaming hardware.

## 19.1 Test Different GPUs

Minimum GPU coverage:

- NVIDIA.
- AMD.
- Intel.

For each GPU, record:

```text
Machine:
GPU vendor:
GPU model:
Kernel driver:
Display server: Wayland/X11
Vulkan result:
OpenGL result:
Game tested:
Result:
```

Validation commands:

```bash
lspci -nnk | grep -EA4 'VGA|3D|Display'
glxinfo -B
vulkaninfo --summary
loginctl show-session "$XDG_SESSION_ID" -p Type -p Desktop
```

Expected result:

- GPU is detected.
- Correct kernel driver is active.
- Vulkan works on the real GPU.
- OpenGL works on the real GPU.
- A test game starts.

Pay special attention to NVIDIA on Wayland. If NVIDIA Wayland is unstable on a machine, validate the X11-compatible Plasma session before marking that machine as supported.

## 19.2 Test Different PC Types

Minimum machine coverage:

- Desktop PC.
- Laptop.
- Laptop with hybrid graphics.

For laptops, also check:

- Built-in display.
- External monitor.
- Touchpad.
- Keyboard brightness keys if present.
- Suspend and resume.
- Sound output and microphone after resume.

For hybrid graphics, record which GPU runs the desktop and which GPU runs the game. Do not assume the discrete GPU is used until Vulkan/OpenGL and MangoHud confirm it.

Validation:

```bash
systemctl suspend
lspci -nnk | grep -EA4 'VGA|3D|Display'
vulkaninfo --summary
mangohud glxgears
```

## 19.3 Test Devices

Check every device category on each test machine where that hardware exists:

- Wi-Fi.
- Ethernet.
- Bluetooth.
- Sound output.
- Microphone.
- Gamepad.
- Mouse.
- Keyboard.
- Monitor.

Support packages included in the profile:

- `linux-firmware` for broad firmware coverage.
- `NetworkManager`, `iwd`, and Plasma NetworkManager for network setup.
- `bluez`, `bluez-utils`, and `bluedevil` for Bluetooth.
- `pipewire`, `wireplumber`, and `sof-firmware` for audio.
- `pciutils` and `usbutils` for hardware inspection.
- `steam-devices` for Steam Input and SteamVR device rules.

Validation commands:

```bash
nmcli device status
bluetoothctl list
wpctl status
arecord -l
lsusb
ls /dev/input
ard-check-system --report
```

Manual validation:

- Connect to Wi-Fi.
- Connect Ethernet.
- Pair a Bluetooth gamepad or headset.
- Play audio through speakers or headphones.
- Record or monitor microphone input.
- Move mouse and type on keyboard.
- Connect an external monitor and set the expected refresh rate.
- Start a game from the launcher with the gamepad connected.

## Stage 19 Result

Stage 19 passes when:

- Ard OS starts on several different PCs.
- Network works through Wi-Fi and Ethernet where available.
- Bluetooth works on machines with supported adapters.
- Sound output and microphone work.
- NVIDIA, AMD, and Intel graphics pass Vulkan/OpenGL checks.
- Games start from the launcher.
- Gamepad, mouse, keyboard, and monitor behavior are usable.

Pay attention to:

- Wi-Fi adapters that need firmware not included in `linux-firmware`.
- NVIDIA Wayland failures.
- Laptops with no sound because of missing firmware, wrong profile, or muted PipeWire routes.
- Bluetooth adapters that need firmware or are soft-blocked.
- Gamepads that appear in `lsusb` but not as input devices.
- Controllers needing rules outside Steam's package coverage; document those per device instead of adding AUR packages to the base ISO.

Move to Stage 20 when the system works on several different hardware configurations.
