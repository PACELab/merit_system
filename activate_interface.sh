#!/bin/sh
# Shell Script to activate eth1 and eth2 interfaces on the newly migrated VNF

ssh -o StrictHostKeyChecking=no -i ~/graybox.pem ubuntu@${1} 'for i in 1 2 ; do echo -e $"auto eth"${i}"\niface eth"${i}" inet dhcp" | sudo tee /etc/network/interfaces.d/eth${i}.cfg ; sudo ifup eth${i} ; done'
