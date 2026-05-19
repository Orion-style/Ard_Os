# Settings Center Checklist

Use this checklist for Stage 11 validation.

The Settings Center replaces basic terminal commands for normal users. It must let the user configure internet, sound, display, gaming performance, and basic system actions from a graphical interface.

Command:

```bash
ard-settings-center
```

The launcher also exposes the same tool through the Settings Center button.

## 11.1 Network

The Network tab must show:

- Wi-Fi network list.
- Connect to selected Wi-Fi network.
- Disable Wi-Fi.
- Enable Wi-Fi.
- Ethernet status.
- IPv4 address.

Validation:

- Wi-Fi scan lists nearby SSIDs.
- Secured Wi-Fi asks for a password in the interface.
- Successful connection refreshes the IP address display.
- Wi-Fi can be turned off and back on without terminal commands.
- Ethernet state is visible when a cable is connected.

## 11.2 Sound

The Sound tab must show:

- Output device selection.
- Microphone selection.
- Volume control.
- Sound test.

Validation:

- Output device can be selected with PipeWire/PulseAudio through `pactl`.
- Microphone can be selected.
- Volume changes apply to the default sink.
- Sound Test plays a short test tone.

## 11.3 Display

The Display tab must show:

- Monitor selection.
- Resolution.
- Refresh rate.
- Scaling.
- Main monitor.

Validation:

- Connected monitors are listed.
- Resolution and refresh rate can be applied.
- A monitor can be set as primary.
- Scaling can be changed from the interface.
- Errors are shown clearly if the current session cannot be controlled through `xrandr`.

## 11.4 Performance

The Performance tab must show:

- Performance mode.
- FPS limit.
- MangoHud toggle.
- Gamemode toggle.

Validation:

- Settings are saved in the user's Ard OS config.
- New game profiles use the saved FPS limit and MangoHud default.
- When Gamemode is enabled, game launches use `gamemoderun` if available.
- Performance mode applies through `powerprofilesctl` when supported.

## 11.5 System

The System tab must show:

- Updates.
- Logs.
- Reboot.
- Shutdown.
- OS version.

Validation:

- OS version is read from `/etc/os-release`.
- Logs open in a graphical window.
- Updates run through a graphical authorization path when available.
- Reboot and shutdown ask for confirmation.

## Stage 11 Result

Stage 11 passes when:

- Wi-Fi can be connected from the Settings Center.
- Sound output and microphone can be selected from the Settings Center.
- Resolution or main monitor can be changed from the Settings Center.
- MangoHud and Gamemode defaults can be enabled from the Settings Center.
- System updates can be started without opening a terminal.

Pay attention to:

- Do not allow arbitrary system file editing from the interface.
- Show understandable errors when tools or permissions are missing.
- Do not require terminal commands for basic actions.

Move to Stage 12 when internet, sound, and display can be configured from the interface.
