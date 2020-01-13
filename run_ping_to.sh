to=$1
log_file=$2
ping -D -i 0.2 ${to} | tee ${log_file}
