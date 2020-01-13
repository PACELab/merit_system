# this is for openstack to be executed on each compute node
sudo apt-get -y install glusterfs-client
sudo mount -t glusterfs gluster1:/openstack-vol /var/lib/nova/instances
#echo "gluster1:/openstack-vol /var/lib/nova/instances glusterfs defaults,_netdev 0 0" | sudo tee --append /etc/fstab
sudo chown -R nova:nova  /var/lib/nova/instances
