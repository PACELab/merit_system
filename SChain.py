import json
import itertools
from ROrc import ROrc
import subprocess, time
import re
import collections
from collections import defaultdict, OrderedDict
from color import color
from threading import Lock
import threading

class Graph:
	def __init__(self):
		self.graph = defaultdict(list)

	def addEdge(self, u, v):
		self.graph[u].append(v)

	def __getitem__(self, key):
		return self.graph[key]

	def DFS(self, v):
		visited = set()
		stack = [v]
		while stack:
			node = stack.pop()
			if node not in visited:
				visited.add(node)
				stack.extend(set(self.graph[node]) - visited)
		return list(visited)[1:]

	def print_graph(self):
		for key, val in self.graph.items():
			print "[", key, "]:", val

class SChain:

	def __init__(self,name,n,data,orch):
		self.name = name
		self.adj_matrix = []

		for i in range(1,n):
			self.adj_matrix.append([int(j) for j in data[i].split()])

		self.vnf_properties = json.loads(data[-1]) # list of dictionaries for each VM
#		print color.MAGENTA, self.vnf_properties, color.END

		self.host_map = {}
		self.vnfs = {} # contains the features and other meta data for each VM
		self.vnf_list = [] # list has same order as the adjacency matrix, can be used as ref in graph
		self.vnf_feature_pred_act = defaultdict(lambda: defaultdict(list))
#		print color.UNDERLINE, "PRED ACT Type:",type(self.vnf_feature_pred_act),type(self.vnf_feature_pred_act["KEY"]), color.END
		for vnf in self.vnf_properties:
			if "host" in vnf:
			    self.host_map[vnf['name']] = vnf['host']
			self.vnfs[vnf['name']] = vnf
			self.vnf_list.append(vnf['name'])

		self.update_host_map(orch) # takes care of updating other props as well
		self.set_available_actions(['moverebuild','migrate','livemigrate'])

		self.chain_lock = Lock()

		self.orch = orch
		self.periodic_runner = {}
		self.periodic_pause = {}
		self.metrics = {}
		for vnf_name in self.vnf_list:
			if self.vnfs[vnf_name]['rehome']:
				thread = threading.Thread(target=self.get_metrics_periodic, args= (vnf_name,) )
				thread.daemon = True
				self.periodic_runner[vnf_name] = True
				self.periodic_pause[vnf_name] = False
				thread.start()

	def contains(self, vnf_name):
		if vnf_name in self.vnfs:
			return True
		else:
			return False

	def stop_periodic_metric_collection(self, vnf_name):
		self.periodic_runner[vnf_name] = False

	def stop_periodic_metric_collection_all(self):
		for vnf_name in self.periodic_runner:
			self.stop_periodic_metric_collection(vnf_name)

	def pause_periodic_metric_collection(self, vnf_name):
		self.periodic_pause[vnf_name] = True

	def resume_periodic_metric_collection(self, vnf_name):
		self.periodic_pause[vnf_name] = False

	def update_host_map(self, orch):
		for vnf_name in self.vnf_list:
			self.update_meta_for(vnf_name,orch)
			self.host_map[vnf_name] = orch.fqdn(self.vnfs[vnf_name]['OS-EXT-SRV-ATTR:hypervisor_hostname'])
			self.vnfs[vnf_name]['host'] = self.host_map[vnf_name]

	def update_meta_for(self, vnf, orch):
		data = orch.get_meta_for(vnf)
		for key, val in data.items():
			self.vnfs[vnf][key] = val
		self.vnfs[vnf]['manage-ip-addr'] = self.vnfs[vnf]['flat-lan-1-net network'] # TODO make conf param
#		self.get_routes(orch)

	def get_latest_metrics(self, vnf_name, orch):
		# get latest metric values (dsk size, pdr, avm avs, rkb etc) and store it in self.vnfs
		# read from log files on gluster host - io files
		# read from src host - the disk size, pdr features
		# read from VM - usedmem
		gluster = 'cp-1'
		metric_names = ['avm','avs','tps','rkb','wkb','disk','mem','usedmem','pdrm', 'pdrs', 'pdrmin', 'pdrlow3', 'wssm', 'wssmax', 'mwpm', 'mwpmin', 'wse', 'nwse']
		self.update_meta_for(vnf_name, orch)
		avm, avs = orch.get_mpstat_metrics(gluster)
		metric_values = [avm,avs]
		io_metrics = orch.get_iostat_metrics(gluster)
		metric_values.extend(list(io_metrics))
		disk_size = orch.get_instance_disk_size(gluster, self.vnfs[vnf_name]['id'])
		metric_values.append(disk_size)
		mem_metrics = orch.get_mem(self.vnfs[vnf_name]['manage-ip-addr'])
		metric_values.extend(list(mem_metrics))
		pdr_d, pdr_metrics = orch.get_pdr_metrics(self.vnfs[vnf_name]['OS-EXT-SRV-ATTR:host'],self.vnfs[vnf_name]['OS-EXT-SRV-ATTR:instance_name']) # dict
		metric_values.extend(pdr_metrics)

		for k,v in zip(metric_names, metric_values):
			self.vnfs[vnf_name][k] = v

		return dict(zip(metric_names, metric_values))

	def get_metrics_periodic(self, vnf_name):
		while self.periodic_runner[vnf_name]:
			if not self.periodic_pause[vnf_name]:
				self.metrics[vnf_name] = self.get_latest_metrics(vnf_name, self.orch)
			time.sleep(60)

	def get_latest_metrics_async(self, vnf_name):
		if vnf_name in self.metrics:
			return self.metrics[vnf_name]
		else:
			self.metrics[vnf_name] = self.get_latest_metrics(vnf_name,self.orch)
			return self.metrics[vnf_name]

	def set_feature_vec(self, vnf_name, action, feat_vec):
		self.vnf_feature_pred_act[vnf_name][action] = []
		self.vnf_feature_pred_act[vnf_name][action].extend(feat_vec)

	def add_feature_vec(self, vnf_name, action, values):
		self.vnf_feature_pred_act[vnf_name][action].extend(values)

	def get_feature_pred_act_vector(self, vnf_name, action):
		return self.vnf_feature_pred_act[vnf_name][action]

	def get_vnf_prop(self, vnf_name, orch):
		# return dictionary with all the features and the source host - naming should be consistent with merit.ini
		# TODO parameterize with merit.ini somehow - maybe pass the merit object
		vnf_prop = self.get_latest_metrics_async(vnf_name)
		vnf_prop['vnf_name'] = vnf_name
		vnf_prop['src_host'] = self.vnfs[vnf_name]['OS-EXT-SRV-ATTR:host']
		vnf_prop['instance'] = int(self.vnfs[vnf_name]['flavor:ram'])//1000 # instance is in GBs rounded
		# 'image': 'vClient (e6e6a29f-3856-4b12-85f7-e80423b58f96)'
		image_hexid = self.vnfs[vnf_name]['image'].split()[1].strip('(').strip(')')
		vnf_prop['image'] = orch.get_image_size(image_hexid)
		return vnf_prop

	def get_dt_paths(self):
		# TODO use graph traversal to find the actual DT paths.
		if self.name == 'rt-fw':
			return [['Router2','Firewall']]
		elif self.name == 'wan':
			return [['PGW','Firewall','IDS','Switch','FFM'],['PGW','Firewall','IDS','Switch','ATS']]

	def set_available_actions(self, actions):
		self.available_actions = actions

	def get_feasible_actions(self, vnf_name):
		return self.vnfs[vnf_name]['feasible_actions']

	def get_vnfs_on_hosts(self, hosts):
		return [vnf_name.encode('ascii') for vnf_name in self.vnf_list if self.host_map[vnf_name] in hosts and self.vnfs[vnf_name]['rehome'] ]

	def get_vnfs_per_host(self, hosts):
		host_to_vnf = defaultdict(list)
		for vnf_name in self.vnf_list:
			if self.host_map[vnf_name] in hosts and self.vnfs[vnf_name]['rehome']:
				host_to_vnf[self.host_map[vnf_name]].append(vnf_name.encode('ascii'))
		return host_to_vnf

	def get_client_endpoint(self,orchestrator):
#		self.vnfs['vClient']['manage-ip-addr'] = orchestrator.get_meta_for("vClient")['flat-lan-1-net network']
		return self.vnfs['vClient']['manage-ip-addr']

	def get_server_endpoint(self,orchestrator):
#		self.vnfs['vServer']['manage-ip-addr'] = orchestrator.get_meta_for("vServer")['flat-lan-1-net network']
#		return self.vnfs['vServer']['manage-ip-addr']
		return [self.vnfs['vServer']['mnic-4 network'],self.vnfs['wServer']['mnic-4 network']]

	def get_ip_for(self,vnf,orchestrator):
		return self.vnfs[vnf]['manage-ip-addr']

	def get_routes(self,orchestrator):
		print color.RED, "Fetching saved routes", color.END
		for name in self.vnfs:
			if 'test_instance' in name:
				continue
			ip = self.get_ip_for(name,orchestrator)
			try:
				output = subprocess.check_output('ssh -o StrictHostKeyChecking=no -i ~/graybox.pem ubuntu@%s "route"'%(ip), shell=True).split()
			except subprocess.CalledProcessError as grepexc:
				print "error code", grepexc.returncode, grepexc.output
				continue
			self.vnfs[name]['routes'] = {}
			for i in range(12, len(output), 8):
				self.vnfs[name]['routes'][output[i]] = [output[i+1], output[i+2]]
