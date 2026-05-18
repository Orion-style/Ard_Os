# Game Launcher Checklist

Use this checklist for Stage 8 validation.

The launcher is the main interface of the gaming OS. The user should not need to type launch commands manually in a terminal. They should open the launcher, choose a game, and press Play.

## 8.1 Create The Main Window

The launcher command is:

```bash
ard-launcher
```

The main window must include:

- Game list.
- Play button.
- Settings button.
- Add Game button.
- Remove Game button.
- Logs button.

The launcher must run as the normal user, not root.

## 8.2 Read Game Configs

The launcher scans:

```text
/games/
```

It finds:

```text
/games/*/config.json
```

Each valid `config.json` is added to the game list.

Required config shape:

```json
{
  "name": "Game Name",
  "exe": "/games/GameName/game.exe",
  "prefix": "/games/GameName/prefix",
  "runner": "wine",
  "custom_runner": "",
  "env": {
    "MANGOHUD": "0",
    "WINEPREFIX": "/games/GameName/prefix",
    "DXVK_HUD": "0"
  },
  "launch_args": [],
  "args": "",
  "gamescope": {
    "enabled": false,
    "width": 1920,
    "height": 1080,
    "fullscreen": true,
    "fps_limit": 60,
    "scaling": "fit"
  },
  "mangohud": {
    "enabled": false,
    "show_fps": true,
    "show_temperature": false,
    "show_frametime": false
  }
}
```

## 8.3 Launch Games

The launcher builds a launch command from the game config:

- Reads the executable path.
- Reads the Wine prefix path.
- Chooses the runner.
- Sets environment variables.
- Launches the game.
- Saves the log.

Supported runner behavior:

- `wine`: launches directly with `WINEPREFIX` set to the game's prefix.
- `proton`: launches with a standalone Proton command or `custom_runner`.
- `proton-experimental`: launches with a standalone Proton command or `custom_runner`.
- `custom`: launches with the command from `custom_runner`.

Each game must launch from its own prefix.

The Settings button edits per-game profile fields including runner, custom runner, environment variables, launch arguments, Gamescope settings, and MangoHud settings.

## 8.4 Show Errors

The launcher must show useful errors in the interface and write them to logs.

Required error cases:

- `exe file not found`
- `Wine prefix not found`
- `runner not installed`
- `permission error`
- `Wine launch error`

The launcher must not hide these behind a generic `Error` message.

## 8.5 View Logs

The Logs button opens the last launch log:

```text
/games/GameName/logs/last-launch.log
```

Failed launches also update:

```text
/games/GameName/logs/crash.log
```

## Stage 8 Result

Stage 8 passes when:

- Launcher opens.
- Games appear in the list.
- Play button launches a game.
- Errors are visible in the interface.
- Logs are saved.

Pay attention to:

- Launcher must not require root.
- Game paths must come from `config.json`.
- Errors must be written to logs.
- Games must launch from separate prefixes.

Move to Stage 9 when the launcher can start at least 2-3 different programs using configs.
