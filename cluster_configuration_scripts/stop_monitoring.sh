nbr_host=${1:-5}
for i in $(seq 1 $nbr_host); do
	ssh -i ~/graybox.pem cp-${i} 'screen -X -S $(screen -ls | grep mpstat | awk "{print \$1}") kill'
	ssh -i ~/graybox.pem cp-${i} 'screen -X -S $(screen -ls | grep iotop | awk "{print \$1}") kill'
	ssh -i ~/graybox.pem cp-${i} 'screen -X -S $(screen -ls | grep iostat | awk "{print \$1}") kill'
	ssh -i ~/graybox.pem cp-${i} 'screen -X -S $(screen -ls | grep collectl | awk "{print \$1}") kill'
	ssh -i ~/graybox.pem cp-${i} 'screen -ls'
done
