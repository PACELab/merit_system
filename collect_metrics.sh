#!/bin/bash
# Script to execute the parsing scripts and collect the output depending on the action performed
# parse_collectl_new: get BW
# Live Migrate: parse_profiler: metrics related to PDR
# Moverebuild: parse_mpstat: avm, avs
# Cold migrate: parse_iostat: tps, rkb, wkb

#Usage
usage() {
	echo "Usage: $0 TARGET_HOST ACTION VM INSTANCE_NAME"
	exit 1
}

src_host=$(nova show $3 | grep hypervisor_hostname | awk '{print $4}' | cut -d  '.' -f 1)

scp -i ~/graybox.pem ../parse_mpstat.py $1:/users/Jasim9
scp -i ~/graybox.pem ../parse_iostat.py $1:/users/Jasim9
scp -i ~/graybox.pem ../parse_collectl_new.py $1:/users/Jasim9
scp -i ~/graybox.pem ../parse_profiler.py $src_host:/users/Jasim9

ans=()

if [ $2 == "livemigrate" ]; then
	ans+=($(ssh -i ~/graybox.pem Jasim9@$1 'python parse_collectl_new.py'))
	ans+=(',')
	ssh -i ~/graybox.pem Jasim9@$src_host "python get_pdr.py $4"
	ans+=($(ssh -i ~/graybox.pem Jasim9@$src_host "python parse_profiler.py profiler_log.txt"))
fi

if [ $2 == "moverebuild" ]; then
	ans+=($(ssh -i ~/graybox.pem Jasim9@$1 'python parse_collectl_new.py'))
	ans+=(',')
	ans+=($(ssh -i ~/graybox.pem Jasim9@$1 'python parse_mpstat.py mpstat_log.csv'))
fi

if [ $2 == "migrate" ]; then
	ans+=($(ssh -i ~/graybox.pem Jasim9@$1 'python parse_collectl_new.py'))
	ans+=(',')
	ans+=($(ssh -i ~/graybox.pem Jasim9@$1 'python parse_iostat.py iostat_log.csv'))
	ans+=(',')
	ans+=($(ssh -i ~/graybox.pem Jasim9@$1 'python parse_mpstat.py mpstat_log.csv'))
fi

echo ${ans[@]}
