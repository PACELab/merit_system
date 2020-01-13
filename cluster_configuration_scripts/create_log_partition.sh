#!/bin/bash
#sudo fdisk -l
#(
#echo n # Add a new partition
#echo p # Primary partition
#echo 1 # Partition number
#echo   # First sector (Accept default: 1)
#echo   # Last sector (Accept default: varies)
#echo w # Write changes
#) | sudo fdisk /dev/sdb
#sudo mkfs.ext4 /dev/sdb1

sudo mkdir -p /data/backup
#sudo mount /dev/sdb1 /data/backup
#echo "/dev/sdb1 /data/backup ext4 defaults 0 0" | sudo tee --append /etc/fstab

sudo lvcreate -L 80G -n logs-lv openstack-volumes
sudo mkfs.ext4 /dev/openstack-volumes/logs-lv
sudo mount -t ext4 /dev/openstack-volumes/logs-lv /data/backup

sudo chown Jasim9:live-migrate-PG0 /data/backup

