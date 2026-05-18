#!/usr/bin/env python3
import json
import os
import shutil
import shlex
import subprocess
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, scrolledtext, simpledialog, ttk


GAMES_DIR = Path("/games")


class Game:
    def __init__(self, config_path, data):
        self.config_path = config_path
        self.dir = config_path.parent
        self.data = data

    @property
    def name(self):
        return self.data.get("name") or self.dir.name

    @property
    def exe(self):
        return Path(self.data.get("exe", ""))

    @property
    def prefix(self):
        return Path(self.data.get("prefix", ""))

    @property
    def runner(self):
        return self.data.get("runner", "wine")

    @property
    def args(self):
        return self.data.get("args", "")

    @property
    def launch_args(self):
        value = self.data.get("launch_args", self.args)
        if isinstance(value, list):
            return [str(item) for item in value]
        if isinstance(value, str) and value:
            return shlex.split(value)
        return []

    @property
    def env_vars(self):
        value = self.data.get("env", {})
        return value if isinstance(value, dict) else {}

    @property
    def custom_runner(self):
        return self.data.get("custom_runner", "")

    @property
    def gamescope(self):
        value = self.data.get("gamescope", {})
        return value if isinstance(value, dict) else {}

    @property
    def mangohud(self):
        value = self.data.get("mangohud", {})
        return value if isinstance(value, dict) else {}

    @property
    def logs_dir(self):
        return self.dir / "logs"

    @property
    def last_log(self):
        return self.logs_dir / "last-launch.log"

    @property
    def crash_log(self):
        return self.logs_dir / "crash.log"


class Launcher(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Ard Launcher")
        self.geometry("900x560")
        self.minsize(760, 460)
        self.games = []
        self.selected_index = None
        self._build_ui()
        self.refresh_games()

    def _build_ui(self):
        root = ttk.Frame(self, padding=12)
        root.pack(fill=tk.BOTH, expand=True)

        left = ttk.Frame(root)
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        columns = ("runner", "exe")
        self.tree = ttk.Treeview(left, columns=columns, show="tree headings", selectmode="browse")
        self.tree.heading("#0", text="Game")
        self.tree.heading("runner", text="Runner")
        self.tree.heading("exe", text="Executable")
        self.tree.column("#0", width=220, minwidth=160)
        self.tree.column("runner", width=90, minwidth=70, anchor=tk.CENTER)
        self.tree.column("exe", width=360, minwidth=220)
        self.tree.pack(fill=tk.BOTH, expand=True)
        self.tree.bind("<<TreeviewSelect>>", self._on_select)
        self.tree.bind("<Double-1>", lambda _event: self.play_selected())

        self.status = tk.StringVar(value="Ready")
        status = ttk.Label(left, textvariable=self.status, anchor=tk.W)
        status.pack(fill=tk.X, pady=(8, 0))

        right = ttk.Frame(root, padding=(12, 0, 0, 0))
        right.pack(side=tk.RIGHT, fill=tk.Y)

        self.play_button = ttk.Button(right, text="Play", command=self.play_selected)
        self.play_button.pack(fill=tk.X, pady=(0, 8))
        ttk.Button(right, text="Settings", command=self.show_settings).pack(fill=tk.X, pady=(0, 8))
        ttk.Button(right, text="Add Game", command=self.add_game).pack(fill=tk.X, pady=(0, 8))
        ttk.Button(right, text="Remove Game", command=self.remove_game).pack(fill=tk.X, pady=(0, 8))
        ttk.Button(right, text="Logs", command=self.show_logs).pack(fill=tk.X, pady=(0, 8))
        ttk.Button(right, text="Refresh", command=self.refresh_games).pack(fill=tk.X, pady=(16, 8))

    def refresh_games(self):
        self.games = []
        self.tree.delete(*self.tree.get_children())
        GAMES_DIR.mkdir(parents=True, exist_ok=True)
        for config_path in sorted(GAMES_DIR.glob("*/config.json")):
            try:
                data = json.loads(config_path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError) as exc:
                self._show_error("Config read error", f"{config_path}\n{exc}")
                continue
            game = Game(config_path, data)
            self.games.append(game)
            self.tree.insert("", tk.END, iid=str(len(self.games) - 1), text=game.name, values=(game.runner, str(game.exe)))
        self.status.set(f"{len(self.games)} game config(s) found in /games")

    def _on_select(self, _event=None):
        selected = self.tree.selection()
        self.selected_index = int(selected[0]) if selected else None

    def selected_game(self):
        if self.selected_index is None:
            self._show_error("No game selected", "Choose a game from the list first.")
            return None
        return self.games[self.selected_index]

    def validate_game(self, game):
        if os.geteuid() == 0:
            return "Launcher must not run games as root."
        if not str(game.exe):
            return "Config is missing exe path."
        if not game.exe.exists():
            return f"exe file not found: {game.exe}"
        if not str(game.prefix):
            return "Config is missing prefix path."
        if not game.prefix.exists():
            return f"Wine prefix not found: {game.prefix}"
        if game.runner == "wine" and shutil.which("wine") is None:
            return "runner not installed: wine"
        if game.runner in ("proton", "proton-experimental"):
            proton_runner = game.custom_runner or shutil.which("proton")
            if not proton_runner:
                return "runner not installed: proton. Set custom_runner to a Proton executable or use Steam-managed Proton."
            if game.custom_runner and not Path(game.custom_runner).exists() and shutil.which(game.custom_runner) is None:
                return f"custom runner not found: {game.custom_runner}"
        if game.runner == "custom":
            if not game.custom_runner:
                return "custom runner is required when runner is custom."
            if not Path(game.custom_runner).exists() and shutil.which(game.custom_runner) is None:
                return f"custom runner not found: {game.custom_runner}"
        if game.runner not in ("wine", "proton", "proton-experimental", "custom"):
            return f"unsupported runner: {game.runner}"
        if game.gamescope.get("enabled") and shutil.which("gamescope") is None:
            return "runner not installed: gamescope"
        if game.mangohud.get("enabled") and shutil.which("mangohud") is None:
            return "runner not installed: mangohud"
        try:
            game.last_log.parent.mkdir(parents=True, exist_ok=True)
            with game.last_log.open("a", encoding="utf-8"):
                pass
        except OSError as exc:
            return f"permission error writing logs: {exc}"
        return None

    def play_selected(self):
        game = self.selected_game()
        if game is None:
            return
        error = self.validate_game(game)
        if error:
            self.write_error_log(game, error)
            self._show_error("Launch blocked", error)
            return

        env = os.environ.copy()
        env["WINEPREFIX"] = str(game.prefix)
        for key, value in game.env_vars.items():
            env[str(key)] = str(value)
        env.setdefault("DXVK_HUD", "0")
        env.update(self._mangohud_env(game))
        command = self._build_command(game)

        self.status.set(f"Launching {game.name}")
        self.play_button.configure(state=tk.DISABLED)
        threading.Thread(target=self._run_game, args=(game, command, env), daemon=True).start()

    def _run_game(self, game, command, env):
        game.logs_dir.mkdir(parents=True, exist_ok=True)
        with game.last_log.open("w", encoding="utf-8") as log:
            log.write(f"Game: {game.name}\n")
            log.write(f"Command: {' '.join(command)}\n")
            log.write(f"WINEPREFIX: {env.get('WINEPREFIX', '')}\n\n")
            log.flush()
            try:
                proc = subprocess.Popen(command, stdout=log, stderr=subprocess.STDOUT, env=env)
                code = proc.wait()
            except OSError as exc:
                code = 1
                log.write(f"Wine launch error: {exc}\n")
            if code != 0:
                shutil.copyfile(game.last_log, game.crash_log)
        self.after(0, self._launch_done, game, code)

    def _launch_done(self, game, code):
        self.play_button.configure(state=tk.NORMAL)
        if code == 0:
            self.status.set(f"{game.name} exited normally")
        else:
            self.status.set(f"{game.name} failed. Open Logs for details.")
            self._show_error("Wine launch error", f"{game.name} exited with code {code}. See {game.last_log}")

    def write_error_log(self, game, error):
        game.logs_dir.mkdir(parents=True, exist_ok=True)
        text = f"Launch blocked: {error}\n"
        game.last_log.write_text(text, encoding="utf-8")
        game.crash_log.write_text(text, encoding="utf-8")

    def _build_command(self, game):
        args = game.launch_args
        if game.runner == "wine":
            command = ["wine", str(game.exe), *args]
        elif game.runner in ("proton", "proton-experimental"):
            runner = game.custom_runner or shutil.which("proton") or "proton"
            command = [runner, "run", str(game.exe), *args]
        elif game.runner == "custom":
            runner_parts = shlex.split(game.custom_runner)
            command = [*runner_parts, str(game.exe), *args]
        else:
            command = ["wine", str(game.exe), *args]

        if game.mangohud.get("enabled"):
            command = ["mangohud", *command]

        if game.gamescope.get("enabled"):
            command = [*self._gamescope_prefix(game.gamescope), *command]

        return command

    def _gamescope_prefix(self, settings):
        command = ["gamescope"]
        width = settings.get("width") or settings.get("resolution_width")
        height = settings.get("height") or settings.get("resolution_height")
        fps_limit = settings.get("fps_limit")
        scaling = settings.get("scaling")
        if width:
            command.extend(["-W", str(width)])
        if height:
            command.extend(["-H", str(height)])
        if fps_limit:
            command.extend(["-r", str(fps_limit)])
        if settings.get("fullscreen"):
            command.append("-f")
        if scaling:
            command.extend(["-S", str(scaling)])
        command.append("--")
        return command

    def _mangohud_env(self, game):
        settings = game.mangohud
        env = {"MANGOHUD": "1" if settings.get("enabled") else "0"}
        options = []
        if settings.get("show_fps"):
            options.append("fps")
        if settings.get("show_temperature"):
            options.extend(["gpu_temp", "cpu_temp"])
        if settings.get("show_frametime"):
            options.append("frametime")
        if options:
            env["MANGOHUD_CONFIG"] = ",".join(options)
        return env

    def show_settings(self):
        game = self.selected_game()
        if game is None:
            return
        ProfileEditor(self, game, self.refresh_games)

    def show_logs(self):
        game = self.selected_game()
        if game is None:
            return
        if not game.last_log.exists():
            self._show_error("No log", f"No last launch log exists yet: {game.last_log}")
            return
        self._text_window(f"{game.name} Last Launch Log", game.last_log.read_text(encoding="utf-8", errors="replace"))

    def add_game(self):
        if os.geteuid() == 0:
            self._show_error("Root blocked", "Do not add or run games as root.")
            return
        game_id = simpledialog.askstring("Add Game", "Game folder id, for example GameName:")
        if not game_id:
            return
        if not all(ch.isalnum() or ch in "._-" for ch in game_id):
            self._show_error("Invalid game id", "Use only letters, numbers, dot, underscore, and hyphen.")
            return
        name = simpledialog.askstring("Add Game", "Display name:", initialvalue=game_id) or game_id
        exe = filedialog.askopenfilename(title="Choose .exe file")
        if not exe:
            return
        runner = simpledialog.askstring(
            "Add Game",
            "Runner: wine, proton, proton-experimental, or custom",
            initialvalue="wine",
        ) or "wine"
        if runner not in ("wine", "proton", "proton-experimental", "custom"):
            self._show_error("Invalid runner", "Runner must be wine, proton, proton-experimental, or custom.")
            return
        game_dir = GAMES_DIR / game_id
        if game_dir.exists():
            self._show_error("Game exists", f"{game_dir} already exists.")
            return
        prefix = game_dir / "prefix"
        logs = game_dir / "logs"
        logs.mkdir(parents=True, exist_ok=False)
        prefix.mkdir(parents=True, exist_ok=True)
        (logs / "last-launch.log").touch()
        (logs / "crash.log").touch()
        config = {
            "name": name,
            "exe": exe,
            "prefix": str(prefix),
            "runner": runner,
            "custom_runner": "",
            "env": {"DXVK_HUD": "0"},
            "launch_args": [],
            "args": "",
            "gamescope": {
                "enabled": False,
                "width": 1920,
                "height": 1080,
                "fullscreen": True,
                "fps_limit": 60,
                "scaling": "fit",
            },
            "mangohud": {
                "enabled": False,
                "show_fps": True,
                "show_temperature": False,
                "show_frametime": False,
            },
        }
        (game_dir / "config.json").write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")
        self.refresh_games()

    def remove_game(self):
        game = self.selected_game()
        if game is None:
            return
        if not messagebox.askyesno("Remove Game", f"Remove {game.name} and its folder?\n\n{game.dir}"):
            return
        shutil.rmtree(game.dir)
        self.selected_index = None
        self.refresh_games()

    def _show_error(self, title, message):
        messagebox.showerror(title, message)

    def _text_window(self, title, text):
        window = tk.Toplevel(self)
        window.title(title)
        window.geometry("760x480")
        area = scrolledtext.ScrolledText(window, wrap=tk.WORD)
        area.pack(fill=tk.BOTH, expand=True)
        area.insert(tk.END, text)
        area.configure(state=tk.DISABLED)


class ProfileEditor(tk.Toplevel):
    def __init__(self, parent, game, on_save):
        super().__init__(parent)
        self.game = game
        self.on_save = on_save
        self.title(f"{game.name} Profile")
        self.geometry("640x620")
        self.resizable(True, True)
        self._build()

    def _build(self):
        frame = ttk.Frame(self, padding=12)
        frame.pack(fill=tk.BOTH, expand=True)

        self.runner = tk.StringVar(value=self.game.runner)
        self.custom_runner = tk.StringVar(value=self.game.custom_runner)
        self.args = tk.StringVar(value=" ".join(self.game.launch_args))
        self.gamescope_enabled = tk.BooleanVar(value=bool(self.game.gamescope.get("enabled")))
        self.gamescope_width = tk.StringVar(value=str(self.game.gamescope.get("width", 1920)))
        self.gamescope_height = tk.StringVar(value=str(self.game.gamescope.get("height", 1080)))
        self.gamescope_fullscreen = tk.BooleanVar(value=bool(self.game.gamescope.get("fullscreen", True)))
        self.gamescope_fps = tk.StringVar(value=str(self.game.gamescope.get("fps_limit", 60)))
        self.gamescope_scaling = tk.StringVar(value=str(self.game.gamescope.get("scaling", "fit")))
        self.mangohud_enabled = tk.BooleanVar(value=bool(self.game.mangohud.get("enabled")))
        self.mangohud_fps = tk.BooleanVar(value=bool(self.game.mangohud.get("show_fps", True)))
        self.mangohud_temp = tk.BooleanVar(value=bool(self.game.mangohud.get("show_temperature", False)))
        self.mangohud_frametime = tk.BooleanVar(value=bool(self.game.mangohud.get("show_frametime", False)))

        row = 0
        ttk.Label(frame, text="Runner").grid(row=row, column=0, sticky=tk.W, pady=4)
        ttk.Combobox(
            frame,
            textvariable=self.runner,
            values=("wine", "proton", "proton-experimental", "custom"),
            state="readonly",
        ).grid(row=row, column=1, sticky=tk.EW, pady=4)
        row += 1

        ttk.Label(frame, text="Custom Runner").grid(row=row, column=0, sticky=tk.W, pady=4)
        ttk.Entry(frame, textvariable=self.custom_runner).grid(row=row, column=1, sticky=tk.EW, pady=4)
        row += 1

        ttk.Label(frame, text="Launch Args").grid(row=row, column=0, sticky=tk.W, pady=4)
        ttk.Entry(frame, textvariable=self.args).grid(row=row, column=1, sticky=tk.EW, pady=4)
        row += 1

        ttk.Label(frame, text="Environment").grid(row=row, column=0, sticky=tk.NW, pady=4)
        self.env_text = tk.Text(frame, height=6, wrap=tk.NONE)
        self.env_text.grid(row=row, column=1, sticky=tk.NSEW, pady=4)
        self.env_text.insert(tk.END, "\n".join(f"{key}={value}" for key, value in self.game.env_vars.items()))
        row += 1

        ttk.Checkbutton(frame, text="Use Gamescope", variable=self.gamescope_enabled).grid(row=row, column=1, sticky=tk.W, pady=4)
        row += 1
        gamescope_frame = ttk.Frame(frame)
        gamescope_frame.grid(row=row, column=1, sticky=tk.EW, pady=4)
        for idx, (label, var) in enumerate((
            ("Width", self.gamescope_width),
            ("Height", self.gamescope_height),
            ("FPS", self.gamescope_fps),
            ("Scaling", self.gamescope_scaling),
        )):
            ttk.Label(gamescope_frame, text=label).grid(row=0, column=idx * 2, sticky=tk.W, padx=(0, 4))
            ttk.Entry(gamescope_frame, textvariable=var, width=8).grid(row=0, column=idx * 2 + 1, sticky=tk.W, padx=(0, 10))
        row += 1
        ttk.Checkbutton(frame, text="Gamescope Fullscreen", variable=self.gamescope_fullscreen).grid(row=row, column=1, sticky=tk.W, pady=4)
        row += 1

        ttk.Checkbutton(frame, text="Use MangoHud", variable=self.mangohud_enabled).grid(row=row, column=1, sticky=tk.W, pady=4)
        row += 1
        hud_frame = ttk.Frame(frame)
        hud_frame.grid(row=row, column=1, sticky=tk.EW, pady=4)
        ttk.Checkbutton(hud_frame, text="FPS", variable=self.mangohud_fps).pack(side=tk.LEFT)
        ttk.Checkbutton(hud_frame, text="Temperature", variable=self.mangohud_temp).pack(side=tk.LEFT, padx=8)
        ttk.Checkbutton(hud_frame, text="Frametime", variable=self.mangohud_frametime).pack(side=tk.LEFT)
        row += 1

        buttons = ttk.Frame(frame)
        buttons.grid(row=row, column=0, columnspan=2, sticky=tk.E, pady=(16, 0))
        ttk.Button(buttons, text="Cancel", command=self.destroy).pack(side=tk.RIGHT, padx=(8, 0))
        ttk.Button(buttons, text="Save", command=self.save).pack(side=tk.RIGHT)

        frame.columnconfigure(1, weight=1)
        frame.rowconfigure(3, weight=1)

    def save(self):
        try:
            env = self._parse_env()
            launch_args = shlex.split(self.args.get()) if self.args.get() else []
        except ValueError as exc:
            messagebox.showerror("Profile error", str(exc), parent=self)
            return

        data = dict(self.game.data)
        data["runner"] = self.runner.get()
        data["custom_runner"] = self.custom_runner.get()
        data["env"] = env
        data["launch_args"] = launch_args
        data["args"] = self.args.get()
        data["gamescope"] = {
            "enabled": self.gamescope_enabled.get(),
            "width": self._int_or_empty(self.gamescope_width.get()),
            "height": self._int_or_empty(self.gamescope_height.get()),
            "fullscreen": self.gamescope_fullscreen.get(),
            "fps_limit": self._int_or_empty(self.gamescope_fps.get()),
            "scaling": self.gamescope_scaling.get(),
        }
        data["mangohud"] = {
            "enabled": self.mangohud_enabled.get(),
            "show_fps": self.mangohud_fps.get(),
            "show_temperature": self.mangohud_temp.get(),
            "show_frametime": self.mangohud_frametime.get(),
        }
        self.game.config_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        self.on_save()
        self.destroy()

    def _parse_env(self):
        env = {}
        for line in self.env_text.get("1.0", tk.END).splitlines():
            line = line.strip()
            if not line:
                continue
            if "=" not in line:
                raise ValueError(f"Environment line must be KEY=VALUE: {line}")
            key, value = line.split("=", 1)
            key = key.strip()
            if not key or not key.replace("_", "").isalnum() or key[0].isdigit():
                raise ValueError(f"Invalid environment variable name: {key}")
            env[key] = value.strip()
        return env

    def _int_or_empty(self, value):
        value = value.strip()
        return int(value) if value else ""


if __name__ == "__main__":
    Launcher().mainloop()
