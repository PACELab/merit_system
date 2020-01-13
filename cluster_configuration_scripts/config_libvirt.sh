sudo sed -i 's/#*listen_tls/listen_tls/' /etc/libvirt/libvirtd.conf
sudo sed -i 's/#*listen_tcp/listen_tcp/' /etc/libvirt/libvirtd.conf
sudo sed -i 's/#*auth_tcp = .*/auth_tcp = "none"/' /etc/libvirt/libvirtd.conf
sudo sed -i 's/#*libvirtd_opts=.*/libvirtd_opts = "-l"/' /etc/default/libvirtd
#sudo echo -e "[libvirt]\nlive_migration_flag=VIR_MIGRATE_UNDEFINE_SOURCE,VIR_MIGRATE_PEER2PEER,VIR_MIGRATE_LIVE" | sudo tee -a /etc/nova/nova.conf
#sudo sed -i '/#user/a user="root"' /etc/libvirt/qemu.conf
#sudo sed -i '/#group/a group="root"' /etc/libvirt/qemu.conf
#sudo sed -i '/#dynamic_ownership/a dynamic_ownership=0' /etc/libvirt/qemu.conf
#sudo sed -i 's/user=".*"/user="root"/g' /etc/libvirt/qemu.conf
#sudo sed -i 's/group=".*"/group="root"/g' /etc/libvirt/qemu.conf
sudo sed -i "s/#live_migration_downtime_steps = /live_migration_downtime_steps = /" /etc/nova/nova.conf
sudo sed -i "s/#live_migration_downtime = /live_migration_downtime = /" /etc/nova/nova.conf
sudo sed -i "s/#live_migration_downtime_delay = /live_migration_downtime_delay = /" /etc/nova/nova.conf
sudo sed -i 's/#dynamic_ownership = [0-1]/dynamic_ownership = 1/g' /etc/libvirt/qemu.conf
sudo service libvirtd restart
