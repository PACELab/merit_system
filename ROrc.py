import requests, time, re
import subprocess, sys, os, random
import math
import csv
from netaddr import IPNetwork, IPAddress
from collections import defaultdict
from color import color
from threading import Lock

# Class to perform change directory to get size from /var/lib/glance and then restore the previos directory path
class cd:
	def __init__(self, newPath):
		self.newPath = os.path.expanduser(newPath)

	def __enter__(self):
		self.savedPath = os.getcwd()
		os.chdir(self.newPath)

	def __exit__(self, etype, value, traceback):
		os.chdir(self.savedPath)


class ROrc:
	def __init__(self,openrc,timeout=14000, tot_bw=950):
		self.var={}
		self.t=timeout
		self.total_bw = tot_bw
		self.host_capacity = {}
		self.ping_running = {}
		self.lock = Lock()
		self.ping_sema = {}

		with open(openrc,'r') as rcf:
			for line in rcf:
				toks=line.strip().split()
				k,v=toks[1].split('=')
				self.var[k]=v
		print "Orchesterator init: Getting hypervisor capacities"
		self.get_hypervisor_info()
		nets_info = subprocess.check_output("openstack network list", shell=True).splitlines()
		self.net_ids = {}
		for line in nets_info:
			toks = line.strip().split()
			if len(toks)>3:
				self.net_ids[toks[3]] = toks[1]
		# get new token
		print "Orchesterator init: Getting new Token"
		self.token=(None,-1)

	def get_new_token(self):
		url = self.var['OS_AUTH_URL']+'/auth/tokens?nocatalog'
		payload = '{ "auth": { "identity": { "methods": ["password"],"password":{"user": {"domain": {"name": "'+self.var['OS_USER_DOMAIN_NAME']+'"},"name": "'+self.var['OS_USERNAME']+'", "password": "'+self.var['OS_PASSWORD']+'"} } }, "scope": { "project": { "domain": { "name": "'+self.var['OS_PROJECT_DOMAIN_NAME']+'" }, "name":	"'+self.var['OS_PROJECT_NAME']+'" } } }}'
		headers = {'content-type': 'application/json', 'Accept-Charset': 'UTF-8'}
		r = requests.post(url, data=payload, headers=headers)
		# TODO get response and update token var

	def do_moverebuild(self,vm,target):
		"""
		:param vm: VNF being migrated
		:type vm: str
		:param target: target to which VNF is being migrated
		:type target: str
		"""
		vm_info = subprocess.check_output("nova show %s"%(vm), shell=True).splitlines()
		target = self.fqdn(target)
#		nets_info = subprocess.check_output("openstack network list", shell=True).splitlines()
#		print "NET INFO",nets_info
#		print "NET IDS",net_ids
		# parse vm info for vm size, image, network ids
		# delete the VM
		# instantiate new vm with the info
		instance_size = -1
		image = -1
		nets = []
		pattern = re.compile('\| (.*) network .*')
		for kv in vm_info:
			if 'flavor:original_name' in kv:
				toks = kv.strip().split()
#				print toks
				instance_size = toks[3]

			if ' image ' in kv:
				toks = kv.strip().split()
#				print toks
				image = toks[3]

			if 'network' in kv:
#				print "KV",kv
				m = re.search(pattern,kv)
				if m:
					nets.append(self.net_ids[m.group(1)])
		print "VM_PARSED_INFO ",instance_size, image, nets
		st = time.time()
		subprocess.check_output("nova delete %s"%(vm), shell=True)
		time.sleep(2)
		net_component = ' --nic net-id='.join(nets)
		print net_component
		boot_command = 'nova boot %s --image %s --flavor %s --nic net-id=%s --key Jasim9-mwajahatXqosXXX --availability-zone nova:%s'%(vm,image,instance_size,net_component,target)
		print boot_command
		subprocess.check_output(boot_command, shell=True)
		return st

	def do_migrate(self,vm,target):
		"""
		:param vm: VNF being migrated
		:type vm: str
		:param target: target to which VNF is being migrated
		:type target: str
		"""

		target = self.fqdn(target)
		st = time.time()
		subprocess.check_output("nova migrate --host %s %s"%(target,vm), shell=True)
		time.sleep(1)
		return st

	def do_verify_migrate(self,vm):
		subprocess.check_output("nova resize-confirm %s"%(vm), shell=True)

	def do_livemigrate(self,vm,target):
		"""
		:param vm: VNF being migrated
		:type vm: str
		:param target: target to which VNF is being migrated
		:type target: str
		"""
		target = self.fqdn(target)
		st = time.time()
		print "LiveMigration Issued for", vm
		subprocess.check_output("nova live-migration %s %s"%(vm,target), shell=True)
		time.sleep(2)
		return st

	def calculate_rehoming_cost(self, total_AT, chain_DTs):
		return total_AT*(sum(chain_DTs)/len(chain_DTs)) # sum(AT)*mean(max_DTs)

	def truncate_logs(self, target): # Truncate log files on the target
		try:
			subprocess.check_output('ssh -i ~/graybox.pem %s "truncate -s 0 collectl.log ; truncate -s 0 iostat_log.csv ; truncate -s 0 mpstat_log.csv"'%(target), shell=True)
		except subprocess.CalledProcessError as grepexc:
			print "Unable to Truncate logs -- error code", grepexc.returncode, grepexc.output

	def disable_dynamic_ownership(self, hostname):
		subprocess.check_output("""ssh -i ~/graybox.pem %s "bash config_qemu_0.sh" """%(hostname), shell=True)

	def enable_dynamic_ownership(self, hostname):
		subprocess.check_output("""ssh -i ~/graybox.pem %s "bash config_qemu_1.sh" """%(hostname), shell=True)

	def get_bw_at_host(self, hostname, fetch='both'):
		# reads last 10 seconds of collectl data and internal max BW to give available BW
		# fetch: both - in and out BW as a list, otherwise in or out
		# also need to convert in Mbps from KBps (collectl)
		# $10 is KBin and $12 is KBout in collectl.log
		if fetch=='in':
			avg_bw = subprocess.check_output("""ssh -i ~/graybox.pem %s "tail collectl.log | awk '{sum+=\$10}END{print sum/NR}'" """%(hostname), shell=True).strip()
			print color.LIGHTRED,"BW IN usage at %s is %0.2f"%(hostname,float(avg_bw)/125),color.END
			return self.total_bw - (float(avg_bw)/125)
		elif fetch=='out':
			avg_bw = subprocess.check_output("""ssh -i ~/graybox.pem %s "tail collectl.log | awk '{sum+=\$12}END{print sum/NR}'" """%(hostname), shell=True).strip()
			print color.LIGHTRED,"BW OUT usage at %s is %0.2f"%(hostname,float(avg_bw)/125),color.END
			return self.total_bw - (float(avg_bw)/125)
		else:
			avg_bw = subprocess.check_output("""ssh -i ~/graybox.pem %s "tail collectl.log | awk '{sumin+=\$10;sumout+=\$12}END{print sumin/NR,sumout/NR}'" """%(hostname), shell=True).strip().split()
			return [self.total_bw - (float(i)/125) for i in avg_bw]


	# Gets VNF specific metrics from collect_metrics.sh
	def get_monitoring_metrics(self, vm, target, action, fetch = 4):
		"""
		:param vm: VNF being migrated
		:type vm: str
		:param target: target to which VNF is being migrated
		:type target: str
		:param action: action that was performed
		:type action: str
		:param fetch: optional parameter only specified during moverebuild as workaround for issue in getting correct field
		:type fetch: int
		"""
		if fetch == 4:
			instance_name = subprocess.check_output("nova show %s | grep -w instance_name | awk '{print $4}'"%(vm), shell=True).strip()
		else:
			instance_name = subprocess.check_output("nova show %s | grep -w instance_name | awk '{print $6}'"%(vm), shell=True).strip()
		ans = subprocess.check_output("bash collect_metrics.sh %s %s %s %s"%(target,action,vm,instance_name), shell=True).strip()
		ans = ans.split(',')
		return ans

	def get_mpstat_metrics(self, hostname, time=20):
		avm, avs = subprocess.check_output("""ssh -i ~/graybox.pem %s "tail -n %d ~/mpstat_log.csv" | python ~/vnf-rehoming/parse_mpstat.py """%(hostname, time), shell=True).strip().split()
		return (float(avm),float(avs))

	def get_iostat_metrics(self, hostname, time=20):
		tps, rkb, wkb = subprocess.check_output("""ssh -i ~/graybox.pem %s "tail -n %d ~/iostat_log.csv" | python ~/vnf-rehoming/parse_iostat.py """%(hostname, time), shell=True).strip().split()
		return (float(tps),float(rkb),float(wkb))

	def get_instance_disk_size(self, hostname, instance_hexid):
		output = subprocess.check_output("""ssh -i ~/graybox.pem %s "ls -l --block-size=M /var/lib/nova/instances/%s/disk" """%(hostname,instance_hexid), shell=True).strip().split()
		# example: -rw-r--r-- 1 libvirt-qemu kvm 382M Jan  9 02:17 /var/lib/nova/instances/be137190-56b9-420a-8ad7-bfe2ff454c41/disk
		dsk_sz = output[4]
		return int(dsk_sz[:-1])

	def get_pdr_metrics(self, hostname, instance_name):
		# ssh -i graybox.pem cp-1 "python get_pdr.py instance-00000001" | python parse_profiler.py
		try:
			pdr_mets = subprocess.check_output("""ssh -i ~/graybox.pem %s "python get_pdr.py %s" | python ~/vnf-rehoming/parse_profiler.py """%(hostname, instance_name), shell=True).strip().split()
			metric_names = ['pdrm', 'pdrs', 'pdrmin', 'pdrlow3', 'wssm', 'wssmax', 'mwpm', 'mwpmin', 'wse', 'nwse']
			metric_values = [float(i) for i in pdr_mets]
			return (dict(zip(metric_names, metric_values)), metric_values)
		except subprocess.CalledProcessError as grepexc:
			print color.RED,"ERROR in get_pdr_metrics process call",color.END
			print "error code", grepexc.returncode, grepexc.output
		except Exception as e:
			print color.RED,"Error in parsing probably - \n",pdr_mets,"\n",str(e),color.END

	def get_mem(self, vm_ip):
		mem, used_mem = subprocess.check_output("""ssh -i ~/graybox.pem ubuntu@%s "free -m" | grep Mem | awk '{print $2,$3}' """%(vm_ip), shell=True).strip().split()
		return (int(mem),int(used_mem))

	def get_image_size(self, image_hexid):
		output = subprocess.check_output("""ls -l --block-size=M /var/lib/glance/images/%s """%(image_hexid), shell=True).strip().split()
		img_sz = output[4]
		return int(img_sz[:-1])

	def generate_training_data(self, data):
		with open("training_data.csv", 'a') as f:
			f.seek(0, os.SEEK_END)
			fwriter = csv.writer(f)
			if f.tell() == 0:
				fwriter.writerow(['bw', 'tps', 'rkb', 'wkb', 'avm', 'avs'])
			fwriter.writerow(data)

	def get_vnf_metrics(self, vm, action, schain):
		"""
		:param vm: VNF being migrated
		:type vm: str
		:param action: action that was performed
		:type action: str
		"""
		res = []
		print color.RED,"This Function is empty get_vnf_metrics", color.END
		return res

	def get_status(self,vm_id):
		# TODO use token call
		status = subprocess.check_output("nova show %s | grep -w status | awk '{print $4}'"%(vm_id), shell=True)
		return status.strip()

	def get_meta_for(self,vm_id):
		data = subprocess.check_output("nova show %s | awk 'NF>2' "%(vm_id), shell=True).splitlines()
		meta = {}
		for line in data:
			toks = line.split('|')
			meta[toks[1].strip()] = toks[2].strip()
#			print toks
#		print color.YELLOW, meta, color.END
		return meta

	def find_intersecting_octets(self, ip1, ip2):    # Get the number of common octets
		ip1_octets = ip1.split('.')
		ip2_octets = ip2.split('.')
		lst = [value for value in ip1_octets if value in ip2_octets]
		return len(lst)

	def add_routes(self,vm_id,action, schain):
		print color.MAGENTA, "Setting up networking for chain %s"%(schain.name), color.END
		if action!='livemigrate':
			with self.lock:
				if schain.name == 'rt-fw':
					subprocess.check_output("bash ~/vnf-rehoming/setup_chain_networking.sh", shell=True)  # Script to setup chain networking
				elif schain.name == 'wan':
					subprocess.check_output("bash ~/vnf-rehoming/setup_chain_networking_wan.sh", shell=True)  # Script to setup chain networking
		return

	def start_ping_in_screen(self,from_vm,to_vm,logfile):
		from_to = "%s,%s"%(from_vm,to_vm)
		if from_to in self.ping_running and self.ping_running[from_to]==True:
			print color.RED, "\tPing already running, incrementing", color.END
			self.ping_sema[from_to] +=1
			return
		else:
			print "Starting ping from %s to %s"%(from_vm,to_vm)
			self.ping_sema[from_to] = 1
			self.ping_running[from_to] = True
		scp_cmd = 'scp -i ~/graybox.pem ~/vnf-rehoming/run_ping_to.sh ubuntu@%s:~/'%(from_vm)
		subprocess.check_output(scp_cmd, shell=True)
		ping_cmd = 'ssh -i ~/graybox.pem ubuntu@%s "screen -S ping-screen -d -m sh run_ping_to.sh %s %s"'%(from_vm,to_vm,logfile)
		print color.CYAN, ping_cmd, color.END
		try:
				subprocess.check_output(ping_cmd, shell=True)
		except subprocess.CalledProcessError as grepexc:
			print "Unable to run ping -- error code", grepexc.returncode, grepexc.output

	def stop_ping_in_screen(self,from_vm,to_vm):
		from_to = "%s,%s"%(from_vm,to_vm)
		self.ping_sema[from_to] -= 1
		if self.ping_sema[from_to]!=0:
			print color.RED, "\tOther threads still running, not killing ping", color.END
			return
		self.ping_running[from_to] = False
		print color.MAGENTA, "Stopping ping screen",from_to, color.END
		try:
			# TODO store screen id for future kill, instead of killall
			subprocess.check_output('ssh -i ~/graybox.pem ubuntu@%s "killall screen"'%(from_vm), shell=True)
		except subprocess.CalledProcessError as grepexc:
			print "Unable to stop ping -- error code", grepexc.returncode, grepexc.output

	def check_ssh_up(self,vm):
		try:
			subprocess.check_output('ssh -q -i ~/graybox.pem ubuntu@%s "ls"'%(vm), shell=True)
		except subprocess.CalledProcessError as grepexc:
			print "SSH threw error code", grepexc.returncode, grepexc.output
			print "\t\tVM IP:",vm
			return False
		return True

	def check_ping_alive(self,from_vm, log_file):
		try:
			first_check = subprocess.check_output('ssh -i ~/graybox.pem ubuntu@%s "tail -1 %s"'%(from_vm,log_file), shell=True).strip().split()
			time.sleep(0.3)
			second_check = subprocess.check_output('ssh -i ~/graybox.pem ubuntu@%s "tail -1 %s"'%(from_vm,log_file), shell=True).strip().split()

			ft = first_check[0].strip('[]')
			st = second_check[0].strip('[]')
			if ft == st:
				return False
			else:
				time.sleep(1)
				if 'bytes' in second_check :
#					print first_check
#					print second_check
#					print lt
					return True
			return False
		except subprocess.CalledProcessError as grepexc:
			print color.RED,"Unable to check ping_alive -- error code", grepexc.returncode, grepexc.output,color.END
		except Exception, e:
			print color.RED, "Runtime error in check_ping_alive :", str(e), color.END

	def calculate_downtime(self,client,log_file,action):
		nbr = random.randint(1,20)
		try:
				subprocess.check_output("scp -i ~/graybox.pem ubuntu@%s:~/%s ~/temp_%d ; bash ~/vnf-rehoming/remove_null.sh ~/temp_%d"%(client,log_file,nbr,nbr), shell=True)
		except subprocess.CalledProcessError as grepexc:
			print "Unable to calculate downtime -- error code", grepexc.returncode, grepexc.output

		parser = 'pinglog_to_downtime.py'
		res = subprocess.check_output("python ~/vnf-rehoming/%s ~/temp_%s | cut -d ' ' -f 8"%(parser,nbr), shell=True).strip()
#		res = subprocess.check_output("python ~/vnf-rehoming/%s ~/temp_%s | awk '{print $NF}'"%(parser,client), shell=True).strip()
		try:
			ret = float(res)
		except ValueError:
			print("Error parsing ping parse output", res)
			return -1
		return ret

	def get_hypervisor_info(self):
		hyp_list = subprocess.check_output("openstack hypervisor list | grep QEMU | grep -w up | awk '{print $4}'", shell=True)
		hyp_list = hyp_list.splitlines()
		for hyp in hyp_list:
			hyp_info = subprocess.check_output("openstack hypervisor show %s | awk '/local_gb\>/{tot=$4}/local_gb_used/{used=$4}END{print tot-used}'"%(hyp), shell=True)
			self.host_capacity[hyp] = int(hyp_info.strip())
		print color.YELLOW, self.host_capacity, color.END

	def fqdn(self, host_name):
		for hn in self.host_capacity:
			if hn == host_name:
				return hn
			elif host_name in hn:
				return hn
		print color.RED, 'host not found in host_capacity. Are you sure the host name is correct?', host_name,color.END
		raise Exception('Incorrect Host Name')

	def get_candidate_hosts(self,vnf_action,hosts_unavailable):
		"""
		:param vnf_action: decided action for each vnf
		:type vnf_action: dict
		:param hosts_unavailable: hosts going away
		:type hosts_unavailable: list
		"""
		nLM = sum(1 for x in vnf_action.values() if x=='livemigrate')
		nCMR = len(vnf_action) - nLM
		vnf_host={}
		lmset=[]
		cmset=[]
		print "Sorted Host Capacities:",sorted(self.host_capacity.items(), key=lambda x: x[1], reverse=True)
		for k,v in sorted(self.host_capacity.items(), key=lambda x: x[1], reverse=True):
			if k in hosts_unavailable or 'cp-1' in k : # TODO use a configuration value instead
				continue
			if nLM>nCMR:
				nLM-=1
				lmset.append(k)
			else:
				nCMR-=1
				cmset.append(k)
			if not nLM and not nCMR:
				break

		i=0; j=0;
		for vnf in vnf_action:
			if vnf_action[vnf] == 'livemigrate':
				vnf_host[vnf] = lmset[i]
				i = (i+1)%len(lmset)
			else:
				vnf_host[vnf] = cmset[j]
				j = (j+1)%len(cmset)

		print color.MAGENTA, 'Target hosts identified: ', vnf_host, color.END
		return vnf_host

def test_migration(s):
	s.start_ping_in_screen('10.11.10.10','10.10.3.10','ping_log.txt')
	time.sleep(10)
	print "start migrate"
	vnf='Firewall'
	s.do_migrate(vnf,sys.argv[1])
	while s.get_status(vnf) != 'VERIFY_RESIZE':
		time.sleep(0.5)
	s.do_verify_migrate(vnf)
#	start_time = orchesterator.do_moverebuild('Firewall','cp-3.lm-rocky.live-migrate-pg0.clemson.cloudlab.us')
	while not s.check_ssh_up('10.11.10.21'):
		time.sleep(0.5)
	print "SSH is up, add routes"
	print "Checking pings now"
	while not s.check_ping_alive('10.11.10.10'):
		time.sleep(0.5)
		print '.',
	print "Ping alive again"

	time.sleep(30)
	s.stop_ping_in_screen('10.11.10.10')
	print "Ping stopped"


if __name__ == "__main__":
	s=ROrc('/users/Jasim9/admin-openrc.sh')
#	print s.get_status('Firewall')
#	s.do_moverebuild('Firewall','cp-3')
#	s.get_hypervisor_info()
#	s.get_meta_for('Firewall')
	print s.get_bw_at_host('cp-2','in')
	print s.get_bw_at_host('cp-2','out')
	print s.get_bw_at_host('cp-2')
