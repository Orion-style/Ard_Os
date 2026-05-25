#!/usr/bin/env python3
import json
import os
import shutil
import subprocess
import threading
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, scrolledtext, simpledialog, ttk


CONFIG_DIR = Path.home() / ".config" / "ard-os"
PERFORMANCE_CONFIG = CONFIG_DIR / "performance.json"
UPDATE_LOG = Path("/var/log/flasteros/update.log")
BETA_WARNING = "Beta test version. Errors are possible."
REBOOT_UPDATE_PACKAGES = (
    "linux",
    "linux-firmware",
    "systemd",
    "mesa",
    "lib32-mesa",
    "vulkan-",
    "lib32-vulkan-",
    "nvidia",
    "amd-ucode",
    "intel-ucode",
    "wine",
    "steam",
    "vkd3d",
    "lib32-vkd3d",
    "dxvk",
    "gamescope",
    "plasma-",
    "xorg-",
)


def have(command):
    return shutil.which(command) is not None


def run(command, timeout=20):
    try:
        return subprocess.run(command, text=True, capture_output=True, timeout=timeout, check=False)
    except FileNotFoundError:
        return None
    except subprocess.TimeoutExpired as exc:
        proc = subprocess.CompletedProcess(command, 124, exc.stdout or "", exc.stderr or "Command timed out.")
        return proc


def command_text(command, timeout=20):
    proc = run(command, timeout=timeout)
    if proc is None:
        return "", f"Required tool is missing: {command[0]}"
    text = (proc.stdout or "").strip()
    error = (proc.stderr or "").strip()
    if proc.returncode != 0:
        return text, error or f"{command[0]} exited with code {proc.returncode}"
    return text, ""


class SettingsCenter(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("FlasterOS Settings Center")
        self.geometry("980x680")
        self.minsize(860, 560)
        self.status = tk.StringVar(value="Ready")
        self.wifi_rows = []
        self.sinks = []
        self.sources = []
        self.outputs = {}
        self.update_rows = []
        self._build()
        self.refresh_all()

    def _build(self):
        root = ttk.Frame(self, padding=12)
        root.pack(fill=tk.BOTH, expand=True)

        style = ttk.Style(self)
        style.configure("Brand.TLabel", foreground="#1ec8a5", font=("TkDefaultFont", 18, "bold"))

        heading = ttk.Frame(root)
        heading.pack(fill=tk.X, pady=(0, 8))
        ttk.Label(heading, text="FlasterOS", style="Brand.TLabel").pack(side=tk.LEFT)
        ttk.Label(heading, text="Settings Center").pack(side=tk.LEFT, padx=(8, 0))
        ttk.Label(heading, text=BETA_WARNING, foreground="#b36b00").pack(side=tk.LEFT, padx=(16, 0))
        ttk.Button(heading, text="Refresh", command=self.refresh_all).pack(side=tk.RIGHT)

        self.tabs = ttk.Notebook(root)
        self.tabs.pack(fill=tk.BOTH, expand=True)
        self._build_network_tab()
        self._build_sound_tab()
        self._build_display_tab()
        self._build_performance_tab()
        self._build_system_tab()

        ttk.Label(root, textvariable=self.status, anchor=tk.W).pack(fill=tk.X, pady=(8, 0))

    def _build_network_tab(self):
        tab = ttk.Frame(self.tabs, padding=12)
        self.tabs.add(tab, text="Network")

        left = ttk.Frame(tab)
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.wifi_tree = ttk.Treeview(left, columns=("signal", "security"), show="tree headings", selectmode="browse")
        self.wifi_tree.heading("#0", text="Wi-Fi Network")
        self.wifi_tree.heading("signal", text="Signal")
        self.wifi_tree.heading("security", text="Security")
        self.wifi_tree.column("#0", width=300)
        self.wifi_tree.column("signal", width=90, anchor=tk.CENTER)
        self.wifi_tree.column("security", width=160)
        self.wifi_tree.pack(fill=tk.BOTH, expand=True)

        buttons = ttk.Frame(tab, padding=(12, 0, 0, 0))
        buttons.pack(side=tk.RIGHT, fill=tk.Y)
        ttk.Button(buttons, text="Scan Wi-Fi", command=self.refresh_network).pack(fill=tk.X, pady=(0, 8))
        ttk.Button(buttons, text="Connect", command=self.connect_wifi).pack(fill=tk.X, pady=(0, 8))
        ttk.Button(buttons, text="Disable Wi-Fi", command=lambda: self.set_wifi(False)).pack(fill=tk.X, pady=(0, 8))
        ttk.Button(buttons, text="Enable Wi-Fi", command=lambda: self.set_wifi(True)).pack(fill=tk.X, pady=(0, 16))
        ttk.Label(buttons, text="Ethernet").pack(anchor=tk.W)
        self.ethernet_status = tk.StringVar(value="Unknown")
        ttk.Label(buttons, textvariable=self.ethernet_status, wraplength=250).pack(fill=tk.X, pady=(4, 16))
        ttk.Label(buttons, text="IP Address").pack(anchor=tk.W)
        self.ip_address = tk.StringVar(value="Unknown")
        ttk.Label(buttons, textvariable=self.ip_address, wraplength=250).pack(fill=tk.X, pady=(4, 0))

    def _build_sound_tab(self):
        tab = ttk.Frame(self.tabs, padding=12)
        self.tabs.add(tab, text="Sound")
        tab.columnconfigure(1, weight=1)

        self.output_device = tk.StringVar()
        self.input_device = tk.StringVar()
        self.volume = tk.IntVar(value=70)

        ttk.Label(tab, text="Output Device").grid(row=0, column=0, sticky=tk.W, pady=6)
        self.output_combo = ttk.Combobox(tab, textvariable=self.output_device, state="readonly")
        self.output_combo.grid(row=0, column=1, sticky=tk.EW, pady=6)
        ttk.Button(tab, text="Use Output", command=self.apply_output_device).grid(row=0, column=2, padx=(8, 0), pady=6)

        ttk.Label(tab, text="Microphone").grid(row=1, column=0, sticky=tk.W, pady=6)
        self.input_combo = ttk.Combobox(tab, textvariable=self.input_device, state="readonly")
        self.input_combo.grid(row=1, column=1, sticky=tk.EW, pady=6)
        ttk.Button(tab, text="Use Microphone", command=self.apply_input_device).grid(row=1, column=2, padx=(8, 0), pady=6)

        ttk.Label(tab, text="Volume").grid(row=2, column=0, sticky=tk.W, pady=6)
        ttk.Scale(tab, from_=0, to=100, variable=self.volume, command=lambda _v: self.volume_label.set(f"{self.volume.get()}%")).grid(row=2, column=1, sticky=tk.EW, pady=6)
        self.volume_label = tk.StringVar(value="70%")
        ttk.Label(tab, textvariable=self.volume_label, width=6).grid(row=2, column=2, sticky=tk.W, padx=(8, 0), pady=6)

        controls = ttk.Frame(tab)
        controls.grid(row=3, column=1, sticky=tk.W, pady=(8, 0))
        ttk.Button(controls, text="Apply Volume", command=self.apply_volume).pack(side=tk.LEFT)
        ttk.Button(controls, text="Sound Test", command=self.sound_test).pack(side=tk.LEFT, padx=(8, 0))

    def _build_display_tab(self):
        tab = ttk.Frame(self.tabs, padding=12)
        self.tabs.add(tab, text="Display")
        tab.columnconfigure(1, weight=1)

        self.monitor = tk.StringVar()
        self.resolution = tk.StringVar()
        self.refresh_rate = tk.StringVar()
        self.scaling = tk.StringVar(value="100%")

        ttk.Label(tab, text="Monitor").grid(row=0, column=0, sticky=tk.W, pady=6)
        self.monitor_combo = ttk.Combobox(tab, textvariable=self.monitor, state="readonly")
        self.monitor_combo.grid(row=0, column=1, sticky=tk.EW, pady=6)
        self.monitor_combo.bind("<<ComboboxSelected>>", lambda _event: self._monitor_changed())
        ttk.Button(tab, text="Main Monitor", command=self.set_primary_monitor).grid(row=0, column=2, padx=(8, 0), pady=6)

        ttk.Label(tab, text="Resolution").grid(row=1, column=0, sticky=tk.W, pady=6)
        self.resolution_combo = ttk.Combobox(tab, textvariable=self.resolution, state="readonly")
        self.resolution_combo.grid(row=1, column=1, sticky=tk.EW, pady=6)
        self.resolution_combo.bind("<<ComboboxSelected>>", lambda _event: self._monitor_changed(keep_resolution=True))

        ttk.Label(tab, text="Refresh Rate").grid(row=2, column=0, sticky=tk.W, pady=6)
        self.refresh_combo = ttk.Combobox(tab, textvariable=self.refresh_rate, state="readonly")
        self.refresh_combo.grid(row=2, column=1, sticky=tk.EW, pady=6)

        ttk.Label(tab, text="Scaling").grid(row=3, column=0, sticky=tk.W, pady=6)
        ttk.Combobox(tab, textvariable=self.scaling, values=("100%", "125%", "150%", "200%"), state="readonly").grid(row=3, column=1, sticky=tk.EW, pady=6)

        ttk.Button(tab, text="Apply Display", command=self.apply_display).grid(row=4, column=1, sticky=tk.W, pady=(12, 0))
        self.display_note = tk.StringVar(value="")
        ttk.Label(tab, textvariable=self.display_note, wraplength=620).grid(row=5, column=0, columnspan=3, sticky=tk.W, pady=(16, 0))

    def _build_performance_tab(self):
        tab = ttk.Frame(self.tabs, padding=12)
        self.tabs.add(tab, text="Performance")
        tab.columnconfigure(1, weight=1)

        config = self._load_performance()
        self.performance_mode = tk.StringVar(value=config.get("performance_mode", "balanced"))
        self.fps_limit = tk.StringVar(value=str(config.get("fps_limit", 60)))
        self.global_mangohud = tk.BooleanVar(value=bool(config.get("mangohud", False)))
        self.global_gamemode = tk.BooleanVar(value=bool(config.get("gamemode", False)))

        ttk.Label(tab, text="Performance Mode").grid(row=0, column=0, sticky=tk.W, pady=6)
        ttk.Combobox(tab, textvariable=self.performance_mode, values=("balanced", "performance", "powersave"), state="readonly").grid(row=0, column=1, sticky=tk.EW, pady=6)

        ttk.Label(tab, text="FPS Limit").grid(row=1, column=0, sticky=tk.W, pady=6)
        ttk.Entry(tab, textvariable=self.fps_limit, width=12).grid(row=1, column=1, sticky=tk.W, pady=6)

        ttk.Checkbutton(tab, text="Enable MangoHud by default for new game profiles", variable=self.global_mangohud).grid(row=2, column=1, sticky=tk.W, pady=6)
        ttk.Checkbutton(tab, text="Use Gamemode for supported launches", variable=self.global_gamemode).grid(row=3, column=1, sticky=tk.W, pady=6)
        ttk.Button(tab, text="Apply Performance", command=self.apply_performance).grid(row=4, column=1, sticky=tk.W, pady=(12, 0))
        ttk.Button(tab, text="Prepare Proton", command=self.prepare_proton).grid(row=5, column=1, sticky=tk.W, pady=(12, 0))
        ttk.Label(tab, text="Plain Wine DirectX 9/10/11 games need DXVK inside that game's prefix. Use ard-setup-wine-dxvk with the game config after plain Wine works.", wraplength=620).grid(row=6, column=1, sticky=tk.W, pady=(8, 0))

    def _build_system_tab(self):
        tab = ttk.Frame(self.tabs, padding=12)
        self.tabs.add(tab, text="System")

        self.os_version = tk.StringVar(value="Unknown")
        ttk.Label(tab, text="OS Version").pack(anchor=tk.W)
        ttk.Label(tab, textvariable=self.os_version).pack(anchor=tk.W, pady=(2, 16))

        updates = ttk.LabelFrame(tab, text="Updates", padding=10)
        updates.pack(fill=tk.BOTH, expand=True, pady=(0, 12))
        updates.columnconfigure(0, weight=1)
        updates.rowconfigure(1, weight=1)

        update_actions = ttk.Frame(updates)
        update_actions.grid(row=0, column=0, sticky=tk.EW, pady=(0, 8))
        ttk.Button(update_actions, text="Check Updates", command=self.check_updates).pack(side=tk.LEFT)
        self.install_updates_button = ttk.Button(update_actions, text="Install Updates", command=self.install_updates, state=tk.DISABLED)
        self.install_updates_button.pack(side=tk.LEFT, padx=(8, 0))
        self.update_summary = tk.StringVar(value="Press Check Updates to scan system packages, kernel, drivers, Wine, Proton, DXVK, VKD3D, launcher, and themes.")
        ttk.Label(update_actions, textvariable=self.update_summary, wraplength=560).pack(side=tk.LEFT, padx=(12, 0))

        columns = ("category", "current", "new", "size", "reboot")
        self.update_tree = ttk.Treeview(updates, columns=columns, show="tree headings", height=10, selectmode="none")
        self.update_tree.heading("#0", text="Package")
        self.update_tree.heading("category", text="Area")
        self.update_tree.heading("current", text="Current")
        self.update_tree.heading("new", text="New")
        self.update_tree.heading("size", text="Size")
        self.update_tree.heading("reboot", text="Reboot")
        self.update_tree.column("#0", width=180)
        self.update_tree.column("category", width=120)
        self.update_tree.column("current", width=120)
        self.update_tree.column("new", width=120)
        self.update_tree.column("size", width=90, anchor=tk.E)
        self.update_tree.column("reboot", width=80, anchor=tk.CENTER)
        self.update_tree.grid(row=1, column=0, sticky=tk.NSEW)

        actions = ttk.Frame(tab)
        actions.pack(anchor=tk.W)
        ttk.Button(actions, text="View Logs", command=self.view_logs).pack(side=tk.LEFT, padx=(8, 0))
        ttk.Button(actions, text="View Update Log", command=self.view_update_log).pack(side=tk.LEFT, padx=(8, 0))
        ttk.Button(actions, text="Check System", command=self.open_diagnostics).pack(side=tk.LEFT, padx=(8, 0))
        ttk.Button(actions, text="Reboot", command=self.reboot_system).pack(side=tk.LEFT, padx=(8, 0))
        ttk.Button(actions, text="Shutdown", command=self.shutdown_system).pack(side=tk.LEFT, padx=(8, 0))

    def refresh_all(self):
        self.refresh_network()
        self.refresh_sound()
        self.refresh_display()
        self.refresh_system()

    def refresh_network(self):
        self.wifi_tree.delete(*self.wifi_tree.get_children())
        self.wifi_rows = []
        text, error = command_text(["nmcli", "-t", "-f", "SSID,SIGNAL,SECURITY", "device", "wifi", "list", "--rescan", "yes"], timeout=25)
        if error:
            self.status.set(error)
        for line in text.splitlines():
            parts = line.split(":")
            ssid = parts[0].strip() if parts else ""
            if not ssid:
                continue
            signal = parts[1].strip() if len(parts) > 1 else ""
            security = ":".join(parts[2:]).strip() if len(parts) > 2 else ""
            self.wifi_rows.append((ssid, signal, security))
            self.wifi_tree.insert("", tk.END, iid=str(len(self.wifi_rows) - 1), text=ssid, values=(signal, security or "Open"))

        devices, _ = command_text(["nmcli", "-t", "-f", "DEVICE,TYPE,STATE,CONNECTION", "device", "status"])
        ethernet = []
        for line in devices.splitlines():
            parts = line.split(":")
            if len(parts) >= 3 and parts[1] == "ethernet":
                ethernet.append(f"{parts[0]}: {parts[2]}")
        self.ethernet_status.set("\n".join(ethernet) if ethernet else "No Ethernet device found")

        ips, ip_error = command_text(["ip", "-4", "-brief", "addr", "show"])
        self.ip_address.set(ips or ip_error or "No IPv4 address")

    def connect_wifi(self):
        selected = self.wifi_tree.selection()
        if not selected:
            self._error("Wi-Fi", "Choose a Wi-Fi network first.")
            return
        ssid, _signal, security = self.wifi_rows[int(selected[0])]
        command = ["nmcli", "device", "wifi", "connect", ssid]
        if security:
            password = simpledialog.askstring("Wi-Fi Password", f"Password for {ssid}:", show="*", parent=self)
            if password is None:
                return
            command.extend(["password", password])
        self._run_background(command, "Wi-Fi connected", self.refresh_network)

    def set_wifi(self, enabled):
        self._run_background(["nmcli", "radio", "wifi", "on" if enabled else "off"], "Wi-Fi updated", self.refresh_network)

    def refresh_sound(self):
        sinks, sink_error = command_text(["pactl", "list", "short", "sinks"])
        sources, source_error = command_text(["pactl", "list", "short", "sources"])
        if sink_error or source_error:
            self.status.set(sink_error or source_error)

        self.sinks = [line.split("\t")[1] for line in sinks.splitlines() if "\t" in line]
        self.sources = [line.split("\t")[1] for line in sources.splitlines() if "\t" in line and ".monitor" not in line]
        self.output_combo["values"] = self.sinks
        self.input_combo["values"] = self.sources
        if self.sinks and not self.output_device.get():
            self.output_device.set(self.sinks[0])
        if self.sources and not self.input_device.get():
            self.input_device.set(self.sources[0])

    def apply_output_device(self):
        if not self.output_device.get():
            self._error("Sound", "No output device is selected.")
            return
        self._run_background(["pactl", "set-default-sink", self.output_device.get()], "Output device selected")

    def apply_input_device(self):
        if not self.input_device.get():
            self._error("Sound", "No microphone is selected.")
            return
        self._run_background(["pactl", "set-default-source", self.input_device.get()], "Microphone selected")

    def apply_volume(self):
        value = max(0, min(100, int(self.volume.get())))
        self._run_background(["pactl", "set-sink-volume", "@DEFAULT_SINK@", f"{value}%"], "Volume updated")

    def sound_test(self):
        if have("speaker-test"):
            subprocess.Popen(["speaker-test", "-t", "sine", "-f", "880", "-l", "1"])
            self.status.set("Playing test tone")
        else:
            self._error("Sound Test", "speaker-test is not installed.")

    def refresh_display(self):
        text, error = command_text(["xrandr", "--query"])
        self.outputs = {}
        if error:
            self.display_note.set(f"Display control needs xrandr in this session. Details: {error}")
            self.monitor_combo["values"] = ()
            return
        current = None
        for line in text.splitlines():
            if " connected" in line:
                current = line.split()[0]
                self.outputs[current] = {"modes": {}, "primary": " primary " in f" {line} "}
            elif current and line.startswith("   "):
                parts = line.split()
                if parts and "x" in parts[0]:
                    mode = parts[0]
                    rates = [part.replace("*", "").replace("+", "") for part in parts[1:]]
                    self.outputs[current]["modes"][mode] = rates
        monitors = list(self.outputs.keys())
        self.monitor_combo["values"] = monitors
        if monitors and self.monitor.get() not in monitors:
            self.monitor.set(monitors[0])
        self._monitor_changed()
        self.display_note.set("Display changes are applied through xrandr for the active graphical session.")

    def _monitor_changed(self, keep_resolution=False):
        monitor = self.monitor.get()
        modes = self.outputs.get(monitor, {}).get("modes", {})
        resolutions = list(modes.keys())
        self.resolution_combo["values"] = resolutions
        if resolutions and (not keep_resolution or self.resolution.get() not in resolutions):
            self.resolution.set(resolutions[0])
        rates = modes.get(self.resolution.get(), [])
        self.refresh_combo["values"] = rates
        if rates and self.refresh_rate.get() not in rates:
            self.refresh_rate.set(rates[0])

    def apply_display(self):
        if not self.monitor.get() or not self.resolution.get():
            self._error("Display", "Choose a monitor and resolution first.")
            return
        command = ["xrandr", "--output", self.monitor.get(), "--mode", self.resolution.get()]
        if self.refresh_rate.get():
            command.extend(["--rate", self.refresh_rate.get()])
        scale = {"100%": "1x1", "125%": "0.8x0.8", "150%": "0.6667x0.6667", "200%": "0.5x0.5"}[self.scaling.get()]
        command.extend(["--scale", scale])
        self._run_background(command, "Display updated", self.refresh_display)

    def set_primary_monitor(self):
        if not self.monitor.get():
            self._error("Display", "Choose a monitor first.")
            return
        self._run_background(["xrandr", "--output", self.monitor.get(), "--primary"], "Main monitor updated", self.refresh_display)

    def _load_performance(self):
        defaults = {"performance_mode": "balanced", "fps_limit": 60, "mangohud": False, "gamemode": True}
        try:
            config = json.loads(PERFORMANCE_CONFIG.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return defaults
        return {**defaults, **config}

    def apply_performance(self):
        try:
            fps = int(self.fps_limit.get())
            if fps < 0 or fps > 1000:
                raise ValueError
        except ValueError:
            self._error("Performance", "FPS limit must be a number from 0 to 1000.")
            return

        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        data = {
            "performance_mode": self.performance_mode.get(),
            "fps_limit": fps,
            "mangohud": self.global_mangohud.get(),
            "gamemode": self.global_gamemode.get(),
        }
        PERFORMANCE_CONFIG.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        if have("powerprofilesctl"):
            self._run_background(["powerprofilesctl", "set", self.performance_mode.get()], "Performance updated")
        else:
            self.status.set(f"Performance settings saved to {PERFORMANCE_CONFIG}")

    def prepare_proton(self):
        if have("ard-prepare-proton"):
            self._run_background(["ard-prepare-proton"], "Proton preparation finished")
        else:
            self._error("Prepare Proton", "ard-prepare-proton is not installed.")

    def refresh_system(self):
        version = "FlasterOS"
        try:
            for line in Path("/etc/os-release").read_text(encoding="utf-8").splitlines():
                if line.startswith("PRETTY_NAME="):
                    version = line.split("=", 1)[1].strip().strip('"')
                    break
        except OSError:
            pass
        self.os_version.set(version)

    def check_updates(self):
        self.install_updates_button.configure(state=tk.DISABLED)
        self.update_summary.set("Checking for updates...")
        self.update_tree.delete(*self.update_tree.get_children())

        def worker():
            rows, error = self._collect_updates()
            self.after(0, self._show_updates, rows, error)

        threading.Thread(target=worker, daemon=True).start()

    def _collect_updates(self):
        if not have("checkupdates"):
            return [], "Missing pacman-contrib: checkupdates is required for safe non-root update checks."
        proc = run(["checkupdates", "--nocolor"], timeout=120)
        if proc is None:
            return [], "Required tool is missing: checkupdates"
        output = (proc.stdout or "").strip()
        if not output and proc.returncode in (0, 2):
            return [], ""
        if proc.returncode not in (0, 2):
            return [], (proc.stderr or proc.stdout or "Could not check for updates.").strip()

        rows = []
        for line in output.splitlines():
            parts = line.split()
            if len(parts) < 4 or parts[2] != "->":
                continue
            package, current, new = parts[0], parts[1], parts[3]
            rows.append({
                "package": package,
                "category": self._update_category(package),
                "current": current,
                "new": new,
                "size": self._package_download_size(package),
                "reboot": self._update_needs_reboot(package),
            })
        return rows, ""

    def _show_updates(self, rows, error):
        self.update_rows = rows
        self.update_tree.delete(*self.update_tree.get_children())
        if error:
            self.update_summary.set(error)
            self._error("Update check failed", error)
            return
        if not rows:
            self.update_summary.set("System is up to date.")
            self.status.set("No updates found")
            return
        total_known = self._total_download_size(rows)
        reboot = any(row["reboot"] for row in rows)
        for index, row in enumerate(rows):
            self.update_tree.insert(
                "",
                tk.END,
                iid=str(index),
                text=row["package"],
                values=(row["category"], row["current"], row["new"], row["size"], "Yes" if row["reboot"] else "No"),
            )
        summary = f"{len(rows)} update(s)"
        if total_known:
            summary += f", about {total_known}"
        summary += ". Reboot required." if reboot else ". No reboot expected."
        self.update_summary.set(summary)
        self.status.set("Update check finished")
        self.install_updates_button.configure(state=tk.NORMAL)

    def install_updates(self):
        if not self.update_rows:
            self._error("Install Updates", "Check for updates first.")
            return
        trust_error = self._pacman_trust_error()
        if trust_error:
            self._error("Install Updates", trust_error)
            return
        reboot = any(row["reboot"] for row in self.update_rows)
        message = f"Install {len(self.update_rows)} update(s) now?\n\nA btrfs snapshot will be created first. A log will be written to {UPDATE_LOG}."
        if reboot:
            message += "\n\nA reboot is expected after this update."
        if not messagebox.askyesno("Install Updates", message, parent=self):
            return

        command_text = (
            "install -d -m 0755 /var/log/flasteros; "
            "{ printf '\\n===== FlasterOS update %s =====\\n' \"$(date -Is)\"; "
            "ard-snapshot pre-update && "
            "pacman -Syu --noconfirm; status=$?; "
            "printf '===== update finished with exit code %s =====\\n' \"$status\"; "
            "exit \"$status\"; } >> /var/log/flasteros/update.log 2>&1"
        )
        command = ["pkexec", "sh", "-c", command_text] if have("pkexec") else ["sudo", "sh", "-c", command_text]
        self.install_updates_button.configure(state=tk.DISABLED)
        self.status.set("Installing updates...")

        def done():
            self.check_updates()
            if reboot and messagebox.askyesno("Updates installed", "Updates finished. Reboot now?", parent=self):
                subprocess.Popen(["systemctl", "reboot"])

        def failed():
            self.install_updates_button.configure(state=tk.NORMAL)

        self._run_background(command, f"Updates installed. Log: {UPDATE_LOG}", done, timeout=3600, error_callback=failed)

    def _pacman_trust_error(self):
        try:
            lines = Path("/etc/pacman.conf").read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError as exc:
            return f"Cannot verify pacman trust settings: {exc}"
        siglevels = []
        active_repos = []
        for raw_line in lines:
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            if line.startswith("[") and line.endswith("]"):
                repo = line.strip("[]")
                if repo != "options":
                    active_repos.append(repo)
                continue
            if line.lower().startswith("siglevel"):
                siglevels.append(line.split("=", 1)[1].strip())
        if not any("Required" in level and "Never" not in level for level in siglevels):
            return "Refusing to update because pacman signature verification is not required."
        allowed_repos = {"core", "extra", "multilib"}
        unknown = [repo for repo in active_repos if repo not in allowed_repos]
        if unknown:
            return f"Review untrusted pacman repositories before updating: {', '.join(unknown)}"
        return ""

    def _update_category(self, package):
        if package in ("linux", "linux-firmware") or package.endswith("-ucode"):
            return "Kernel"
        if "nvidia" in package or package.startswith(("mesa", "lib32-mesa", "vulkan-", "lib32-vulkan-")):
            return "Drivers"
        if package.startswith("wine") or package in ("winetricks",):
            return "Wine"
        if package in ("steam", "gamescope") or "proton" in package:
            return "Proton"
        if "dxvk" in package:
            return "DXVK"
        if "vkd3d" in package:
            return "VKD3D"
        if package.startswith(("plasma-", "breeze", "sddm", "xorg-")):
            return "Themes"
        if package.startswith("ard-"):
            return "Launcher"
        return "System"

    def _update_needs_reboot(self, package):
        return any(package == item or package.startswith(item) for item in REBOOT_UPDATE_PACKAGES)

    def _package_download_size(self, package):
        text, error = command_text(["pacman", "-Si", package], timeout=10)
        if error:
            return "Unknown"
        for line in text.splitlines():
            if line.startswith("Download Size"):
                return line.split(":", 1)[1].strip() or "Unknown"
        return "Unknown"

    def _total_download_size(self, rows):
        total_mib = 0.0
        known = False
        for row in rows:
            value = row["size"]
            parts = value.split()
            if len(parts) < 2:
                continue
            try:
                amount = float(parts[0])
            except ValueError:
                continue
            unit = parts[1].lower()
            if unit.startswith("kib"):
                total_mib += amount / 1024
            elif unit.startswith("mib"):
                total_mib += amount
            elif unit.startswith("gib"):
                total_mib += amount * 1024
            else:
                continue
            known = True
        if not known:
            return ""
        if total_mib >= 1024:
            return f"{total_mib / 1024:.2f} GiB"
        return f"{total_mib:.1f} MiB"

    def view_logs(self):
        command = ["journalctl", "-b", "-n", "300", "--no-pager"]
        text, error = command_text(command, timeout=10)
        self._text_window("System Logs", text or error or "No logs returned.")

    def view_update_log(self):
        try:
            text = UPDATE_LOG.read_text(encoding="utf-8", errors="replace")
        except OSError as exc:
            text = f"Could not read {UPDATE_LOG}: {exc}"
        self._text_window("Update Log", text or "No update log entries.")

    def open_diagnostics(self):
        try:
            subprocess.Popen(["python3", "/opt/ard-os/diagnostics/ard-diagnostics.py"])
        except OSError as exc:
            self._error("Diagnostics", f"Could not open diagnostics: {exc}")

    def reboot_system(self):
        if messagebox.askyesno("Reboot", "Reboot the PC now?", parent=self):
            subprocess.Popen(["systemctl", "reboot"])

    def shutdown_system(self):
        if messagebox.askyesno("Shutdown", "Shut down the PC now?", parent=self):
            subprocess.Popen(["systemctl", "poweroff"])

    def _run_background(self, command, success, callback=None, timeout=300, error_callback=None):
        self.status.set(f"Running: {' '.join(command)}")

        def worker():
            proc = run(command, timeout=timeout)
            if proc is None:
                self.after(0, self._error, "Command missing", f"Required tool is missing: {command[0]}")
                if error_callback:
                    self.after(0, error_callback)
                return
            if proc.returncode != 0:
                message = (proc.stderr or proc.stdout or f"{command[0]} exited with code {proc.returncode}").strip()
                if command[0] == "sudo" and "password" in message.lower():
                    message = "Administrator permission is required. Install polkit/pkexec or run this action from a desktop session that can show an authentication dialog."
                self.after(0, self._error, "Settings error", message)
                if error_callback:
                    self.after(0, error_callback)
                return
            self.after(0, self.status.set, success)
            if callback:
                self.after(0, callback)

        threading.Thread(target=worker, daemon=True).start()

    def _error(self, title, message):
        self.status.set(message)
        messagebox.showerror(title, message, parent=self)

    def _text_window(self, title, text):
        window = tk.Toplevel(self)
        window.title(title)
        window.geometry("820x520")
        area = scrolledtext.ScrolledText(window, wrap=tk.WORD)
        area.pack(fill=tk.BOTH, expand=True)
        area.insert(tk.END, text)
        area.configure(state=tk.DISABLED)


if __name__ == "__main__":
    SettingsCenter().mainloop()
