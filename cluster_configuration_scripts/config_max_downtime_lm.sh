dt=${1:-5000}
steps=${2:-8}
delay=${3:-35}
#echo $dt
sudo sed -i "s/#live_migration_downtime = /live_migration_downtime = /" /etc/nova/nova.conf
sudo sed -i "s/live_migration_downtime = [0-9]*/live_migration_downtime = ${dt}/" /etc/nova/nova.conf
sh config_novaLM.sh ${steps} ${delay}
