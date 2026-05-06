#!/usr/bin/env bash
set -euo pipefail

systemctl enable NetworkManager.service
systemctl enable sddm.service

useradd -m -G wheel -s /bin/bash ard
passwd -d ard

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
cat > /home/ard/Desktop/ard-install.desktop <<'EOF'
[Desktop Entry]
Type=Application
Name=Install Ard OS
Comment=Install Ard OS base system to disk
Exec=konsole -e sudo ard-install
Icon=system-software-install
Terminal=false
Categories=System;
EOF
chmod 0755 /home/ard/Desktop/ard-install.desktop
chown -R ard:ard /home/ard

printf 'ard-live\n' > /etc/hostname
