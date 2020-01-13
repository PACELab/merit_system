rsync -avzP -e "ssh -i /users/Jasim9/compass.key" ubuntu@130.245.168.179:~/data/images*.tar.gz ~/img-data/
#rsync -avzP -e "ssh -i /users/Jasim9/graybox.pem" Jasim9@clnode038.clemson.cloudlab.us:~/img-data/images*.tar.gz ~/img-data/
tar -xzvf ~/img-data/images*.tar.gz -C ~/img-data/
#openstack image create "vServer" --disk-format qcow2 --public --container-format bare --file ~/img-data/vServer.img
#openstack image create "Firewall" --disk-format qcow2 --public --container-format bare --file ~/img-data/Firewall.img
openstack image create "vClient" --disk-format qcow2 --public --container-format bare --file ~/img-data/vClient.img
#openstack image create "Router" --disk-format qcow2 --public --container-format bare --file ~/img-data/Router2.img
openstack image create "Trusty_cloudserver" --disk-format qcow2 --public --container-format bare --file ~/img-data/trusty-server-cloudimg-amd64-disk1.img
openstack image create "Bionic_cloudserver" --disk-format qcow2 --public --container-format bare --file ~/img-data/bionic-server-cloudimg-amd64.img

openstack image create "test0_snap" --disk-format qcow2 --public --container-format bare --file ~/img-data/trusty-server-cloudimg-amd64-disk1.img
openstack image create "test1_snap" --disk-format qcow2 --public --container-format bare --file ~/img-data/test1_snap.img
openstack image create "test2_snap" --disk-format qcow2 --public --container-format bare --file ~/img-data/test2_snap.img
openstack image create "test3_snap" --disk-format qcow2 --public --container-format bare --file ~/img-data/test3_snap.img
openstack image create "test4_snap" --disk-format qcow2 --public --container-format bare --file ~/img-data/test4_snap.img

openstack image create "Server_snap" --disk-format qcow2 --public --container-format bare --file ~/img-data/trusty-server-cloudimg-amd64-disk1.img
openstack image create "Router_snap" --disk-format qcow2 --public --container-format bare --file ~/img-data/trusty-server-cloudimg-amd64-disk1.img
openstack image create "memcached" --disk-format qcow2 --public --container-format bare --file ~/img-data/memcached.img
openstack image create "Snort_IDS" --disk-format qcow2 --public --container-format bare --file ~/img-data/snort_ids.img
openstack image create "Apache_ATS" --disk-format qcow2 --public --container-format bare --file ~/img-data/apache_ats.img
openstack image create "Bionic_DPDK" --disk-format qcow2 --public --container-format bare --file ~/img-data/bionic_dpdk.img

openstack security group rule create --ingress --dst-port 11211 --remote-ip 0.0.0.0/00 --project admin `openstack security group list --project admin | grep default | awk '{print $2}'`
openstack flavor create m1.mediumlarge --id 101 --ram 12288 --disk 120 --vcpus 6
openstack image list
