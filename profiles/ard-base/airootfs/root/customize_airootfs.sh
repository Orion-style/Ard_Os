#!/usr/bin/env bash
set -euo pipefail

systemctl enable NetworkManager.service
systemctl enable sddm.service
systemctl enable power-profiles-daemon.service || true
systemctl enable bluetooth.service || true
systemctl enable qemu-guest-agent.service || true
systemctl enable vboxservice.service || true

chmod 0755 /usr/local/bin/ard-installer /usr/local/bin/ard-settings-center /usr/local/bin/ard-check-system /usr/local/bin/ard-snapshot
chmod 0755 /opt/ard-os/installer/ard-installer.py /opt/ard-os/settings/ard-settings-center.py /opt/ard-os/diagnostics/ard-diagnostics.py

useradd -m -G wheel -s /bin/bash ard
passwd -d ard

install -d -m 0755 /opt/ard-os
install -d -m 0775 -o ard -g wheel /games
install -d -m 0755 /var/log/ard-os

printf 'ard ALL=(ALL:ALL) NOPASSWD: ALL\n' > /etc/sudoers.d/10-ard-live
chmod 0440 /etc/sudoers.d/10-ard-live

mkdir -p /etc/sddm.conf.d
cat > /etc/sddm.conf.d/10-ard-autologin.conf <<'EOF'
[Autologin]
User=ard
Session=plasma.desktop
Relogin=true
EOF

mkdir -p /home/ard/Desktop
cp /usr/share/applications/ard-installer.desktop /home/ard/Desktop/ard-installer.desktop

cp /usr/share/applications/ard-launcher.desktop /home/ard/Desktop/ard-launcher.desktop
cp /usr/share/applications/ard-settings-center.desktop /home/ard/Desktop/ard-settings-center.desktop
cp /usr/share/applications/ard-diagnostics.desktop /home/ard/Desktop/ard-diagnostics.desktop
chmod 0755 /home/ard/Desktop/ard-installer.desktop
chmod 0755 /home/ard/Desktop/ard-launcher.desktop
chmod 0755 /home/ard/Desktop/ard-settings-center.desktop
chmod 0755 /home/ard/Desktop/ard-diagnostics.desktop
chown -R ard:ard /home/ard

printf 'ard-live\n' > /etc/hostname

plymouth-set-default-theme flasteros || true
