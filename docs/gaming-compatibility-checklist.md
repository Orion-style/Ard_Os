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
