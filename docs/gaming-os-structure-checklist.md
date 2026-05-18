# Gaming OS Structure Checklist

Use this checklist for Stage 7 validation.

Stage 7 organizes the gaming system. Games, Wine prefixes, configs, and logs must have predictable locations. Do not place them randomly across the filesystem.

## 7.1 Separate System And Game Files

Required structure:

```text
/opt/ard-os/       Ard OS programs and OS-owned files
/games/            installed games and per-game runtime data
/var/log/ard-os/   Ard OS system logs
/home/user/        normal user files
```

Rules:

- Do not store games in `/opt/ard-os`, `/usr`, `/etc`, or other system folders.
- Do not run games as root.
- Use `/games` for installed games, prefixes, per-game configs, and per-game logs.

Validation:

```bash
test -d /opt/ard-os
test -d /games
test -d /var/log/ard-os
test "$(id -u)" -ne 0
```

## 7.2 Create A Separate Folder For Each Game

Examples:

```text
/games/GenshinImpact/
/games/ZZZ/
/games/StarRail/
```

Create a new game structure with:

```bash
ard-create-game --id GameName --name "Game Name" --exe /games/GameName/game.exe
```

## 7.3 Create A Separate Wine Prefix For Each Game

Each game must have its own Wine prefix:

```text
/games/GenshinImpact/prefix/
/games/ZZZ/prefix/
/games/StarRail/prefix/
```

A Wine prefix is a separate Windows-like environment for one game. Do not use one shared prefix for all games; one game can break another game's settings.

## 7.4 Create A Separate Config For Each Game

Each game has a `config.json`:

```json
{
  "name": "Game Name",
  "exe": "/games/GameName/game.exe",
  "prefix": "/games/GameName/prefix",
  "runner": "wine",
  "args": ""
}
```

Supported manual runner for this stage:

- `wine`: runs with `WINEPREFIX` set to the game's prefix.

Steam-managed Proton remains the preferred Proton path from Stage 6. Do not mix Steam Proton data into a manual Wine prefix.

## 7.5 Create Separate Logs For Each Game

Each game has separate logs:

```text
/games/GameName/logs/last-launch.log
/games/GameName/logs/crash.log
```

Run a game from its config with:

```bash
ard-run-game /games/GameName/config.json
```

The command writes launch output to:

```text
/games/GameName/logs/last-launch.log
```

## Stage 7 Result

Each game must have its own separate environment:

- The game is stored in its own folder.
- The game has its own prefix.
- The game has its own `config.json`.
- The game has its own logs.
- Deleting one game does not break another.

Pay attention to:

- Do not store games in system folders.
- Do not run games as root.
- Do not use one prefix for all games.
- Do not mix logs from different games.

Move to Stage 8 when you can manually add a game into this structure and run it using its config.
