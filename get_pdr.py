from __future__ import division
import sys, json, time, subprocess
from datetime import datetime

def main(domain):
	with open('profiler_log_%s.txt'%(domain),'w') as wf:
		subprocess.check_output("""sudo virsh qemu-monitor-command %s '{"execute": "set_profiler_parameter", "arguments": {"period": 15000} }' """%(domain),shell=True)
		subprocess.check_output(""" sudo virsh qemu-monitor-command %s '{ "execute": "start_profiler" }' """%(domain),shell=True)
		time.sleep(15)
		json_str=subprocess.check_output(""" sudo virsh qemu-monitor-command %s '{ "execute": "query_profile_result" }' """%(domain),shell=True)
		json_obj=json.loads(json_str)
		while 'error' in json_obj:
			time.sleep(1)
			json_str=subprocess.check_output(""" sudo virsh qemu-monitor-command %s '{ "execute": "query_profile_result" }' """%(domain),shell=True)
			json_obj=json.loads(json_str)
		res = json_obj['return']
		ws_entropy=res['working_set_entropy']
		nws_entropy=res['non_working_set_entropy']
		output="pdr,%s\nwss,%s\nmwp,%s\nws_entropy,%s\nnws_entropy,%s\n"%(res['pdr'],res['ws'],res['mwpp'],ws_entropy,nws_entropy)
		wf.write(output)
		wf.flush()
		print output


if len(sys.argv)<2:
	print "No instance name provided"
	exit(0)
main(sys.argv[1])

#{u'return': {u'zero_pages': 436439, u'non_working_set_entropy': 0.684628, u'computation_time': u'26,27,26,26,26', u'total_pages': 526546, u'pdr': u'65,59,55,55,64',
# u'rd': u'0,57,55,55,62', u'state': u'completed', u'ws': u'65,67,67,67,69', u'crd': u'0,57,57,57,63', u'working_set_entropy': -1, u'working_set_pages': 69, u'params':
#{u'adaptive': False, u'max_iteration': 5, u'period': 5000, u'interval': 1000, u'sampling': 32}, u'mwpp': u'0,1,0,0,0'}, u'id': u'libvirt-344'}
