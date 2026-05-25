# Performance Checklist

Use this checklist for Stage 18 validation.

The system should spend minimum resources on itself and maximum resources on the game. Performance work must not break sound, network, updates, graphics drivers, or rollback.

## 18.1 Remove Unnecessary Services

Keep required system services enabled:

- `NetworkManager.service`
- `sddm.service`
- PipeWire and WirePlumber user services
- update, snapshot, and graphics driver tooling required by earlier stages

Do not enable background services just because the package is installed. VM guest services are enabled only when the installed system detects a matching virtual machine:

- QEMU/KVM: `qemu-guest-agent.service` and `spice-vdagentd.service`
- VirtualBox: `vboxservice.service`
- Bare metal: no VM guest service should be enabled

Validation:

```bash
systemctl --type=service --state=running
systemctl is-enabled NetworkManager.service sddm.service
systemctl is-enabled qemu-guest-agent.service vboxservice.service || true
```

On real gaming hardware, confirm that guest services are disabled or missing without disabling network, audio, updates, SDDM, or power profile controls.

## 18.2 Configure GameMode

GameMode should activate automatically when a game starts from the launcher or from `ard-run-game`.

Launcher behavior:

- The default performance config enables GameMode.
- If `~/.config/ard-os/performance.json` exists, its `gamemode` value controls the wrapper.
- When enabled and `gamemoderun` is installed, launches are wrapped with `gamemoderun`.

Validation:

```bash
gamemoded -t
ard-run-game /games/GameName/config.json
```

The launch log should show the game starting normally, and GameMode should not be required for system tools, desktop applications, updates, or installers.

## 18.3 Configure zram

Install `zram-generator` and provide:

```text
/etc/systemd/zram-generator.conf
```

Default policy:

```ini
[zram0]
zram-size = ram / 2
compression-algorithm = zstd
swap-priority = 100
```

Validation after reboot:

```bash
zramctl
swapon --show
systemctl status systemd-zram-setup@zram0.service
```

zram should exist as compressed swap. It should help low-RAM systems without replacing real RAM or hiding memory leaks.

## 18.4 Configure Shader Cache

Game launches should leave shader caching enabled by default.

Launch environment defaults:

```text
DXVK_STATE_CACHE=1
MESA_SHADER_CACHE_DISABLE=false
MESA_SHADER_CACHE_MAX_SIZE=12G
```

Validation:

```bash
grep -E 'DXVK_STATE_CACHE|MESA_SHADER_CACHE' /games/GameName/logs/last-launch.log || true
find ~/.cache -maxdepth 3 -iname '*shader*' -o -iname '*dxvk*'
```

The exact cache location depends on the game, runner, Steam, DXVK, and Mesa. Do not delete shader caches during normal cleanup unless the user asks for troubleshooting.

## 18.5 Check Frametime

Do not judge performance by FPS alone. A game can show high FPS and still stutter.

Use MangoHud with frametime enabled:

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

Validation:

- Start a known game from the launcher.
- Confirm startup time is reasonable.
- Confirm FPS is stable.
- Confirm frametime is smooth, without repeated spikes.
- Confirm closing the game returns to the launcher.

## Stage 18 Result

Stage 18 passes when:

- Games start quickly.
- There is no unnecessary background load.
- FPS is stable.
- Frametime is smooth.
- zram is active and RAM is not wasted.
- Sound, network, updates, rollback, and graphics still work.

Pay attention to:

- Do not disable important services.
- Do not break PipeWire, WirePlumber, NetworkManager, SDDM, updates, or snapshots.
- Do not use global cleanup that deletes game prefixes, shader caches, or Steam compatibility data.
- Do not optimize benchmarks while making real games less stable.

Move to Stage 19 when the system works stably and does not load the hardware without reason.
