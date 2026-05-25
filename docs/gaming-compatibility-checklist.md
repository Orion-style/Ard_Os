# Gaming Compatibility Layer Checklist

Use this checklist for Stage 6 validation.

Stage 6 adds the ability to run Windows programs and games on Linux. Start this stage only after Stage 5 passes: GPU is detected, Vulkan works on the real GPU, OpenGL works on the real GPU, and the display is stable after reboot.

The compatibility path is:

```text
.exe game -> Wine/Proton -> DXVK/VKD3D -> Vulkan -> Linux -> graphics card
```

The game behaves as if it is running on Windows, while its calls are translated to Linux.

## 6.1 Install Wine

Wine is needed to run `.exe` files and provides basic compatibility with Windows programs.

Install the base Wine set:

```bash
sudo pacman -Syu --needed wine wine-gecko wine-mono winetricks
```

The installed system also includes a helper:

```bash
sudo ard-install-gaming-compat
```

Package roles:

- `wine`: Windows compatibility layer.
- `wine-gecko`: browser engine replacement used by Wine applications.
- `wine-mono`: .NET Framework replacement used by Wine applications.
- `winetricks`: helper for installing common Windows runtime components into Wine prefixes.
- `steam`: first supported path for Proton-managed games.
- `mangohud`: FPS and hardware overlay.
- `gamemode`: per-game performance optimization daemon and launcher.
- `gamescope`: nested compositor for isolated game sessions.

Validation commands:

```bash
wine --version
wineboot --init
winecfg
```

Rules:

- Run Wine as the normal user, not root.
- Do not use Wine before Vulkan and OpenGL pass Stage 5 checks.
- Keep the first Wine prefix simple; do not tune DXVK, VKD3D, Proton, or launchers yet.

Pass criteria:

- `wine --version` prints a Wine version.
- `wineboot --init` creates a Wine prefix for the normal user.
- `winecfg` opens.
- No Wine process runs as root.

Do not move to Proton, DXVK, VKD3D, or launcher work until plain Wine starts correctly.

## 6.2 Install Proton

Proton is a gaming-oriented version of Wine and usually works better for games.

Use Proton through Steam first:

```bash
steam
```

In Steam, enable Steam Play for supported titles and, when needed, for all other titles. Steam manages official Proton downloads inside the user's Steam library.

Standalone Proton can be added later through a managed compatibility-tools directory, but do not make it the first path. Start with Steam-managed Proton because it keeps the game runtime, Proton version, DXVK, and VKD3D-Proton together.

Validation:

- Steam starts as the normal user.
- Steam Play can be enabled.
- At least one Proton version appears in Steam compatibility settings after Steam downloads it.
- No Steam or Proton process runs as root.

Helper:

```bash
ard-prepare-proton
```

This checks common Steam compatibility paths for Proton. If Proton is missing, it starts Steam and tells the user to enable Steam Play and download Proton. Proton is not guaranteed immediately after package installation; Steam must download a compatibility tool first.

## 6.3 Install DXVK

DXVK is needed for DirectX 9/10/11 games.

```text
DirectX 11 -> DXVK -> Vulkan
```

For Steam games, use Proton. Proton includes DXVK for DirectX 9/10/11 translation.

Do not assume a separate system `dxvk` package is installed from the official Arch repositories. In this project, Proton is the primary DXVK path. Standalone Wine prefixes need an explicit, documented DXVK setup such as `winetricks dxvk`, a trusted custom DXVK install, or a package source chosen by the maintainer.

For a standalone Wine prefix, install DXVK into that prefix only after plain Wine works:

```bash
WINEPREFIX="$HOME/.wine-ard-test" wineboot --init
WINEPREFIX="$HOME/.wine-ard-test" winetricks dxvk
```

For a FlasterOS game config:

```bash
ard-setup-wine-dxvk /games/GameName/config.json
```

Validation:

- Vulkan already passes `vulkaninfo --summary`.
- The Wine prefix is owned by the normal user.
- A DirectX 9/10/11 test game starts through Proton or the DXVK-enabled Wine prefix.

## 6.4 Install VKD3D-Proton

VKD3D-Proton is needed for DirectX 12 games.

```text
DirectX 12 -> VKD3D-Proton -> Vulkan
```

For Steam games, use Proton. Proton includes VKD3D-Proton for DirectX 12 translation.

For standalone Wine testing, keep this separate from the first simple Wine prefix. DirectX 12 compatibility depends heavily on GPU driver quality and Vulkan support.

Validation:

- Vulkan works on the real GPU.
- Proton starts a DirectX 12 test game, or the selected Wine prefix has an explicitly installed VKD3D/VKD3D-Proton setup.
- Any failure is recorded with the Wine prefix path, GPU driver, Vulkan result, and game name.

## 6.5 Install Helper Tools

Required tools:

- `winetricks`
- `mangohud`
- `gamemode`
- `gamescope`

Purpose:

- `winetricks`: installs Windows libraries into Wine prefixes.
- `mangohud`: shows FPS and hardware load.
- `gamemode`: optimizes the system while gaming.
- `gamescope`: creates a separate gaming session.

Install or refresh them:

```bash
sudo pacman -Syu --needed winetricks mangohud lib32-mangohud gamemode lib32-gamemode gamescope
```

The repository helper installs the full Stage 6 base package set:

```bash
sudo ard-install-gaming-compat
```

Validation commands:

```bash
winetricks --version
mangohud --version
gamemoded -t
gamescope --version
```

MangoHud test:

```bash
mangohud glxgears
```

GameMode test with a command:

```bash
gamemoderun glxgears
```

Gamescope smoke test:

```bash
gamescope -- glxgears
```

## Stage 6 Result

At the end of Stage 6:

- `.exe` files start.
- A Wine prefix is created.
- Steam starts.
- A simple Windows game starts.
- MangoHud shows FPS.

Pay attention to:

- Wrong Wine prefix.
- Missing Vulkan support.
- Missing DXVK in the selected Proton or Wine-prefix path.
- Missing Windows libraries.
- Games that require anti-cheat.
- Games that require a specific Windows API version.

Do not try to bypass anti-cheat. If a game does not start because of anti-cheat, treat it as a compatibility limitation.

Move to Stage 7 only when at least one Windows game starts through Wine or Proton.
