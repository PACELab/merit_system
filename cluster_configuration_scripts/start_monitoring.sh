nbr_host=${1:-5}
for i in $(seq 1 $nbr_host); do
	ssh -i ~/graybox.pem cp-${i} 'screen -S iotop-screen -d -m sh start_iotop.sh'
	ssh -i ~/graybox.pem cp-${i} 'screen -S iostat-screen -d -m sh start_iostat.sh'
	ssh -i ~/graybox.pem cp-${i} 'screen -S mpstat-screen -d -m sh start_mpstat.sh'
	ssh -i ~/graybox.pem cp-${i} 'screen -S collectl-screen -d -m sh start_collectl.sh'
done
