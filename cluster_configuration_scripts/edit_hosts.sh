nbr_host=${1:-5}
sudo sed -i 's/\(10\.11\.10.*\) cp-1-0/\1 cp-1-0\tgluster1/' /etc/hosts
pfx=$(head -1 /etc/hosts | awk '{print $2}' | cut -d. -f 2-)
#sudo sed -i "s/\(10\.11.*\) cp-1-0/\1 cp-1-0\tcp-1.${pfx}/" /etc/hosts
#sudo sed -i "s/\(10\.11.*\) cp-2-0/\1 cp-2-0\tcp-2.${pfx}/" /etc/hosts
#sudo sed -i "s/\(10\.11.*\) cp-3-0/\1 cp-3-0\tcp-3.${pfx}/" /etc/hosts
#sudo sed -i "s/\(10\.11.*\) cp-4-0/\1 cp-4-0\tcp-4.${pfx}/" /etc/hosts
#sudo sed -i "s/\(10\.11.*\) cp-5-0/\1 cp-5-0\tcp-5.${pfx}/" /etc/hosts
#sudo sed -i "s/\(10\.11.*\) cp-6-0/\1 cp-6-0\tcp-6.${pfx}/" /etc/hosts
#sudo sed -i "s/\(10\.11.*\) cp-7-0/\1 cp-7-0\tcp-7.${pfx}/" /etc/hosts

for j in $(seq 1 $nbr_host); do
	sudo sed -i "s/\(10\.11.*\) cp-${j}-0/\1 cp-${j}-0\tcp-${j}.${pfx}/" /etc/hosts
done

