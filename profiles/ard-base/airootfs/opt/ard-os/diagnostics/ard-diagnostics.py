#!/usr/bin/env python3
import argparse
import os
import re
import shutil
import socket
import subprocess
import tempfile
import threading
import time
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, scrolledtext, ttk


REPORT_DIR = Path.home() / "ard-diagnostics"
REPORT_FILE = REPORT_DIR / "report.txt"
GAMES_DIR = Path("/games")
MAX_COMMAND_CHARS = 12000
MAX_LOG_CHARS = 20000
NETWORK_TARGETS = ("archlinux.org", "steamcdn-a.akamaihd.net")
SECRET_PATTERNS = (
    re.compile(r"(?i)(password|passwd|token|secret|apikey|api_key|authorization|cookie)\s*[:=]\s*\S+"),
    re.compile(r"(?i)(bearer\s+)[A-Za-z0-9._~+/=-]+"),
)


def have(command):
    return shutil.which(command) is not None


def run(command, timeout=20, env=None):
    try:
        return subprocess.run(command, text=True, capture_output=True, timeout=timeout, check=False, env=env)
    except FileNotFoundError:
        return None
    except subprocess.TimeoutExpired as exc:
        return subprocess.CompletedProcess(command, 124, exc.stdout or "", exc.stderr or "Command timed out.")
    except OSError as exc:
        return subprocess.CompletedProcess(command, 1, "", str(exc))


def redact(text):
    if not text:
        return ""
    clean = text.replace("\r\n", "\n")
    for pattern in SECRET_PATTERNS:
        clean = pattern.sub(lambda match: match.group(1) + "=<redacted>" if match.lastindex else "<redacted>", clean)
    home = str(Path.home())
    if home and home != "/":
        clean = clean.replace(home, "$HOME")
    if len(clean) > MAX_COMMAND_CHARS:
        clean = clean[:MAX_COMMAND_CHARS] + "\n... truncated ...\n"
    return clean


def read_limited(path, limit=MAX_LOG_CHARS):
    try:
        data = Path(path).read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        return f"Could not read {path}: {exc}"
    if len(data) > limit:
        return data[-limit:] + "\n... earlier log output truncated ...\n"
    return data


class Report:
    def __init__(self):
        self.lines = []

    def section(self, title):
        self.lines.append("")
        self.lines.append(f"## {title}")
        self.lines.append("")

    def line(self, text=""):
        self.lines.append(str(text))

    def command(self, label, command, timeout=20, env=None):
        self.line(f"$ {' '.join(command)}")
        proc = run(command, timeout=timeout, env=env)
        if proc is None:
            self.line(f"Result: MISSING ({command[0]})")
            return None
        self.line(f"Exit code: {proc.returncode}")
        output = "\n".join(part for part in ((proc.stdout or "").strip(), (proc.stderr or "").strip()) if part)
        self.line(redact(output) or "(no output)")
        return proc

    def status(self, label, ok, detail=""):
        state = "PASS" if ok else "FAIL"
        self.line(f"{state}: {label}{f' - {detail}' if detail else ''}")

    def text(self):
        return "\n".join(self.lines).strip() + "\n"


def first_line(text):
    return (text or "").strip().splitlines()[0] if (text or "").strip() else ""


def collect_system(report):
    report.section("System")
    report.line(f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S %Z')}")
    report.command("OS version", ["cat", "/etc/os-release"])
    report.command("Kernel version", ["uname", "-a"])
    report.command("CPU", ["sh", "-c", "lscpu | sed -n '1,25p'"])


def collect_graphics(report):
    report.section("Graphics")
    lspci = report.command("Graphics card and driver", ["sh", "-c", "lspci -nnk | grep -EA4 'VGA|3D|Display'"])
    report.status("graphics card detected", bool(lspci and first_line(lspci.stdout)))

    vulkan = report.command("Vulkan", ["vulkaninfo", "--summary"], timeout=30)
    report.status("Vulkan works", bool(vulkan and vulkan.returncode == 0 and "GPU" in (vulkan.stdout or "")))

    glx = report.command("OpenGL", ["glxinfo", "-B"], timeout=20)
    report.status("OpenGL works", bool(glx and glx.returncode == 0 and "OpenGL renderer" in (glx.stdout or "")))


def proton_candidates():
    candidates = []
    roots = [
        Path.home() / ".steam/root/compatibilitytools.d",
        Path.home() / ".local/share/Steam/compatibilitytools.d",
        Path.home() / ".local/share/Steam/steamapps/common",
    ]
    for root in roots:
        if root.exists():
            candidates.extend(root.glob("**/proton"))
    if have("proton"):
        candidates.append(Path(shutil.which("proton")))
    return sorted({str(path) for path in candidates if path.exists()})


def collect_wine(report):
    report.section("Wine And Proton")
    wine_version = report.command("Wine version", ["wine", "--version"])
    report.status("Wine installed", bool(wine_version and wine_version.returncode == 0))

    proton = proton_candidates()
    report.status("Proton installed", bool(proton), proton[0] if proton else "No Proton executable found in Steam compatibility paths.")
    if proton:
        report.line("Proton candidates:")
        for path in proton[:10]:
            report.line(f"- {path}")

    if not have("wine"):
        report.status("prefix can be created", False, "wine is missing")
        report.status("test .exe can start", False, "wine is missing")
        return

    with tempfile.TemporaryDirectory(prefix="ard-wine-prefix-") as tempdir:
        env = os.environ.copy()
        env["WINEPREFIX"] = tempdir
        boot = report.command("Create temporary Wine prefix", ["wineboot", "--init"], timeout=90, env=env)
        report.status("prefix can be created", bool(boot and boot.returncode == 0))
        test_exe = report.command("Start Wine test .exe", ["wine", "cmd", "/c", "ver"], timeout=60, env=env)
        report.status("test .exe can start", bool(test_exe and test_exe.returncode == 0))


def collect_dxvk(report):
    report.section("DXVK And VKD3D")
    dxvk_paths = find_dxvk_paths()
    vkd3d = report.command("VKD3D packages", ["sh", "-c", "pacman -Q vkd3d lib32-vkd3d 2>/dev/null || true"])
    report.status("DXVK available", bool(dxvk_paths), f"{len(dxvk_paths)} matching file(s)" if dxvk_paths else "No DXVK files found.")
    report.status("VKD3D available", bool(vkd3d and "vkd3d" in (vkd3d.stdout or "")))
    vulkan = run(["vulkaninfo", "--summary"], timeout=30)
    report.status("game runtime can see Vulkan", bool(vulkan and vulkan.returncode == 0))


def find_dxvk_paths(limit=50):
    matches = []
    roots = (
        Path("/usr/share/dxvk"),
        Path("/usr/lib/dxvk"),
        Path("/usr/lib32/dxvk"),
        Path.home() / ".local/share/Steam/steamapps/common",
        Path.home() / ".steam/root/steamapps/common",
    )
    for root in roots:
        if not root.exists():
            continue
        if "dxvk" in root.name.lower():
            matches.append(root)
        for current, dirs, files in os.walk(root):
            dirs[:] = [name for name in dirs if name not in (".git", "shadercache", "compatdata")]
            if "dxvk" in Path(current).name.lower():
                matches.append(Path(current))
            for name in files:
                if "dxvk" in name.lower():
                    matches.append(Path(current) / name)
            if len(matches) >= limit:
                return sorted({str(path) for path in matches})[:limit]
    return sorted({str(path) for path in matches})[:limit]


def collect_network(report):
    report.section("Network")
    internet = run(["curl", "-I", "--max-time", "10", "https://archlinux.org"], timeout=15)
    report.status("internet reachable", bool(internet and internet.returncode == 0))
    for host in NETWORK_TARGETS:
        try:
            socket.gethostbyname(host)
            report.status(f"DNS resolves {host}", True)
        except OSError as exc:
            report.status(f"DNS resolves {host}", False, str(exc))
    mirror = first_pacman_mirror()
    if mirror:
        target = mirror.replace("$repo", "core").replace("$arch", "x86_64")
        update = run(["curl", "-I", "--max-time", "10", target], timeout=15)
        report.status("update servers reachable", bool(update and update.returncode == 0), target)
    else:
        report.status("update servers reachable", False, "No enabled pacman mirror found.")


def first_pacman_mirror():
    try:
        for line in Path("/etc/pacman.d/mirrorlist").read_text(encoding="utf-8", errors="replace").splitlines():
            line = line.strip()
            if line.startswith("Server ="):
                return line.split("=", 1)[1].strip()
    except OSError:
        return ""
    return ""


def du_size(path):
    proc = run(["du", "-sh", str(path)], timeout=30)
    if proc and proc.returncode == 0:
        return proc.stdout.strip()
    return f"{path}: unavailable"


def collect_disk(report):
    report.section("Disk Space")
    report.command("Free space", ["df", "-h", "/", str(GAMES_DIR), "/var/log"], timeout=20)
    for label, path in (
        ("games folder size", GAMES_DIR),
        ("logs size", Path("/var/log/ard-os")),
    ):
        report.line(f"{label}: {du_size(path) if path.exists() else f'{path} does not exist'}")
    prefixes = sorted(GAMES_DIR.glob("*/prefix")) if GAMES_DIR.exists() else []
    total = 0
    report.line("prefix sizes:")
    if not prefixes:
        report.line("- no game prefixes found")
    for prefix in prefixes[:30]:
        report.line(f"- {du_size(prefix)}")
        total += 1
    if len(prefixes) > total:
        report.line(f"- {len(prefixes) - total} more prefix(es) omitted")


def collect_logs(report):
    report.section("Last Launch Error And Game Logs")
    logs = []
    if GAMES_DIR.exists():
        logs.extend(GAMES_DIR.glob("*/logs/crash.log"))
        logs.extend(GAMES_DIR.glob("*/logs/last-launch.log"))
    logs = sorted({path for path in logs if path.exists()}, key=lambda path: path.stat().st_mtime, reverse=True)
    if not logs:
        report.line("No game launch logs found.")
        return
    for path in logs[:8]:
        report.line(f"### {path}")
        report.line(redact(read_limited(path)))


def generate_report():
    report = Report()
    report.line("# Ard OS Diagnostic Report")
    report.line("")
    report.line("This report is generated for debugging game launch and system compatibility problems.")
    report.line("It avoids browser files, documents, saved passwords, tokens, and unrelated personal files.")
    collect_system(report)
    collect_graphics(report)
    collect_wine(report)
    collect_dxvk(report)
    collect_network(report)
    collect_disk(report)
    collect_logs(report)
    text = report.text()
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_FILE.write_text(text, encoding="utf-8")
    return text


class DiagnosticsApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Ard System Diagnostics")
        self.geometry("940x680")
        self.minsize(780, 520)
        self.status = tk.StringVar(value="Press Check System to run diagnostics.")
        self._build()

    def _build(self):
        root = ttk.Frame(self, padding=12)
        root.pack(fill=tk.BOTH, expand=True)
        controls = ttk.Frame(root)
        controls.pack(fill=tk.X, pady=(0, 8))
        self.check_button = ttk.Button(controls, text="Check System", command=self.check_system)
        self.check_button.pack(side=tk.LEFT)
        self.save_button = ttk.Button(controls, text="Create report", command=self.create_report)
        self.save_button.pack(side=tk.LEFT, padx=(8, 0))
        ttk.Label(controls, textvariable=self.status, anchor=tk.W).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(12, 0))
        self.output = scrolledtext.ScrolledText(root, wrap=tk.WORD)
        self.output.pack(fill=tk.BOTH, expand=True)

    def check_system(self):
        self.create_report()

    def create_report(self):
        self.check_button.configure(state=tk.DISABLED)
        self.save_button.configure(state=tk.DISABLED)
        self.status.set("Running diagnostics...")

        def worker():
            try:
                text = generate_report()
            except Exception as exc:
                self.after(0, self._failed, str(exc))
                return
            self.after(0, self._done, text)

        threading.Thread(target=worker, daemon=True).start()

    def _done(self, text):
        self.output.configure(state=tk.NORMAL)
        self.output.delete("1.0", tk.END)
        self.output.insert(tk.END, text)
        self.output.configure(state=tk.DISABLED)
        self.status.set(f"Report saved: {REPORT_FILE}")
        self.check_button.configure(state=tk.NORMAL)
        self.save_button.configure(state=tk.NORMAL)
        messagebox.showinfo("Report created", f"Saved report.txt to:\n{REPORT_FILE}", parent=self)

    def _failed(self, error):
        self.status.set(error)
        self.check_button.configure(state=tk.NORMAL)
        self.save_button.configure(state=tk.NORMAL)
        messagebox.showerror("Diagnostics failed", error, parent=self)


def main():
    parser = argparse.ArgumentParser(description="Run Ard OS system diagnostics.")
    parser.add_argument("--report", action="store_true", help="create report.txt and print the path")
    args = parser.parse_args()
    if args.report:
        generate_report()
        print(REPORT_FILE)
        return
    DiagnosticsApp().mainloop()


if __name__ == "__main__":
    main()
