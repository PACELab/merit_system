for i in 0 1 2 3 4 5 ; do
	neutron net-create mnic-${i}
	neutron subnet-create mnic-${i} --enable-dhcp --no-gateway --name msub-${i} 10.10.${i}.1/24
done
