#sudo gluster peer probe gluster2
#sudo gluster peer status
sudo gluster pool list
yes | sudo gluster volume create openstack-vol gluster1:/data/gluster/openstack-vol
sudo gluster volume start openstack-vol
sudo gluster volume info openstack-vol

