sudo lvcreate -W y -L 180G -n gluster-lv openstack-volumes
sudo mkfs.ext4 /dev/openstack-volumes/gluster-lv
sudo mkdir -p /data/gluster
sudo mount -t ext4 /dev/openstack-volumes/gluster-lv /data/gluster/
df -h
sudo mkdir -p /data/gluster/openstack-vol
