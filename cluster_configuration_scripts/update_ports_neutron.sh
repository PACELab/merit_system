for i in `neutron port-list | grep "\"10.10." | awk '{print $2}'` ; do neutron port-update ${i} --allowed-address-pairs type=dict list=true ip_address=10.10.1.1/16 ; done
