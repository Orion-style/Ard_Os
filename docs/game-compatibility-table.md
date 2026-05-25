# Game Compatibility Table

Use this table for Stage 20 and release validation.

Status values:

- `works`
- `works-with-notes`
- `broken`
- `blocked-by-anti-cheat`
- `needs-retest`

## Tested Games

| Game | Version | Runner | GPU | Status | Notes | Last tested |
| --- | --- | --- | --- | --- | --- | --- |
| Test Windows program | n/a | Wine | AMD/Intel/NVIDIA | needs-retest | Use as the minimum launcher smoke test. | n/a |

Hoyoverse status is tracked separately in:

```text
docs/hoyoverse-compatibility.md
```

Do not copy a Hoyoverse game into the supported list until it is verified there first.

## Required Fields

For every release-supported game, record:

- Game name.
- Game version or launcher version.
- Runner: Wine, Proton, Proton Experimental, or custom.
- GPU tested.
- Status.
- Notes.
- Last tested date.

Do not list a game as supported unless it starts from the FlasterOS launcher and writes a launch log.
