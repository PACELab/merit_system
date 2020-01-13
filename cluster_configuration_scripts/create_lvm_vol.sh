#!/bin/sh
#sudo lvremove -y openstack-volumes/openstack-volumes-pool
sudo lvcreate -L 60G -n img-data-lv openstack-volumes
sudo mkfs.ext4 /dev/openstack-volumes/img-data-lv
mkdir ~/img-data
sudo mount -t ext4 /dev/openstack-volumes/img-data-lv ~/img-data/
sudo chown -R Jasim9:live-migrate-PG0 ~/img-data/
df -h
#df -h /var/lib/glance/images/
#sudo lvcreate -L 300G -n glance-lv openstack-volumes
#sudo mkfs.ext3 /dev/openstack-volumes/glance-lv
#sudo mkdir /mnt/tmpglance
#sudo mount -t ext3 /dev/openstack-volumes/glance-lv /mnt/tmpglance/
#df -h
#sudo mv /var/lib/glance/images/* /mnt/tmpglance/
#sudo umount /dev/openstack-volumes/glance-lv
#sudo mount -t ext3 /dev/openstack-volumes/glance-lv /var/lib/glance/images/
#sudo chown -R glance:glance /var/lib/glance/images/

#sudo lvcreate -L 200G -n logs-lv openstack-volumes
#sudo mkfs.ext3 /dev/openstack-volumes/logs-lv
#sudo mkdir /mnt/tmplogs
#sudo mount -t ext3 /dev/openstack-volumes/logs-lv /mnt/tmplogs/
#df -h
#sudo mv /var/log/* /mnt/tmplogs/
#sudo umount /dev/openstack-volumes/logs-lv
#sudo mount -t ext3 /dev/openstack-volumes/logs-lv /var/log/

