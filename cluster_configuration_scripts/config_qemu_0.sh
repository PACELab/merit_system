#sudo sed -i 's/#user = ".*"/user = "root"/g' /etc/libvirt/qemu.conf
#sudo sed -i 's/#group = ".*"/group = "root"/g' /etc/libvirt/qemu.conf
sudo sed -i 's/dynamic_ownership = [0-1]/dynamic_ownership = 0/g' /etc/libvirt/qemu.conf
sudo service libvirtd restart
sudo service nova-compute restart
