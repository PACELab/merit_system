# needs another network - fix
n0id=`openstack network list | grep 'mnic-0' | awk '{print $2}'`
n1id=`openstack network list | grep 'mnic-1' | awk '{print $2}'`
n2id=`openstack network list | grep 'mnic-2' | awk '{print $2}'`
n3id=`openstack network list | grep 'mnic-3' | awk '{print $2}'`
n4id=`openstack network list | grep 'mnic-4' | awk '{print $2}'`
n5id=`openstack network list | grep 'mnic-5' | awk '{print $2}'`
flanid=`openstack network list | grep 'flat' | awk '{print $2}'`
domain=$(nova hypervisor-list | grep enabled | head -1 | awk '{print $4}' | cut -d '.' -f 2-)
sufix=$1
nova boot "vClient"${sufix} --image `openstack image list | grep Client | awk '{print $2}'` --flavor m1.large --nic net-id=${flanid} --nic net-id=${n0id} --key Jasim9-mwajahatXqosXXX --availability-zone nova:cp-1.${domain}
sleep 60
nova boot "vServer"${sufix} --image `openstack image list | grep Trusty | awk '{print $2}'` --flavor m1.medium --nic net-id=${flanid} --nic net-id=${n4id} --key Jasim9-mwajahatXqosXXX --availability-zone nova:cp-1.${domain}
sleep 60
nova boot "wServer"${sufix} --image `openstack image list | grep Trusty | awk '{print $2}'` --flavor m1.medium --nic net-id=${flanid} --nic net-id=${n4id} --key Jasim9-mwajahatXqosXXX --availability-zone nova:cp-1.${domain}
sleep 60
nova boot "Firewall"${sufix} --image `openstack image list | grep Trusty | awk '{print $2}'` --flavor m1.medium --nic net-id=${flanid} --nic net-id=${n1id} --nic net-id=${n2id} --key Jasim9-mwajahatXqosXXX --availability-zone nova:cp-2.${domain}
sleep 60
nova boot "PGW"${sufix} --image `openstack image list | grep Trusty | awk '{print $2}'` --flavor m1.small --nic net-id=${flanid} --nic net-id=${n1id} --nic net-id=${n0id} --key Jasim9-mwajahatXqosXXX --availability-zone nova:cp-5.${domain}
sleep 60
nova boot "IDS"${sufix} --image `openstack image list | grep Trusty | awk '{print $2}'` --flavor m1.medium --nic net-id=${flanid} --nic net-id=${n2id} --nic net-id=${n5id} --key Jasim9-mwajahatXqosXXX --availability-zone nova:cp-3.${domain}
sleep 60
nova boot "Switch"${sufix} --image `openstack image list | grep Trusty | awk '{print $2}'` --flavor m1.small --nic net-id=${flanid} --nic net-id=${n1id} --nic net-id=${n3id} --nic net-id=${n5id} --key Jasim9-mwajahatXqosXXX --availability-zone nova:cp-4.${domain}
sleep 60
nova boot "ATS"${sufix} --image `openstack image list | grep Trusty | awk '{print $2}'` --flavor m1.medium --nic net-id=${flanid} --nic net-id=${n4id} --nic net-id=${n3id} --key Jasim9-mwajahatXqosXXX --availability-zone nova:cp-7.${domain}
sleep 60
nova boot "FFM"${sufix} --image `openstack image list | grep Trusty | awk '{print $2}'` --flavor m1.medium --nic net-id=${flanid} --nic net-id=${n4id} --nic net-id=${n3id} --key Jasim9-mwajahatXqosXXX --availability-zone nova:cp-6.${domain}


#nova boot "test_instance1"${sufix} --image `openstack image list | grep test1 | awk '{print $2}'` --flavor m1.small --nic net-id=${flanid} --key Jasim9-mwajahatXqosXXX --availability-zone nova:cp-1.${domain}
#nova boot "test_instance2"${sufix} --image `openstack image list | grep test2 | awk '{print $2}'` --flavor m1.small --nic net-id=${flanid} --key Jasim9-mwajahatXqosXXX --availability-zone nova:cp-1.${domain}
#nova boot "test_instance3"${sufix} --image `openstack image list | grep test3 | awk '{print $2}'` --flavor m1.small --nic net-id=${flanid} --key Jasim9-mwajahatXqosXXX --availability-zone nova:cp-1.${domain}
#nova boot "test_instance4"${sufix} --image `openstack image list | grep test4 | awk '{print $2}'` --flavor m1.small --nic net-id=${flanid} --key Jasim9-mwajahatXqosXXX --availability-zone nova:cp-1.${domain}
#nova boot "test_instance5"${sufix} --image `openstack image list | grep test0 | awk '{print $2}'` --flavor m1.small --nic net-id=${flanid} --key Jasim9-mwajahatXqosXXX --availability-zone nova:cp-1.${domain}

