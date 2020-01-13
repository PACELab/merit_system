export PYTHONIOENCODING=utf8

#echo $OS_TOKEN
curl -i -s -X POST $OS_AUTH_URL/auth/tokens?nocatalog   -H "Content-Type: application/json"   -d '{ "auth": { "identity": { "methods": ["password"],"password": {"user": {"domain": {"name": "'"$OS_USER_DOMAIN_NAME"'"},"name": "'"$OS_USERNAME"'", "password": "'"$OS_PASSWORD"'"} } }, "scope": { "project": { "domain": { "name": "'"$OS_PROJECT_DOMAIN_NAME"'" }, "name":  "'"$OS_PROJECT_NAME"'" } } }}' > curl_op.txt
OS_TOKEN=`python parse_curl.py`
st=$(echo | ts)

while [ 1 ] ; do
	instance=$(curl -s -H "X-Auth-Token: $OS_TOKEN" http://ctl:8774/v2.1/servers?name=$1 | grep -Po '"'"id"'"\s*:\s*"\K([^"]*)')
#	instance=$(curl -s -H "X-Auth-Token: $OS_TOKEN" http://ctl:8774/v2.1/servers?name=$1 )
#	echo $instance
	status=$(curl -s -H "X-Auth-Token: $OS_TOKEN" http://ctl:8774/v2.1/servers/$instance | grep -Po '"'"status"'"\s*:\s*"\K([^"]*)')
	echo $status | ts ;
	en=$(echo | ts)
	tdiff=$(echo -e "t t test\n$st\n$en" | awk '{print $3}' | python time_diff.py)
	if [ "$tdiff" -gt 14000 ] ; then # token expires every 4 hours, this can be configured when instantiating the profile
		curl -i -s -X POST $OS_AUTH_URL/auth/tokens?nocatalog   -H "Content-Type: application/json"   -d '{ "auth": { "identity": { "methods": ["password"],"password": {"user": {"domain": {"name": "'"$OS_USER_DOMAIN_NAME"'"},"name": "'"$OS_USERNAME"'", "password": "'"$OS_PASSWORD"'"} } }, "scope": { "project": { "domain": { "name": "'"$OS_PROJECT_DOMAIN_NAME"'" }, "name":  "'"$OS_PROJECT_NAME"'" } } }}' > curl_op.txt
		OS_TOKEN=`python parse_curl.py`
		st=$(echo | ts)
	else
		sleep 0.5 ;
	fi
done
