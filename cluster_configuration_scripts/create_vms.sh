n1id=`openstack network list | grep 'mnic-1' | awk '{print $2}'`
n2id=`openstack network list | grep 'mnic-2' | awk '{print $2}'`
n3id=`openstack network list | grep 'mnic-3' | awk '{print $2}'`
flanid=`openstack network list | grep 'flat' | awk '{print $2}'`
domain=$(nova hypervisor-list | grep enabled | head -1 | awk '{print $4}' | cut -d '.' -f 2-)
sufix=$1
nova boot "vClient"${sufix} --image `openstack image list | grep Client | awk '{print $2}'` --flavor m1.large --nic net-id=${flanid} --nic net-id=${n1id} --key Jasim9-mwajahatXqosXXX --availability-zone nova:cp-1.${domain}
sleep 60
nova boot "vServer"${sufix} --image `openstack image list | grep Trusty | awk '{print $2}'` --flavor m1.large --nic net-id=${flanid} --nic net-id=${n3id} --key Jasim9-mwajahatXqosXXX --availability-zone nova:cp-5.${domain}
sleep 60
nova boot "Firewall"${sufix} --image `openstack image list | grep Trusty | awk '{print $2}'` --flavor m1.medium --nic net-id=${flanid} --nic net-id=${n2id} --nic net-id=${n3id} --key Jasim9-mwajahatXqosXXX --availability-zone nova:cp-3.${domain}
sleep 60
nova boot "Router2"${sufix} --image `openstack image list | grep Trusty | awk '{print $2}'` --flavor m1.small --nic net-id=${flanid} --nic net-id=${n1id} --nic net-id=${n2id} --key Jasim9-mwajahatXqosXXX --availability-zone nova:cp-2.${domain}


#nova boot "test_instance1"${sufix} --image `openstack image list | grep test1 | awk '{print $2}'` --flavor m1.small --nic net-id=${flanid} --key Jasim9-mwajahatXqosXXX --availability-zone nova:cp-1.${domain}
#nova boot "test_instance2"${sufix} --image `openstack image list | grep test2 | awk '{print $2}'` --flavor m1.small --nic net-id=${flanid} --key Jasim9-mwajahatXqosXXX --availability-zone nova:cp-1.${domain}
#nova boot "test_instance3"${sufix} --image `openstack image list | grep test3 | awk '{print $2}'` --flavor m1.small --nic net-id=${flanid} --key Jasim9-mwajahatXqosXXX --availability-zone nova:cp-1.${domain}
#nova boot "test_instance4"${sufix} --image `openstack image list | grep test4 | awk '{print $2}'` --flavor m1.small --nic net-id=${flanid} --key Jasim9-mwajahatXqosXXX --availability-zone nova:cp-1.${domain}
#nova boot "test_instance5"${sufix} --image `openstack image list | grep test0 | awk '{print $2}'` --flavor m1.small --nic net-id=${flanid} --key Jasim9-mwajahatXqosXXX --availability-zone nova:cp-1.${domain}

