inp=${1:-1} # default of 1 - configure interfaces and enable forwarding
del=${2:-1} # default of 1 - delete, added by default always

nlout=$(nova list)
cip=$(echo "$nlout" | grep Client | sed -r 's/.*flat-lan.*=(10.11.[0-9]*.[0-9]*).*/\1/')
vsip=$(echo "$nlout" | grep vServer | sed -r 's/.*flat-lan.*=(10.11.[0-9]*.[0-9]*).*/\1/')
wsip=$(echo "$nlout" | grep wServer | sed -r 's/.*flat-lan.*=(10.11.[0-9]*.[0-9]*).*/\1/')
swip=$(echo "$nlout" | grep Switch | sed -r 's/.*flat-lan.*=(10.11.[0-9]*.[0-9]*).*/\1/')
fwip=$(echo "$nlout" | grep Firewall | sed -r 's/.*flat-lan.*=(10.11.[0-9]*.[0-9]*).*/\1/')
pgip=$(echo "$nlout" | grep PGW | sed -r 's/.*flat-lan.*=(10.11.[0-9]*.[0-9]*).*/\1/')
idsip=$(echo "$nlout" | grep IDS | sed -r 's/.*flat-lan.*=(10.11.[0-9]*.[0-9]*).*/\1/')
atsip=$(echo "$nlout" | grep ATS | sed -r 's/.*flat-lan.*=(10.11.[0-9]*.[0-9]*).*/\1/')
ffmip=$(echo "$nlout" | grep FFM | sed -r 's/.*flat-lan.*=(10.11.[0-9]*.[0-9]*).*/\1/')

pg0ip=$(echo "$nlout" | grep PGW | sed -r 's/.*mnic-0=([0-9]*.[0-9]*.[0-9]*.[0-9]*).*/\1/')
pg1ip=$(echo "$nlout" | grep PGW | sed -r 's/.*mnic-1=([0-9]*.[0-9]*.[0-9]*.[0-9]*).*/\1/')
echo "PGW IPs ${pg0ip} ${pg1ip}"
fw1ip=$(echo "$nlout" | grep Firewall | sed -r 's/.*mnic-1=([0-9]*.[0-9]*.[0-9]*.[0-9]*).*/\1/')
fw2ip=$(echo "$nlout" | grep Firewall | sed -r 's/.*mnic-2=([0-9]*.[0-9]*.[0-9]*.[0-9]*).*/\1/')
echo "FW IPs ${fw1ip} ${fw2ip}"
ids2ip=$(echo "$nlout" | grep IDS | sed -r 's/.*mnic-2=([0-9]*.[0-9]*.[0-9]*.[0-9]*).*/\1/')
ids5ip=$(echo "$nlout" | grep IDS | sed -r 's/.*mnic-5=([0-9]*.[0-9]*.[0-9]*.[0-9]*).*/\1/')
echo "IDS IPs ${ids2ip} ${ids5ip}"

sw1ip=$(echo "$nlout" | grep Switch | sed -r 's/.*mnic-1=([0-9]*.[0-9]*.[0-9]*.[0-9]*).*/\1/')
sw3ip=$(echo "$nlout" | grep Switch | sed -r 's/.*mnic-3=([0-9]*.[0-9]*.[0-9]*.[0-9]*).*/\1/')
sw5ip=$(echo "$nlout" | grep Switch | sed -r 's/.*mnic-5=([0-9]*.[0-9]*.[0-9]*.[0-9]*).*/\1/')
echo "SW IPs ${sw1ip} ${sw3ip} ${sw5ip}"

ats3ip=$(echo "$nlout" | grep ATS | sed -r 's/.*mnic-3=([0-9]*.[0-9]*.[0-9]*.[0-9]*).*/\1/')
ats4ip=$(echo "$nlout" | grep ATS | sed -r 's/.*mnic-4=([0-9]*.[0-9]*.[0-9]*.[0-9]*).*/\1/')
echo "ATS IPs ${ats3ip} ${ats4ip}"

ffm3ip=$(echo "$nlout" | grep FFM | sed -r 's/.*mnic-3=([0-9]*.[0-9]*.[0-9]*.[0-9]*).*/\1/')
ffm4ip=$(echo "$nlout" | grep FFM | sed -r 's/.*mnic-4=([0-9]*.[0-9]*.[0-9]*.[0-9]*).*/\1/')
echo "FFM IPs ${ffm3ip} ${ffm4ip}"
vs4ip=$(echo "$nlout" | grep vServer | sed -r 's/.*mnic-4=([0-9]*.[0-9]*.[0-9]*.[0-9]*).*/\1/')
ws4ip=$(echo "$nlout" | grep wServer | sed -r 's/.*mnic-4=([0-9]*.[0-9]*.[0-9]*.[0-9]*).*/\1/')
echo "Servers IPs ${vs4ip} ${ws4ip}"

if [ "$inp" -eq 2 ] ; then
	echo "Copying configuration script"
	scp -o StrictHostKeyChecking=no -i ~/graybox.pem ~/vnf-rehoming/configure_interfaces.sh ubuntu@${cip}:~/
	scp -o StrictHostKeyChecking=no -i ~/graybox.pem ~/vnf-rehoming/configure_interfaces.sh ubuntu@${vsip}:~/
	scp -o StrictHostKeyChecking=no -i ~/graybox.pem ~/vnf-rehoming/configure_interfaces.sh ubuntu@${wsip}:~/
	scp -o StrictHostKeyChecking=no -i ~/graybox.pem ~/vnf-rehoming/configure_interfaces.sh ubuntu@${swip}:~/
	scp -o StrictHostKeyChecking=no -i ~/graybox.pem ~/vnf-rehoming/configure_interfaces.sh ubuntu@${fwip}:~/
	scp -o StrictHostKeyChecking=no -i ~/graybox.pem ~/vnf-rehoming/configure_interfaces.sh ubuntu@${idsip}:~/
	scp -o StrictHostKeyChecking=no -i ~/graybox.pem ~/vnf-rehoming/configure_interfaces.sh ubuntu@${atsip}:~/
	scp -o StrictHostKeyChecking=no -i ~/graybox.pem ~/vnf-rehoming/configure_interfaces.sh ubuntu@${ffmip}:~/
	scp -o StrictHostKeyChecking=no -i ~/graybox.pem ~/vnf-rehoming/configure_interfaces.sh ubuntu@${pgip}:~/
fi

if [ "$inp" -ge 1 ] ; then
	ssh -o StrictHostKeyChecking=no -i ~/graybox.pem ubuntu@${cip} "bash configure_interfaces.sh"
	ssh -o StrictHostKeyChecking=no -i ~/graybox.pem ubuntu@${vsip} "bash configure_interfaces.sh"
	ssh -o StrictHostKeyChecking=no -i ~/graybox.pem ubuntu@${wsip} "bash configure_interfaces.sh"
	ssh -o StrictHostKeyChecking=no -i ~/graybox.pem ubuntu@${swip} "bash configure_interfaces.sh"
	ssh -o StrictHostKeyChecking=no -i ~/graybox.pem ubuntu@${fwip} "bash configure_interfaces.sh"
	ssh -o StrictHostKeyChecking=no -i ~/graybox.pem ubuntu@${idsip} "bash configure_interfaces.sh"
	ssh -o StrictHostKeyChecking=no -i ~/graybox.pem ubuntu@${atsip} "bash configure_interfaces.sh"
	ssh -o StrictHostKeyChecking=no -i ~/graybox.pem ubuntu@${ffmip} "bash configure_interfaces.sh"
	ssh -o StrictHostKeyChecking=no -i ~/graybox.pem ubuntu@${pgip} "bash configure_interfaces.sh"
fi

if [ "$del" -eq 1 ] ; then

echo "Deleting routes on Client"
ssh -o StrictHostKeyChecking=no -i ~/graybox.pem ubuntu@${cip} "sudo ip route del 10.10.4.0/23"
ssh -o StrictHostKeyChecking=no -i ~/graybox.pem ubuntu@${cip} "sudo ip route del 10.10.2.0/23"
ssh -o StrictHostKeyChecking=no -i ~/graybox.pem ubuntu@${cip} "sudo ip route del 10.10.1.0/24"

echo "Deleting routes on PGW"
ssh -o StrictHostKeyChecking=no -i ~/graybox.pem ubuntu@${pgip} "sudo ip route del 10.10.4.0/23"
ssh -o StrictHostKeyChecking=no -i ~/graybox.pem ubuntu@${pgip} "sudo ip route del 10.10.2.0/23"

echo "Deleting routes on FW"
ssh -o StrictHostKeyChecking=no -i ~/graybox.pem ubuntu@${fwip} "sudo ip route del 10.10.4.0/23"
ssh -o StrictHostKeyChecking=no -i ~/graybox.pem ubuntu@${fwip} "sudo ip route del 10.10.3.0/24"
ssh -o StrictHostKeyChecking=no -i ~/graybox.pem ubuntu@${fwip} "sudo ip route del 10.10.0.0/24"

echo "Deleting routes on IDS"
ssh -o StrictHostKeyChecking=no -i ~/graybox.pem ubuntu@${idsip} "sudo ip route del 10.10.4.0/24"
ssh -o StrictHostKeyChecking=no -i ~/graybox.pem ubuntu@${idsip} "sudo ip route del 10.10.0.0/23"
ssh -o StrictHostKeyChecking=no -i ~/graybox.pem ubuntu@${idsip} "sudo ip route del 10.10.3.0/24"

echo "Deleting routes on SW"
ssh -o StrictHostKeyChecking=no -i ~/graybox.pem ubuntu@${swip} "sudo ip route del 10.10.0.0/23"
ssh -o StrictHostKeyChecking=no -i ~/graybox.pem ubuntu@${swip} "sudo ip route del ${vs4ip}/32"
ssh -o StrictHostKeyChecking=no -i ~/graybox.pem ubuntu@${swip} "sudo ip route del ${ws4ip}/32"
ssh -o StrictHostKeyChecking=no -i ~/graybox.pem ubuntu@${swip} "sudo ip route del 10.10.2.0/24"

echo "Deleting routes on FFM"
ssh -o StrictHostKeyChecking=no -i ~/graybox.pem ubuntu@${ffmip} "sudo ip route del 10.10.0.0/23"
ssh -o StrictHostKeyChecking=no -i ~/graybox.pem ubuntu@${ffmip} "sudo ip route del 10.10.2.0/24"
ssh -o StrictHostKeyChecking=no -i ~/graybox.pem ubuntu@${ffmip} "sudo ip route del 10.10.5.0/24"

echo "Deleting routes on ATS"
ssh -o StrictHostKeyChecking=no -i ~/graybox.pem ubuntu@${atsip} "sudo ip route del 10.10.0.0/23"
ssh -o StrictHostKeyChecking=no -i ~/graybox.pem ubuntu@${atsip} "sudo ip route del 10.10.2.0/24"
ssh -o StrictHostKeyChecking=no -i ~/graybox.pem ubuntu@${atsip} "sudo ip route del 10.10.5.0/24"

echo "Deleting routes on vServer"
#ssh -o StrictHostKeyChecking=no -i ~/graybox.pem ubuntu@${vsip} "sudo ip route del 10.10.5.0/24"
#ssh -o StrictHostKeyChecking=no -i ~/graybox.pem ubuntu@${vsip} "sudo ip route del 10.10.3.0/23"
#ssh -o StrictHostKeyChecking=no -i ~/graybox.pem ubuntu@${vsip} "sudo ip route del 10.10.1.0/23"
ssh -o StrictHostKeyChecking=no -i ~/graybox.pem ubuntu@${vsip} "sudo ip route del 10.10.0.0/21"

echo "Deleting routes on wServer"
#ssh -o StrictHostKeyChecking=no -i ~/graybox.pem ubuntu@${wsip} "sudo ip route del 10.10.5.0/24"
#ssh -o StrictHostKeyChecking=no -i ~/graybox.pem ubuntu@${wsip} "sudo ip route del 10.10.3.0/23"
#ssh -o StrictHostKeyChecking=no -i ~/graybox.pem ubuntu@${wsip} "sudo ip route del 10.10.1.0/23"
ssh -o StrictHostKeyChecking=no -i ~/graybox.pem ubuntu@${wsip} "sudo ip route del 10.10.0.0/21"

fi


echo "Adding routes on Client"
ssh -o StrictHostKeyChecking=no -i ~/graybox.pem ubuntu@${cip} "sudo ip route add 10.10.4.0/23 via ${pg0ip}"
ssh -o StrictHostKeyChecking=no -i ~/graybox.pem ubuntu@${cip} "sudo ip route add 10.10.2.0/23 via ${pg0ip}"
ssh -o StrictHostKeyChecking=no -i ~/graybox.pem ubuntu@${cip} "sudo ip route add 10.10.1.0/24 via ${pg0ip}"

echo "Adding routes on PGW"
ssh -o StrictHostKeyChecking=no -i ~/graybox.pem ubuntu@${pgip} "sudo ip route add 10.10.4.0/23 via ${fw1ip}"
ssh -o StrictHostKeyChecking=no -i ~/graybox.pem ubuntu@${pgip} "sudo ip route add 10.10.2.0/23 via ${fw1ip}"

echo "Adding routes on FW"
ssh -o StrictHostKeyChecking=no -i ~/graybox.pem ubuntu@${fwip} "sudo ip route add 10.10.4.0/23 via ${ids2ip}"
ssh -o StrictHostKeyChecking=no -i ~/graybox.pem ubuntu@${fwip} "sudo ip route add 10.10.3.0/24 via ${ids2ip}"
ssh -o StrictHostKeyChecking=no -i ~/graybox.pem ubuntu@${fwip} "sudo ip route add 10.10.0.0/24 via ${pg1ip}"

echo "Adding routes on IDS"
ssh -o StrictHostKeyChecking=no -i ~/graybox.pem ubuntu@${idsip} "sudo ip route add 10.10.4.0/24 via ${sw5ip}"
ssh -o StrictHostKeyChecking=no -i ~/graybox.pem ubuntu@${idsip} "sudo ip route add 10.10.0.0/23 via ${fw2ip}"
ssh -o StrictHostKeyChecking=no -i ~/graybox.pem ubuntu@${idsip} "sudo ip route add 10.10.3.0/24 via ${sw5ip}"

echo "Adding routes on SW"
ssh -o StrictHostKeyChecking=no -i ~/graybox.pem ubuntu@${swip} "sudo ip route add 10.10.0.0/23 via ${ids5ip}"
ssh -o StrictHostKeyChecking=no -i ~/graybox.pem ubuntu@${swip} "sudo ip route add ${vs4ip}/32 via ${ffm3ip}"
ssh -o StrictHostKeyChecking=no -i ~/graybox.pem ubuntu@${swip} "sudo ip route add ${ws4ip}/32 via ${ats3ip}"
ssh -o StrictHostKeyChecking=no -i ~/graybox.pem ubuntu@${swip} "sudo ip route add 10.10.2.0/24 via ${ids5ip}"

echo "Adding routes on FFM"
ssh -o StrictHostKeyChecking=no -i ~/graybox.pem ubuntu@${ffmip} "sudo ip route add 10.10.0.0/23 via ${sw3ip}"
ssh -o StrictHostKeyChecking=no -i ~/graybox.pem ubuntu@${ffmip} "sudo ip route add 10.10.2.0/24 via ${sw3ip}"
ssh -o StrictHostKeyChecking=no -i ~/graybox.pem ubuntu@${ffmip} "sudo ip route add 10.10.5.0/24 via ${sw3ip}"

echo "Adding routes on ATS"
ssh -o StrictHostKeyChecking=no -i ~/graybox.pem ubuntu@${atsip} "sudo ip route add 10.10.0.0/23 via ${sw3ip}"
ssh -o StrictHostKeyChecking=no -i ~/graybox.pem ubuntu@${atsip} "sudo ip route add 10.10.2.0/24 via ${sw3ip}"
ssh -o StrictHostKeyChecking=no -i ~/graybox.pem ubuntu@${atsip} "sudo ip route add 10.10.5.0/24 via ${sw3ip}"

echo "Adding routes on vServer"
ssh -o StrictHostKeyChecking=no -i ~/graybox.pem ubuntu@${vsip} "sudo ip route add 10.10.0.0/21 via ${ffm4ip}"

echo "Adding routes on wServer"
ssh -o StrictHostKeyChecking=no -i ~/graybox.pem ubuntu@${wsip} "sudo ip route add 10.10.0.0/21 via ${ats4ip}"


if [ "$inp" -ge 1 ] ; then

	echo "Enabling ip forwarding"
	ssh -o StrictHostKeyChecking=no -i ~/graybox.pem ubuntu@${swip} "sudo sysctl -w net.ipv4.ip_forward=1"
	ssh -o StrictHostKeyChecking=no -i ~/graybox.pem ubuntu@${fwip} "sudo sysctl -w net.ipv4.ip_forward=1"
	ssh -o StrictHostKeyChecking=no -i ~/graybox.pem ubuntu@${idsip} "sudo sysctl -w net.ipv4.ip_forward=1"
	ssh -o StrictHostKeyChecking=no -i ~/graybox.pem ubuntu@${atsip} "sudo sysctl -w net.ipv4.ip_forward=1"
	ssh -o StrictHostKeyChecking=no -i ~/graybox.pem ubuntu@${ffmip} "sudo sysctl -w net.ipv4.ip_forward=1"
	ssh -o StrictHostKeyChecking=no -i ~/graybox.pem ubuntu@${pgip} "sudo sysctl -w net.ipv4.ip_forward=1"

fi
