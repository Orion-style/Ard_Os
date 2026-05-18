# Gaming Mode Checklist

Use this checklist for Stage 10 validation.

Gaming Mode is a separate login session where the launcher starts instead of the normal desktop.

Expected flow:

```text
turn on PC -> log in -> launcher opens -> choose game -> game starts -> close game -> return to launcher
```

## 10.1 Create A Separate Session

The login manager must show:

- Ard Desktop Mode: normal KDE Plasma desktop.
- Ard Gaming Mode: starts the launcher session.

Session files:

```text
/usr/share/xsessions/ard-desktop.desktop
/usr/share/xsessions/ard-gaming.desktop
```

Validation:

```bash
test -f /usr/share/xsessions/ard-desktop.desktop
test -f /usr/share/xsessions/ard-gaming.desktop
```

## 10.2 Start The Launcher Through Gamescope

Gaming Mode uses:

```text
login manager -> gamescope session -> launcher -> game
```

Session wrapper:

```bash
/usr/local/bin/ard-gaming-session
```

It starts:

```bash
gamescope -f -- ard-launcher
```

If Gamescope is missing, the wrapper logs that condition and starts `ard-launcher` directly so the user is not left at a black screen.

## 10.3 Return After Closing The Game

The launcher stays open while the selected game runs. After the game process exits, the launcher re-enables Play and shows launch status.

Validation:

- Start a game from Gaming Mode.
- Close the game.
- Confirm the launcher is still visible and usable.
- Confirm `/games/GameName/logs/last-launch.log` was updated.

## 10.4 Configure Controls

Check:

- Mouse.
- Keyboard.
- Gamepad.
- Alt+Tab.
- Exit from game.
- Reboot.
- Shutdown.

Launcher controls:

- Exit Session: closes the launcher and returns to the login manager.
- Reboot: calls `systemctl reboot`.
- Shutdown: calls `systemctl poweroff`.

Emergency exit shortcuts:

```text
Ctrl+Alt+Backspace
Ctrl+Alt+B
```

These close the launcher session and return to the login manager.

## Stage 10 Result

Stage 10 passes when:

- Gaming Mode can be selected at the login screen.
- After login, only the launcher opens.
- Games start from the launcher.
- After closing a game, the launcher is available again.
- The PC can be shut down from the launcher.

Pay attention to:

- Black screen after exiting a game.
- Window focus loss.
- Gamepad does not work.
- Game closed, but process remains.
- Launcher froze and there is no way out.

Move to Stage 11 when Gaming Mode works without using the terminal.
