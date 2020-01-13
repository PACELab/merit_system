steps=$1
delay=$2
sudo sed -i "s/live_migration_downtime_steps = [0-9]*/live_migration_downtime_steps = ${steps}/" /etc/nova/nova.conf
sudo sed -i "s/live_migration_downtime_delay = [0-9]*/live_migration_downtime_delay = ${delay}/" /etc/nova/nova.conf
sudo service nova-compute restart
