iostat -d 1 -t | stdbuf -oL -eL awk '$2 ~ /^[0-9]{2}:[0-9]{2}:[0-9]{2}/{ts=$1"-"$2}/sda|sdb/{tps[$1]=$2;reads[$1]=$3;writes[$1]=$4}!NF{printf "%s ",ts; for (i in tps){printf "%s,%s,%s,%s ",i,tps[i],reads[i],writes[i]; } printf "\n"; }' | tee iostat_log.csv
