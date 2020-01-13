#!/bin/sh
# to be executed on the controller machine
#sh create_lvm_vol.sh
nbr_host=${1:-5}
sudo sed -i 's/\(10\.11.*\) cp-1-0/\1 cp-1-0\tgluster1/' /etc/hosts
#sudo sed -i 's/\(192\.168.*\) cp-2/\1 cp-2\tgluster2/' /etc/hosts
for i in $(seq 1 $nbr_host); do
	scp -o StrictHostKeyChecking=no -i graybox.pem edit_hosts.sh Jasim9@cp-${i}:~/
	ssh -o StrictHostKeyChecking=no -i graybox.pem Jasim9@cp-${i} 'sh edit_hosts.sh'
done
echo "Setting up Gluster node"
for i in 1 ; do
	scp -o StrictHostKeyChecking=no -i graybox.pem create_gluster_vol.sh install_gluster.sh config_gluster.sh Jasim9@gluster${i}:~/
	ssh -i graybox.pem Jasim9@gluster${i} 'sh install_gluster.sh'
	ssh -i graybox.pem Jasim9@gluster${i} 'sh create_gluster_vol.sh'
done
ssh -i graybox.pem Jasim9@gluster1 'sh config_gluster.sh'
for i in $(seq 1 $nbr_host); do
	scp -i graybox.pem mount_gluster.sh config_libvirt.sh graybox.pem modify_qemu.sh get_pdr.py config_qemu*.sh config_novaLM.sh install_monitoring.sh qemu_monitor.py config_max_downtime_lm.sh start_*.sh ~/wondershaper/wondershaper Jasim9@cp-${i}:~/
	echo "Setting up node "${i}
	ssh -i graybox.pem Jasim9@cp-${i} 'sudo service nova-compute stop'
	ssh -i graybox.pem Jasim9@cp-${i} 'sh mount_gluster.sh'
	ssh -i graybox.pem Jasim9@cp-${i} 'sh config_libvirt.sh'
	ssh -i graybox.pem Jasim9@cp-${i} 'sh config_max_downtime_lm.sh'
	ssh -i graybox.pem Jasim9@cp-${i} 'sudo service nova-compute start'
done

