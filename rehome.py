import pickle
import sys, os, threading, time
import warnings, socket, operator, itertools
from SChain import SChain
from merit import MERIT
from ROrc import ROrc
from color import color
from collections import defaultdict

orchestrator = ROrc('/users/Jasim9/admin-openrc.sh')

def sys_init(chain_file,training_dir):
	chain_list={}
	with open(chain_file,'r') as cf:
		lines=cf.read().splitlines()
		n_chains=int(lines[0])
		j=1
		for i in range(n_chains):
			desc=lines[j].split()
			num_vnf=int(desc[0])
			chain_name=desc[1]
			chain_list[chain_name]=SChain(chain_name,num_vnf,lines[j:j+num_vnf+2],orchestrator)
			j+=num_vnf+2
#	if __debug__:
	print "Chain reading complete, building models"
	models=MERIT(chain_list, orchestrator)

	return (chain_list,models)


def perform_action(action, vnf, target_host, schain):
	"""
	:param action: action to be performed
	:type action: str
	:param vnf: vnf to be migrated
	:type vnf: str
	:param schain: service chain object
	:type schain: SChain
	:param target: targets for the VNF
	:type target: str
	"""

	schain.pause_periodic_metric_collection(vnf)

	print color.PURPLE, "Rehoming %s VNF to %s using %s"%(vnf, target_host, action), color.END

	client = schain.get_client_endpoint(orchestrator)
	server, server2 = schain.get_server_endpoint(orchestrator)
	# changes here for multiple downtimes - maybe server endpoint returns multiple points
	orchestrator.start_ping_in_screen(client,server,'ping_logv.txt')
	orchestrator.start_ping_in_screen(client,server2,'ping_logw.txt')
	start_time = -1
#	orchestrator.truncate_logs(target_host)   # Truncate log files prior to start of action
	end_time = -1

	if action == 'moverebuild':
		start_time = orchestrator.do_moverebuild(vnf,target_host)
		st = time.time()
		while orchestrator.get_status(vnf) != 'ACTIVE':
			time.sleep(max(0.01,1-(time.time()-st)))
			st = time.time()
		end_time = st
		schain.update_meta_for(vnf,orchestrator)
	elif action == 'migrate':
		start_time = orchestrator.do_migrate(vnf,target_host)
		st = time.time()
		while orchestrator.get_status(vnf) != 'VERIFY_RESIZE':
			time.sleep(max(0.01,1-(time.time()-st)))
			st = time.time()
		orchestrator.do_verify_migrate(vnf)
		end_time = time.time()
	elif action == 'livemigrate':
		src_host = schain.host_map[vnf]
		orchestrator.disable_dynamic_ownership(src_host)
		orchestrator.disable_dynamic_ownership(target_host)
		start_time = orchestrator.do_livemigrate(vnf,target_host)
		st = time.time()
		while orchestrator.get_status(vnf) != 'ACTIVE':
			time.sleep(max(0.01,1-(time.time()-st)))
			st = time.time()
		end_time = st
		orchestrator.enable_dynamic_ownership(src_host)
		orchestrator.enable_dynamic_ownership(target_host)
	else:
		print "Unknown action: HOW DID I GET HERE ???"
		return (-1,-1)

	# action complete
	if start_time==-1 or end_time==-1:
		print "Oh O what is this."
	print color.YELLOW, "Action Status ACTIVE : %s-%s"%(vnf,action), color.END
	action_time = end_time - start_time

	# figure out if ssh is up on the vnf
	while not orchestrator.check_ssh_up(schain.get_ip_for(vnf, orchestrator)):
		time.sleep(0.5)

	# TODO the routes should be added asap but the host_map may need to be updated for routing to work?
	# add the static routes back
	st = time.time()
	orchestrator.add_routes(vnf,action,schain)
	el = time.time() - st
	print color.RED,"\t\tTime taken to add routes",el, "VNF and Action:",action,vnf, color.END
	timeout = 120 # TODO make it a conf param
	# Update the host_map, which also updates the meta data of VM
	# figure out when the ping is up
	st = time.time()
	while not orchestrator.check_ping_alive(client,'ping_logv.txt'):
		time.sleep(0.5)
		if time.time() - st > timeout:
			break
	while not orchestrator.check_ping_alive(client,'ping_logw.txt'):
		time.sleep(0.5)
		if time.time() - st > timeout:
			break
	orchestrator.stop_ping_in_screen(client,server)
	orchestrator.stop_ping_in_screen(client,server2)
	# get ping values and parse
	downtime = orchestrator.calculate_downtime(client,'ping_logv.txt',action)
	downtime2 = orchestrator.calculate_downtime(client,'ping_logw.txt',action)
	print color.MAGENTA, "Action Time: %f \t Downtimes:"%(action_time), downtime, downtime2, color.END

	# get saved feature vec and prediction vector from schain, or maybe just save the AT and DT to schain and then get it in schedule rehoming
	try:
		schain.add_feature_vec(vnf, action, [action_time, downtime, downtime2])
	except Exception, e:
		print "VNF: %s \t Action: %s"%(vnf,action)
		print str(e)

	schain.resume_periodic_metric_collection(vnf)

	print color.YELLOW, "Action completed for",vnf,color.END
#	return (action_time, downtime)

def schedule_rehoming(vnf_action, schain, vnf_target):
	"""
	:param vnf_action: mapping of actions for each vnf
	:type vnf_action: dict
	:param schain: service chain object
	:type schain: SChain
	:param vnf_target: mapping of targets for each VNF
	:type vnf_target: dict
	"""
	threads=[]
	print "Spawning action threads"
	for vnf in vnf_action:
		thread = threading.Thread( target=perform_action, args = (vnf_action[vnf], vnf, vnf_target[vnf], schain, ))
		thread.daemon = True
		thread.start()
		threads.append(thread)
	for t in threads:
		t.join()
	print color.WHITE,"Action threads returned",color.END
	action_names = {'moverebuild':'RB','migrate':'CM','livemigrate':'LM'}
	comb = ""
	for vnf in vnf_action:
		comb+= "%s_%s-"%(action_names[vnf_action[vnf]],vnf)
	comb = comb.strip('-')
	with open('experiment_results.csv', 'a') as f:
		for vnf in vnf_action:
			print color.DARKCYAN, "%s,%s"%(comb,','.join([str(i) for i in schain.get_feature_pred_act_vector(vnf, vnf_action[vnf])])), color.END
			f.write('%s,%s,%s,%s\n'%(comb,vnf,vnf_action[vnf],','.join([str(i) for i in schain.get_feature_pred_act_vector(vnf, vnf_action[vnf] )])))

	print color.BOLD, color.PURPLE, "Rehoming complete", color.END
	# putting it here maybe
	schain.update_host_map(orchestrator)
	print "Host Map updated"

def get_feasible_combinations(vnf_list, vnf_schain, reduction=1):
	"""
	:param vnf_list: list of VNFs to be rehomed
	:type vnf_list: list[str] if reduction==1 else list[list[str]]
	:param vnf_schain: Mapping of VNFs to their SChain objects
	:type vnf_schain: Dict[str:SChain]
	"""
	# TODO combination is based on reduction factor.
	# Use nCr combinations based on vnf_list sizes of sublists then form the cartesian product.
	print color.MAGENTA, vnf_list, color.END
	if reduction==1:
		ac = [ vnf_schain[v].get_feasible_actions(v) for v in vnf_list ]
		print color.YELLOW, "Feasible actions lists", ac, color.END
		feasible_actions = [ element for element in itertools.product(*ac) ]
		return ([[v for v in vnf_list] for i in range(len(feasible_actions))],feasible_actions)
	else:
		possible_vnfs = []
		for v_list in vnf_list:
			combs = []
			for comb in itertools.combinations(v_list,int(reduction*len(v_list))):
				combs.append(comb)
			possible_vnfs.append(combs)
		partial_vnfs = []
		for part_comb in itertools.product(*possible_vnfs):
			partial_vnfs.append([el for tupl in part_comb for el in tupl])
		feasible_combinations = []
		combination_vnfs = []
		for comb in partial_vnfs:
			ac = [vnf_schain[v].get_feasible_actions(v) for v in comb]
			feasible_actions = [element for element in itertools.product(*ac)]
			feasible_combinations.extend(feasible_actions)
			combination_vnfs.extend([[v for v in comb] for i in range(len(feasible_actions))])
		return (combination_vnfs,feasible_combinations)


def get_vnfs_to_be_moved(schains, hosts, partial=False):
	vnfs_to_move = []
	vnf_schain = {} # map to keep track of schain object for each VNF - later used to get properties from right object
	host_vnfs = defaultdict(list)
	for chain_name in schains:
		if partial:
			ret = schains[chain_name].get_vnfs_per_host(hosts) # host to VNF mapping
			vnfs_in_chain = []
			for h,v in ret.items():
				host_vnfs[h].extend(v)
				vnfs_in_chain.extend(v)
		else:
			vnfs_in_chain = schains[chain_name].get_vnfs_on_hosts(hosts)
			vnfs_to_move.extend(vnfs_in_chain)
		for v in vnfs_in_chain:
			vnf_schain[v] = schains[chain_name]
	if partial:
		vnfs_to_move = [host_vnfs[h] for h in host_vnfs]
	return (vnfs_to_move, vnf_schain) # vnfs_to_move is a list of lists when partial

def rehome_to_host(vnf, target, action, schains):
	"""
	:param vnf: vnf to be migrated
	:type vnf: str
	:param target: target host
	:type target: str
	:param action: action to be performed
	:type action: str
	:param schains: service chain objects
	:type schain: dict of SChain
	"""
	for chain in schains:
		if schains[chain].contains(vnf):
			perform_action(action, vnf, target, schains[chain])
			schains[chain].update_host_map(orchestrator)
			break

def print_combinations(combination_actions, combination_vnfs, combination_costs, combination_delays, combination_downtimes, optimal_index):

	action_names = {'moverebuild':'RB','migrate':'CM','livemigrate':'LM'}

	print color.ORANGE
	print "#####################################################################################"
	print "|\tCombination\t\t\t\t|\tDelay\t\t|\t\tDowntime\t|\tTotal Cost\t|"
	for i,combination in enumerate(combination_actions):
		comb = ""
		for action, vnf in zip(combination, combination_vnfs[i]):
			comb+= "%s_%s-"%(action_names[action],vnf)
		comb = comb.strip('-')
		if i==optimal_index:
			print color.WHITE,
		print "|\t%s\t\t|\t"%comb, combination_delays[i],"\t\t|\t", combination_downtimes[i],"\t|\t", combination_costs[i],"\t|"
		if i==optimal_index:
			print color.ORANGE,
	print "#####################################################################################"
	print color.END
	return

def rehome_vnfs(schains, hosts, merit, partial= False):
	"""
	:param schains: service chain objects
	:type schain: dict of SChain
	:param hosts: list of hostnames
	:type hosts: list
	:param merit: merit object containing cost models
	:type merit: MERIT
	"""
	vnfs_to_move, vnf_schain = get_vnfs_to_be_moved(schains, hosts, partial)
	if len(vnfs_to_move)<1:
		return None
	if partial:
		vnfs_to_move, action_combinations = get_feasible_combinations(vnfs_to_move, vnf_schain, reduction=0.5) # TODO hardcoded for now, parameterize later
	else:
		vnfs_to_move, action_combinations = get_feasible_combinations(vnfs_to_move, vnf_schain) # list of combinations
	print color.BOLD + "REHOMING: %d Combinations identified:\n"%len(action_combinations) + color.END, color.GREEN, action_combinations, color.END
#	return -1
	combination_cost = []
	targets=[]
	vnf_combination_dict = {}
	vnf_action = {}
	n = len(action_combinations)
	combination_delays = []
	combination_downtimes = []
	for j,combination in enumerate(action_combinations):
		vnf_action = dict(zip(vnfs_to_move[j], combination))
		print color.UNDERLINE, color.WHITE, "Evaluating combination %dth of %d:"%(j+1,n), vnf_action, color.END
		vnf_targets = orchestrator.get_candidate_hosts(vnf_action,hosts)
		c_AT , c_DT, rehoming_cost = merit.predict_rehoming_cost(vnf_action,vnf_targets, vnf_schain)
		combination_delays.append(c_AT)
		combination_downtimes.append(c_DT)
		# FORCE SELECTION OF VNF
		if "Firewall" in vnfs_to_move[j]:
			rehoming_cost *=50 # increase cost to discourge selection
		print "Rehoming cost", rehoming_cost
		combination_cost.append(rehoming_cost)
		targets.append(vnf_targets)

	index, cost = min(enumerate(combination_cost), key=operator.itemgetter(1)) # pick combination with minimum cost
	selected_combination = action_combinations[index]

	print_combinations(action_combinations, vnfs_to_move, combination_cost, combination_delays, combination_downtimes, index)

	return (dict(zip(vnfs_to_move[index], selected_combination)), targets[index])


def evacuate_hosts(hosts,chains, merit, partial= False):
	"""
	:param hosts: list of hostnames
	:type hosts: list
	:param chains: service chains in the system
	:type chains: dict
	:param merit: merit object containing cost models
	:type merit: MERIT
	"""
#	hosts = [orchestrator.fqdn(h) for h in hosts]
	# TODO this function and schedule rehoming needs to be properly rewritten for multiple chains
	rehoming_policy = rehome_vnfs(chains, hosts, merit, partial)
	if not rehoming_policy:
		print color.RED, "No VNFs to be rehomed", color.END
		return 0
	for chain_name in chains:
		print color.BOLD+"Rehoming policy for %s : \n"%(chain_name)+color.END, color.YELLOW, rehoming_policy, color.END
		# TODO does not this need to be fixed based on only the vnfs that belong to this chain instead of passing the whole policy
		t = threading.Thread(target = schedule_rehoming, args=(rehoming_policy[0], chains[chain_name], rehoming_policy[1], ))
		t.start()
		t.join() # TODO remove later for multiple chains on system
	return

#@resys.route('/')
#def index():
#	return 'Hello World'

if __name__== "__main__":
	chain_list, merit = sys_init(sys.argv[1],sys.argv[2])
	#resys.run(host='0.0.0.0', port=2002, debug=True)
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	server_address = ('localhost', 2002)
	print >>sys.stderr, 'starting up on %s port %s' % server_address
	sock.bind(server_address)
	# Listen for incoming connections
	try:
		sock.listen(1)
		while True:
	    # Wait for a connection
			print >>sys.stderr, 'waiting for a connection'
	 		connection, client_address = sock.accept()
			try:
				print >>sys.stderr, 'connection from', client_address
				# Receive the data in small chunks and retransmit it
				while True:
					data = connection.recv(1024)
					print >>sys.stderr, 'received "%s"' % data
					if data:
						toks=data.strip().split()
						if toks[0] == 'rehome':
							hosts=[orchestrator.fqdn(i) for i in toks[1:] ]
							connection.send('Starting Evacuation .... ')
							rc = evacuate_hosts(hosts, chain_list, merit, partial = False)
							if rc==0:
								connection.send('Host is empty.\n')
							else:
								connection.send('Rehoming is complete.\n')
						elif toks[0] == 'rehomep':
							hosts=[orchestrator.fqdn(i) for i in toks[1:] ]
							connection.send('Starting Partial Evacuation .... ')
							rc = evacuate_hosts(hosts, chain_list, merit, partial = True)
							if rc==0:
								connection.send('Host is empty.\n')
							else:
								connection.send('Rehoming is complete.\n')
						elif toks[0] == 'rehomed':
							if len(toks)==4:
								vnf_name = toks[1]
								target = orchestrator.fqdn(toks[2])
								action = toks[3]
								rehome_to_host(vnf_name,target,action,chain_list)
								connection.send('Rehoming is complete.\n')
							else:
								connection.send('Incorrect usage.\nUsage: rehomed VNF TARGET ACTION\n')
						else:
							print >>sys.stderr, 'Unknown protocol', client_address
					else:
						print >>sys.stderr, 'Connection closed', client_address
						break
			finally:
				# Clean up the connection
				connection.close()
	finally:
		sock.close()
