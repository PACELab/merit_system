nbr_host=${1:-5}
for i in $(seq 1 $nbr_host); do
	scp -o StrictHostKeyChecking=no -i graybox.pem ~/graybox.pem setup_ssh_compute.sh cp-${i}:~/
done
for i in $(seq 1 $nbr_host); do
	ssh -o StrictHostKeyChecking=no -i ~/graybox.pem cp-${i} 'bash setup_ssh_compute.sh'
done

for i in $(seq 1 $nbr_host); do
	ssh -i ~/graybox.pem cp-${i} "sh install_monitoring.sh"
done
