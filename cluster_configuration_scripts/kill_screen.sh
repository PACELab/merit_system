for i in "$@"
do
ssh -i graybox.pem ubuntu@${i} 'killall screen'
#ssh -i graybox.pem ubuntu@10.11.10.20 'killall screen'
#ssh -i graybox.pem ubuntu@10.11.10.21 'killall screen'
#ssh -i graybox.pem ubuntu@10.11.10.22 'killall screen'
done
