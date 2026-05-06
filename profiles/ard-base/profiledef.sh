#!/usr/bin/env bash

iso_name="ard-os"
iso_label="ARDOS_$(date +%Y%m)"
iso_publisher="Ard OS Project"
iso_application="Ard OS Base Live ISO"
iso_version="$(date +%Y.%m.%d)"
install_dir="ard"
buildmodes=('iso')
bootmodes=('bios.syslinux.mbr' 'bios.syslinux.eltorito' 'uefi-ia32.grub.esp' 'uefi-x64.grub.esp' 'uefi-ia32.grub.eltorito' 'uefi-x64.grub.eltorito')
arch="x86_64"
pacman_conf="pacman.conf"
airootfs_image_type="squashfs"
airootfs_image_tool_options=('-comp' 'zstd' '-Xcompression-level' '15')
file_permissions=(
  ["/etc/shadow"]="0:0:400"
  ["/root"]="0:0:750"
  ["/root/customize_airootfs.sh"]="0:0:755"
  ["/usr/local/bin/ard-install"]="0:0:755"
)
