# Game Profiles Checklist

Use this checklist for Stage 9 validation.

A game profile is the per-game launch configuration stored in that game's own `config.json`. Do not store all game settings in one global file.

Profiles can be edited through the launcher's Settings button or directly in the game's `config.json`.

## 9.1 Add Runner Selection

Each profile supports:

- `wine`
- `proton`
- `proton-experimental`
- `custom`

Example:

```json
{
  "runner": "proton-experimental",
  "custom_runner": ""
}
```

Use `custom_runner` when a game needs a specific runner path or command.

For Proton, do not assume a `proton` command exists in `PATH`. The launcher and `ard-run-game` should search common Steam compatibility tool paths first. If a game needs a specific Proton build, set `custom_runner`.

Before using a Proton profile on a fresh install, run:

```bash
ard-prepare-proton
```

Steam must download Proton before Proton profiles are guaranteed to work.

## 9.2 Add Environment Variables

Each profile has its own `env` object:

```json
{
  "env": {
    "MANGOHUD": "1",
    "WINEPREFIX": "/games/GameName/prefix",
    "DXVK_HUD": "0"
  }
}
```

Environment variables are applied only to that game launch.

## 9.3 Add Launch Arguments

Each profile supports launch arguments:

```json
{
  "launch_args": ["-windowed", "-force-vulkan"],
  "args": "-windowed -force-vulkan"
}
```

Use `launch_args` for new profiles. `args` remains supported for older configs.

## 9.4 Add Gamescope Settings

Each profile can enable Gamescope:

```json
{
  "gamescope": {
    "enabled": true,
    "width": 1920,
    "height": 1080,
    "fullscreen": true,
    "fps_limit": 60,
    "scaling": "fit"
  }
}
```

These settings are per game. Do not make Gamescope global for all games.

## 9.5 Add MangoHud Toggle

Each profile can enable MangoHud and choose what to show:

```json
{
  "mangohud": {
    "enabled": true,
    "show_fps": true,
    "show_temperature": true,
    "show_frametime": true
  }
}
```

## Stage 9 Result

Stage 9 passes when:

- Game 1 starts through Proton.
- Game 2 starts through Wine.
- Game 3 starts with MangoHud.
- Game 4 starts with an FPS limit through Gamescope.

Pay attention to:

- Do not change settings globally for all games.
- Do not store all settings in one file.
- Do not break a game profile when updating the launcher.

Move to Stage 10 when each game can have its own launch method without editing launcher code.
