sudo apt-get install -y software-properties-common
sudo add-apt-repository ppa:gluster/glusterfs-4.1 -y
sudo apt-get update
sudo DEBIAN_FRONTEND=noninteractive apt-get install -y glusterfs-server
sudo service glusterd start
sudo service glusterd status

