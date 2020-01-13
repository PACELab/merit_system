sudo apt-get update
sudo DEBIAN_FRONTEND=noninteractive apt-get -y install moreutils collectl python-pip scons libevent-dev gengetopt g++ git
sudo pip install --upgrade python-novaclient
sudo pip install -U flask statistics scikit-learn
sudo cp /root/setup/admin-openrc.sh ~/
sudo cp ~/admin-openrc.sh ~/vnf-rehoming/
sudo chmod 600 ~/vnf-rehoming/graybox.pem
sudo chmod 600 ~/vnf-rehoming/compass.key
cp ~/vnf-rehoming/graybox.pem ~/
cp ~/vnf-rehoming/compass.key ~/
echo -e "Host *\nStrictHostKeyChecking no" | sudo tee ~/.ssh/config
source ~/admin-openrc.sh
git clone  https://github.com/magnific0/wondershaper.git ~/wondershaper
git clone https://github.com/leverich/mutilate.git ~/mutilate
cd ~/mutilate
scons
cd ~/vnf-rehoming
sh create_lvm_vol.sh
sh create_log_partition.sh
