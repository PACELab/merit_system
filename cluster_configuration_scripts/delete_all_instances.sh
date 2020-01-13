nova list | awk '$2 && $2 != "ID" {print $2}' | xargs -n1 nova delete
