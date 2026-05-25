# Hoyoverse Compatibility

Do not claim Hoyoverse support until each game has been tested on an installed FlasterOS system.

Hoyoverse games may fail because of anti-cheat, launcher behavior, Wine/Proton regressions, or game updates. Do not bypass anti-cheat.

For HoyoPlay testing, prepare a real Proton path first:

```bash
ard-prepare-proton
```

Prefer a tested Proton build such as Proton Experimental, Proton 10+ when available, or a documented GE-Proton build installed in Steam compatibility tools. Record the exact Proton path or version in the table.

Status values:

- `not-tested`
- `works`
- `does-not-work`
- `blocked-by-anti-cheat`
- `blocked-by-launcher`
- `needs-retest`

| Game | Status | Runner | Hardware | Result / reason | Last tested |
| --- | --- | --- | --- | --- | --- |
| Genshin Impact | not-tested | n/a | n/a | No verified launch yet. Do not advertise support. | n/a |
| Honkai: Star Rail | not-tested | n/a | n/a | No verified launch yet. Do not advertise support. | n/a |
| Zenless Zone Zero | not-tested | n/a | n/a | No verified launch yet. Do not advertise support. | n/a |

Minimum proof for `works`:

- Installed FlasterOS, not only live ISO.
- 512 GB SSD recommended for testing GI + HSR + ZZZ together.
- Real GPU with Vulkan working.
- Game starts from the FlasterOS launcher.
- Game reaches playable state.
- `/games/GameName/logs/last-launch.log` exists.
- Result still works after reboot.
