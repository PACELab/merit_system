nlout=$(nova list)
cip=$(echo "$nlout" | grep Client | sed -r 's/.*flat-lan.*=(10.11.[0-9]*.[0-9]*).*/\1/')
sip=$(echo "$nlout" | grep Server | sed -r 's/.*flat-lan.*=(10.11.[0-9]*.[0-9]*).*/\1/')
rtip=$(echo "$nlout" | grep Router2 | sed -r 's/.*flat-lan.*=(10.11.[0-9]*.[0-9]*).*/\1/')
fwip=$(echo "$nlout" | grep Firewall | sed -r 's/.*flat-lan.*=(10.11.[0-9]*.[0-9]*).*/\1/')

r1ip=$(echo "$nlout" | grep Router2 | sed -r 's/.*mnic-1=([0-9]*.[0-9]*.[0-9]*.[0-9]*).*/\1/')
r2ip=$(echo "$nlout" | grep Router2 | sed -r 's/.*mnic-2=([0-9]*.[0-9]*.[0-9]*.[0-9]*).*/\1/')
f2ip=$(echo "$nlout" | grep Firewall | sed -r 's/.*mnic-2=([0-9]*.[0-9]*.[0-9]*.[0-9]*).*/\1/')
f3ip=$(echo "$nlout" | grep Firewall | sed -r 's/.*mnic-3=([0-9]*.[0-9]*.[0-9]*.[0-9]*).*/\1/')


ssh -o StrictHostKeyChecking=no -i ~/graybox.pem ubuntu@${cip} 'for i in 1 ; do echo -e $"auto eth"${i}"\niface eth"${i}" inet dhcp" | sudo tee /etc/network/interfaces.d/eth${i}.cfg ; sudo ifup eth${i} ; done'
ssh -o StrictHostKeyChecking=no -i ~/graybox.pem ubuntu@${rtip} 'for i in 1 2 ; do echo -e $"auto eth"${i}"\niface eth"${i}" inet dhcp" | sudo tee /etc/network/interfaces.d/eth${i}.cfg ; sudo ifup eth${i} ; done'
ssh -o StrictHostKeyChecking=no -i ~/graybox.pem ubuntu@${fwip} 'for i in 1 2 ; do echo -e $"auto eth"${i}"\niface eth"${i}" inet dhcp" | sudo tee /etc/network/interfaces.d/eth${i}.cfg ; sudo ifup eth${i} ; done'
ssh -o StrictHostKeyChecking=no -i ~/graybox.pem ubuntu@${sip} 'for i in 1 ; do echo -e $"auto eth"${i}"\niface eth"${i}" inet dhcp" | sudo tee /etc/network/interfaces.d/eth${i}.cfg ; sudo ifup eth${i} ; done'

ssh -o StrictHostKeyChecking=no -i ~/graybox.pem ubuntu@${cip} "sudo ip route del 10.10.2.0/23"
ssh -o StrictHostKeyChecking=no -i ~/graybox.pem ubuntu@${rtip} "sudo ip route del 10.10.3.0/24"
ssh -o StrictHostKeyChecking=no -i ~/graybox.pem ubuntu@${fwip} "sudo ip route del 10.10.1.0/24"
ssh -o StrictHostKeyChecking=no -i ~/graybox.pem ubuntu@${sip} "sudo ip route del 10.10.2.0/24"
ssh -o StrictHostKeyChecking=no -i ~/graybox.pem ubuntu@${sip} "sudo ip route del 10.10.1.0/24"

ssh -o StrictHostKeyChecking=no -i ~/graybox.pem ubuntu@${cip} "sudo ip route add 10.10.2.0/23 via ${r1ip}"
ssh -o StrictHostKeyChecking=no -i ~/graybox.pem ubuntu@${rtip} "sudo ip route add 10.10.3.0/24 via ${f2ip}"
ssh -o StrictHostKeyChecking=no -i ~/graybox.pem ubuntu@${fwip} "sudo ip route add 10.10.1.0/24 via ${r2ip}"
ssh -o StrictHostKeyChecking=no -i ~/graybox.pem ubuntu@${sip} "sudo ip route add 10.10.2.0/24 via ${f3ip}"
ssh -o StrictHostKeyChecking=no -i ~/graybox.pem ubuntu@${sip} "sudo ip route add 10.10.1.0/24 via ${f3ip}"

ssh -o StrictHostKeyChecking=no -i ~/graybox.pem ubuntu@${rtip} "sudo sysctl -w net.ipv4.ip_forward=1"
ssh -o StrictHostKeyChecking=no -i ~/graybox.pem ubuntu@${fwip} "sudo sysctl -w net.ipv4.ip_forward=1"
