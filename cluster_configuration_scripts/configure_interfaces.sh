#!/bin/bash
# configure interfaces (eth form)
# execute on the VM,
ip link show | grep eth[0-9] | awk '{print $2}' | sed 's/:$//' | while read i ; do if [ ! -f /etc/network/interfaces.d/${i}.cfg ] ; then echo -e $"auto "${i}"\niface "${i}" inet dhcp" | sudo tee /etc/network/interfaces.d/${i}.cfg ; sudo ifup ${i} ; else echo "Already configured"; fi ; done
