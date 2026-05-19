#!/usr/bin/env python3
import os
import json
import re
import subprocess
import tempfile
import threading
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, ttk


MIN_PASSWORD_LEN = 6
USERNAME_RE = re.compile(r"^[a-z_][a-z0-9_-]*[$]?$")
HOSTNAME_RE = re.compile(r"^[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?$")

TEXT = {
    "en": {
        "title": "Install FlasterOS",
        "language": "Language",
        "language_text": "Choose installer language.",
        "disk": "Disk",
        "disk_text": "Select the disk where FlasterOS will be installed.",
        "refresh": "Refresh",
        "warning": "All data on the selected disk will be deleted.",
        "scheme": "Partition scheme: EFI, /, /home",
        "user": "User",
        "username": "Username",
        "password": "Password",
        "confirm_password": "Confirm password",
        "hostname": "Computer name",
        "install": "Install",
        "back": "Back",
        "next": "Next",
        "cancel": "Cancel",
        "progress": "Installing FlasterOS. Do not power off the computer.",
        "done": "Installation complete. Reboot and remove the USB drive.",
        "reboot": "Reboot now",
        "no_disk": "Select a target disk.",
        "bad_user": "Enter a valid Linux username. Do not use root.",
        "bad_host": "Enter a valid computer name.",
        "bad_password": "Password must be at least 6 characters, must not contain ':', and both password fields must match.",
        "confirm": "This will permanently delete all data on {disk}. Continue?",
        "failed": "Installation failed. Review the log below.",
    },
    "ru": {
        "title": "\u0423\u0441\u0442\u0430\u043d\u043e\u0432\u043a\u0430 FlasterOS",
        "language": "\u042f\u0437\u044b\u043a",
        "language_text": "\u0412\u044b\u0431\u0435\u0440\u0438\u0442\u0435 \u044f\u0437\u044b\u043a \u0443\u0441\u0442\u0430\u043d\u043e\u0432\u0449\u0438\u043a\u0430.",
        "disk": "\u0414\u0438\u0441\u043a",
        "disk_text": "\u0412\u044b\u0431\u0435\u0440\u0438\u0442\u0435 \u0434\u0438\u0441\u043a \u0434\u043b\u044f \u0443\u0441\u0442\u0430\u043d\u043e\u0432\u043a\u0438 FlasterOS.",
        "refresh": "\u041e\u0431\u043d\u043e\u0432\u0438\u0442\u044c",
        "warning": "\u0412\u0441\u0435 \u0434\u0430\u043d\u043d\u044b\u0435 \u043d\u0430 \u0432\u044b\u0431\u0440\u0430\u043d\u043d\u043e\u043c \u0434\u0438\u0441\u043a\u0435 \u0431\u0443\u0434\u0443\u0442 \u0443\u0434\u0430\u043b\u0435\u043d\u044b.",
        "scheme": "\u0421\u0445\u0435\u043c\u0430 \u0440\u0430\u0437\u0434\u0435\u043b\u043e\u0432: EFI, /, /home",
        "user": "\u041f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u0435\u043b\u044c",
        "username": "\u0418\u043c\u044f \u043f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u0435\u043b\u044f",
        "password": "\u041f\u0430\u0440\u043e\u043b\u044c",
        "confirm_password": "\u041f\u043e\u0432\u0442\u043e\u0440 \u043f\u0430\u0440\u043e\u043b\u044f",
        "hostname": "\u0418\u043c\u044f \u043a\u043e\u043c\u043f\u044c\u044e\u0442\u0435\u0440\u0430",
        "install": "\u0423\u0441\u0442\u0430\u043d\u043e\u0432\u0438\u0442\u044c",
        "back": "\u041d\u0430\u0437\u0430\u0434",
        "next": "\u0414\u0430\u043b\u0435\u0435",
        "cancel": "\u041e\u0442\u043c\u0435\u043d\u0430",
        "progress": "\u0418\u0434\u0435\u0442 \u0443\u0441\u0442\u0430\u043d\u043e\u0432\u043a\u0430 FlasterOS. \u041d\u0435 \u0432\u044b\u043a\u043b\u044e\u0447\u0430\u0439\u0442\u0435 \u043a\u043e\u043c\u043f\u044c\u044e\u0442\u0435\u0440.",
        "done": "\u0423\u0441\u0442\u0430\u043d\u043e\u0432\u043a\u0430 \u0437\u0430\u0432\u0435\u0440\u0448\u0435\u043d\u0430. \u041f\u0435\u0440\u0435\u0437\u0430\u0433\u0440\u0443\u0437\u0438\u0442\u0435\u0441\u044c \u0438 \u0438\u0437\u0432\u043b\u0435\u043a\u0438\u0442\u0435 USB-\u043d\u0430\u043a\u043e\u043f\u0438\u0442\u0435\u043b\u044c.",
        "reboot": "\u041f\u0435\u0440\u0435\u0437\u0430\u0433\u0440\u0443\u0437\u0438\u0442\u044c",
        "no_disk": "\u0412\u044b\u0431\u0435\u0440\u0438\u0442\u0435 \u0446\u0435\u043b\u0435\u0432\u043e\u0439 \u0434\u0438\u0441\u043a.",
        "bad_user": "\u0412\u0432\u0435\u0434\u0438\u0442\u0435 \u043a\u043e\u0440\u0440\u0435\u043a\u0442\u043d\u043e\u0435 \u0438\u043c\u044f \u043f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u0435\u043b\u044f Linux. \u041d\u0435 \u0438\u0441\u043f\u043e\u043b\u044c\u0437\u0443\u0439\u0442\u0435 root.",
        "bad_host": "\u0412\u0432\u0435\u0434\u0438\u0442\u0435 \u043a\u043e\u0440\u0440\u0435\u043a\u0442\u043d\u043e\u0435 \u0438\u043c\u044f \u043a\u043e\u043c\u043f\u044c\u044e\u0442\u0435\u0440\u0430.",
        "bad_password": "\u041f\u0430\u0440\u043e\u043b\u044c \u0434\u043e\u043b\u0436\u0435\u043d \u0431\u044b\u0442\u044c \u043d\u0435 \u043a\u043e\u0440\u043e\u0447\u0435 6 \u0441\u0438\u043c\u0432\u043e\u043b\u043e\u0432, \u043d\u0435 \u0434\u043e\u043b\u0436\u0435\u043d \u0441\u043e\u0434\u0435\u0440\u0436\u0430\u0442\u044c ':', \u043e\u0431\u0430 \u043f\u043e\u043b\u044f \u0434\u043e\u043b\u0436\u043d\u044b \u0441\u043e\u0432\u043f\u0430\u0434\u0430\u0442\u044c.",
        "confirm": "\u0412\u0441\u0435 \u0434\u0430\u043d\u043d\u044b\u0435 \u043d\u0430 {disk} \u0431\u0443\u0434\u0443\u0442 \u0431\u0435\u0437\u0432\u043e\u0437\u0432\u0440\u0430\u0442\u043d\u043e \u0443\u0434\u0430\u043b\u0435\u043d\u044b. \u041f\u0440\u043e\u0434\u043e\u043b\u0436\u0438\u0442\u044c?",
        "failed": "\u0423\u0441\u0442\u0430\u043d\u043e\u0432\u043a\u0430 \u043d\u0435 \u0443\u0434\u0430\u043b\u0430\u0441\u044c. \u041f\u0440\u043e\u0432\u0435\u0440\u044c\u0442\u0435 \u0436\u0443\u0440\u043d\u0430\u043b \u043d\u0438\u0436\u0435.",
    },
}


def run_command(args):
    return subprocess.run(args, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)


class Installer(tk.Tk):
    def __init__(self):
        super().__init__()
        self.lang = tk.StringVar(value="en")
        self.selected_disk = tk.StringVar()
        self.username = tk.StringVar(value="ard")
        self.hostname = tk.StringVar(value="ard-os")
        self.password = tk.StringVar()
        self.password_confirm = tk.StringVar()
        self.step = 0
        self.disks = []
        self.install_running = False

        self.title(TEXT["en"]["title"])
        self.geometry("760x560")
        self.minsize(680, 500)

        self.header = ttk.Label(self, font=("TkDefaultFont", 18, "bold"))
        self.header.pack(anchor=tk.W, padx=20, pady=(18, 8))

        self.body = ttk.Frame(self)
        self.body.pack(fill=tk.BOTH, expand=True, padx=20, pady=8)

        self.nav = ttk.Frame(self)
        self.nav.pack(fill=tk.X, padx=20, pady=(8, 18))
        self.back_button = ttk.Button(self.nav, command=self.back)
        self.back_button.pack(side=tk.LEFT)
        self.cancel_button = ttk.Button(self.nav, command=self.destroy)
        self.cancel_button.pack(side=tk.RIGHT)
        self.next_button = ttk.Button(self.nav, command=self.next)
        self.next_button.pack(side=tk.RIGHT, padx=(0, 8))

        self.show_step()

    def t(self, key):
        return TEXT[self.lang.get()][key]

    def clear_body(self):
        for child in self.body.winfo_children():
            child.destroy()

    def show_step(self):
        self.clear_body()
        self.title(self.t("title"))
        self.header.configure(text=self.t(["language", "disk", "user", "install"][self.step]))
        self.back_button.configure(text=self.t("back"), state=tk.NORMAL if self.step > 0 and not self.install_running else tk.DISABLED)
        self.cancel_button.configure(text=self.t("cancel"), state=tk.DISABLED if self.install_running else tk.NORMAL)
        self.next_button.configure(text=self.t("next") if self.step < 3 else self.t("install"))

        if self.step == 0:
            self.show_language()
        elif self.step == 1:
            self.show_disk()
        elif self.step == 2:
            self.show_user()
        else:
            self.show_install()

    def show_language(self):
        ttk.Label(self.body, text=self.t("language_text")).pack(anchor=tk.W, pady=(0, 12))
        ttk.Radiobutton(self.body, text="English", variable=self.lang, value="en", command=self.show_step).pack(anchor=tk.W, pady=4)
        ttk.Radiobutton(self.body, text="\u0420\u0443\u0441\u0441\u043a\u0438\u0439", variable=self.lang, value="ru", command=self.show_step).pack(anchor=tk.W, pady=4)

    def load_disks(self):
        self.disks = []
        result = run_command(["lsblk", "-J", "-b", "-dn", "-o", "NAME,SIZE,MODEL,TYPE,RM"])
        try:
            devices = json.loads(result.stdout).get("blockdevices", [])
        except json.JSONDecodeError:
            devices = []
        for item in devices:
            name = item.get("name", "")
            size = int(item.get("size") or 0)
            model = item.get("model") or "Unknown model"
            dtype = item.get("type", "")
            removable = item.get("rm", False)
            if dtype != "disk":
                continue
            size_gib = size / 1024 / 1024 / 1024
            device = f"/dev/{name}"
            label = f"{device}  {size_gib:.1f} GiB  {model}  removable={removable}"
            self.disks.append((device, label))

    def show_disk(self):
        if not self.disks:
            self.load_disks()
        ttk.Label(self.body, text=self.t("disk_text")).pack(anchor=tk.W, pady=(0, 8))
        ttk.Label(self.body, text=self.t("warning"), foreground="#a40000").pack(anchor=tk.W, pady=(0, 8))
        ttk.Label(self.body, text=self.t("scheme")).pack(anchor=tk.W, pady=(0, 12))
        list_frame = ttk.Frame(self.body)
        list_frame.pack(fill=tk.BOTH, expand=True)
        for device, label in self.disks:
            ttk.Radiobutton(list_frame, text=label, variable=self.selected_disk, value=device).pack(anchor=tk.W, pady=3)
        ttk.Button(self.body, text=self.t("refresh"), command=self.refresh_disks).pack(anchor=tk.W, pady=(12, 0))

    def refresh_disks(self):
        self.load_disks()
        self.show_step()

    def show_user(self):
        form = ttk.Frame(self.body)
        form.pack(anchor=tk.NW, fill=tk.X)
        fields = [
            (self.t("username"), self.username, False),
            (self.t("password"), self.password, True),
            (self.t("confirm_password"), self.password_confirm, True),
            (self.t("hostname"), self.hostname, False),
        ]
        for row, (label, var, secret) in enumerate(fields):
            ttk.Label(form, text=label).grid(row=row, column=0, sticky=tk.W, pady=7, padx=(0, 12))
            entry = ttk.Entry(form, textvariable=var, show="*" if secret else "")
            entry.grid(row=row, column=1, sticky=tk.EW, pady=7)
        form.columnconfigure(1, weight=1)

    def show_install(self):
        summary = ttk.Frame(self.body)
        summary.pack(fill=tk.X, pady=(0, 16))
        rows = [
            (self.t("language"), "\u0420\u0443\u0441\u0441\u043a\u0438\u0439" if self.lang.get() == "ru" else "English"),
            (self.t("disk"), self.selected_disk.get()),
            (self.t("username"), self.username.get()),
            (self.t("hostname"), self.hostname.get()),
            ("EFI", "1 GiB FAT32"),
            ("/", "btrfs"),
            ("/home", "btrfs"),
        ]
        for row, (key, value) in enumerate(rows):
            ttk.Label(summary, text=f"{key}:").grid(row=row, column=0, sticky=tk.W, pady=3, padx=(0, 10))
            ttk.Label(summary, text=value).grid(row=row, column=1, sticky=tk.W, pady=3)
        self.log = tk.Text(self.body, height=14, wrap=tk.WORD)
        self.log.pack(fill=tk.BOTH, expand=True)

    def validate_current(self):
        if self.step == 1 and not self.selected_disk.get():
            messagebox.showerror(self.t("title"), self.t("no_disk"), parent=self)
            return False
        if self.step == 2:
            if self.username.get() == "root" or not USERNAME_RE.match(self.username.get()):
                messagebox.showerror(self.t("title"), self.t("bad_user"), parent=self)
                return False
            if not HOSTNAME_RE.match(self.hostname.get()):
                messagebox.showerror(self.t("title"), self.t("bad_host"), parent=self)
                return False
            if len(self.password.get()) < MIN_PASSWORD_LEN or ":" in self.password.get() or self.password.get() != self.password_confirm.get():
                messagebox.showerror(self.t("title"), self.t("bad_password"), parent=self)
                return False
        return True

    def next(self):
        if self.install_running:
            return
        if not self.validate_current():
            return
        if self.step < 3:
            self.step += 1
            self.show_step()
            return
        self.start_install()

    def back(self):
        if self.step > 0 and not self.install_running:
            self.step -= 1
            self.show_step()

    def append_log(self, text):
        self.log.insert(tk.END, text)
        self.log.see(tk.END)

    def start_install(self):
        disk = self.selected_disk.get()
        if not messagebox.askyesno(self.t("title"), self.t("confirm").format(disk=disk), parent=self):
            return
        self.install_running = True
        self.back_button.configure(state=tk.DISABLED)
        self.cancel_button.configure(state=tk.DISABLED)
        self.next_button.configure(state=tk.DISABLED)
        self.append_log(self.t("progress") + "\n\n")
        threading.Thread(target=self.run_install, daemon=True).start()

    def run_install(self):
        password_path = None
        try:
            fd, password_path = tempfile.mkstemp(prefix="ard-install-password-")
            os.close(fd)
            Path(password_path).write_text(self.password.get(), encoding="utf-8")
            os.chmod(password_path, 0o600)
            locale = "ru_RU.UTF-8" if self.lang.get() == "ru" else "en_US.UTF-8"
            cmd = [
                "sudo", "-n", "ard-install",
                "--disk", self.selected_disk.get(),
                "--hostname", self.hostname.get(),
                "--username", self.username.get(),
                "--locale", locale,
                "--password-file", password_path,
                "--confirm-erase",
            ]
            process = subprocess.Popen(cmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            assert process.stdout
            for line in process.stdout:
                self.after(0, self.append_log, line)
            code = process.wait()
            if code == 0:
                self.after(0, self.install_done)
            else:
                self.after(0, self.install_failed)
        except Exception as exc:
            self.after(0, self.append_log, f"\n{exc}\n")
            self.after(0, self.install_failed)
        finally:
            if password_path:
                try:
                    os.remove(password_path)
                except OSError:
                    pass

    def install_done(self):
        self.install_running = False
        self.append_log("\n" + self.t("done") + "\n")
        self.next_button.configure(text=self.t("reboot"), state=tk.NORMAL, command=self.reboot)

    def install_failed(self):
        self.install_running = False
        self.append_log("\n" + self.t("failed") + "\n")
        self.cancel_button.configure(state=tk.NORMAL)

    def reboot(self):
        subprocess.Popen(["systemctl", "reboot"])


if __name__ == "__main__":
    Installer().mainloop()
