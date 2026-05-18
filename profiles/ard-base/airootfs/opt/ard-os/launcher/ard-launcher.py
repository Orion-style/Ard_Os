#!/usr/bin/env python3
import json
import os
import shutil
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
        if game.runner == "proton" and shutil.which("proton") is None:
            return "runner not installed: proton. Use Steam-managed Proton or install a standalone proton command."
        if game.runner not in ("wine", "proton"):
            return f"unsupported runner: {game.runner}"
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
        env.setdefault("MANGOHUD", "0")
        args = game.args.split() if game.args else []
        command = ["wine", str(game.exe), *args] if game.runner == "wine" else ["proton", "run", str(game.exe), *args]

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

    def show_settings(self):
        game = self.selected_game()
        if game is None:
            return
        self._text_window(f"{game.name} Settings", game.config_path.read_text(encoding="utf-8"))

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
        runner = simpledialog.askstring("Add Game", "Runner: wine or proton", initialvalue="wine") or "wine"
        if runner not in ("wine", "proton"):
            self._show_error("Invalid runner", "Runner must be wine or proton.")
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
        config = {"name": name, "exe": exe, "prefix": str(prefix), "runner": runner, "args": ""}
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


if __name__ == "__main__":
    Launcher().mainloop()
