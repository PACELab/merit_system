#sudo apt-get update && sudo apt-get -y install git libglib2.0-dev libfdt-dev libpixman-1-dev zlib1g-dev
#git clone --single-branch --branch profiler https://github.com/changyeon/qemu.git ~/qemu
#cd ~/qemu
#sed -i 's/QEMU_CFLAGS="-Werror=format-truncation=0 $QEMU_CFLAGS"/#QEMU_CFLAGS="-Werror=format-truncation=0 $QEMU_CFLAGS"/' ~/qemu/configure
#./configure --target-list=x86_64-softmmu
#make -j9
sudo mv /usr/bin/qemu-system-x86_64 ~/qemu-system-x86_64_backup
scp -o StrictHostKeyChecking=no -i ~/graybox.pem ctl:~/vnf-rehoming/qemu-system-x86_64 ~/qemu_modified
sudo cp ~/qemu_modified /usr/bin/qemu-system-x86_64
sudo sed -i '/hw_machine_type = /a  hw_machine_type = x86_64=pc-i440fx-2.8' /etc/nova/nova.conf
sudo ln -sf /usr/share/seabios/bios-256k.bin /usr/share/qemu/bios-256k.bin
sudo ln -sf /usr/share/seabios/kvmvapic.bin /usr/share/qemu/kvmvapic.bin
sudo ln -sf /usr/lib/ipxe/qemu/efi-virtio.rom /usr/share/qemu/efi-virtio.rom
sudo ln -sf /usr/share/seabios/vgabios-cirrus.bin /usr/share/qemu/vgabios-cirrus.bin
sudo service nova-compute restart
