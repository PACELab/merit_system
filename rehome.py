import pickle
import sys, os, threading, time
import warnings, socket, operator, itertools
from SChain import SChain
from merit import MERIT
from ROrc import ROrc
from color import color

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

	print color.PURPLE, "Rehoming %s VNF to %s using %s"%(vnf, target_host, action), color.END

	client = schain.get_client_endpoint(orchestrator)
	server = schain.get_server_endpoint(orchestrator)
#	vnf_data = orchestrator.get_vnf_metrics(vnf, action, schain)  # Get the initial metrics for the vnf and update vnf properties
#	schain.vnfs[vnf]['metrics'] = vnf_data
#	hostname_metrics = {}
#	if action == 'moverebuild':   # Passing an additional argument of fetch as workaround for nova show not getting the right field
#		host_data = orchestrator.get_monitoring_metrics(vnf, target_host, action, 5)          # Get host specific metrics and add to dict
#	else:
#		host_data = orchestrator.get_monitoring_metrics(vnf, target_host, action)          # Get host specific metrics and add to dict
#	hostname_metrics[target_host] = host_data

	# changes here for multiple downtimes - maybe server endpoint returns multiple points
	orchestrator.start_ping_in_screen(client,server,'ping_log.txt')
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

	action_time = end_time - start_time

	# figure out if ssh is up on the vnf
	while not orchestrator.check_ssh_up(schain.get_ip_for(vnf, orchestrator)):
		time.sleep(0.5)

	# TODO the routes should be added asap but the host_map may need to be updated for routing to work?
	# add the static routes back
	orchestrator.add_routes(vnf,action,schain)
	# Update the host_map, which also updates the meta data of VM
	schain.update_host_map(orchestrator)
	# figure out when the ping is up
	while not orchestrator.check_ping_alive(client):
		time.sleep(0.5)
	orchestrator.stop_ping_in_screen(client,server)
	# get ping values and parse
	downtime = orchestrator.calculate_downtime(client,'ping_log.txt',action)


	# get saved feature vec and prediction vector from schain, or maybe just save the AT and DT to schain and then get it in schedule rehoming
	schain.add_feature_vec(vnf, [action_time, downtime])

#	vnf_data = orchestrator.get_vnf_metrics(vnf, action, schain)
#	schain.vnfs[vnf]['metrics'] = vnf_data
#
#	hostname_metrics = {}
#	if action == 'moverebuild':   # Passing an additional argument of fetch as workaround for nova show not getting the right field
#		host_data = orchestrator.get_monitoring_metrics(vnf, target_host, action, 5)
#	else:
#		host_data = orchestrator.get_monitoring_metrics(vnf, target_host, action)           # Get updated host metrics after the action and update the dict
#	hostname_metrics[target_host] = host_data
#
#	host_data.append(action_time)
#	host_data.append(downtime)
#
#	orchestrator.generate_training_data(host_data)            # Write the host metrics and action time, downtime to the file
	return (action_time, downtime)

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
		thread.start()
		threads.append(thread)
	for t in threads:
		t.join()

	# TODO form combination, get feature vectors from schain and save to file as a comb
	action_names = {'moverebuild':'RB','migrate':'CM','livemigrate':'LM'}
	comb = ""
	for vnf in vnf_action:
		comb+= "%s_%s-"%(action_names[vnf_action[vnf]],vnf)
	comb = comb.strip('-')
	with open('experiment_results.csv', 'a') as f:
		for vnf in vnf_action:
			print color.DARKCYAN, "%s,%s"%(comb,','.join([str(i) for i in schain.get_feature_pred_act_vector(vnf)])), color.END
			f.write('%s,%s,%s,%s\n'%(comb,vnf,vnf_action[vnf],','.join([str(i) for i in schain.get_feature_pred_act_vector(vnf)])))
	print color.BOLD, color.PURPLE, "Rehoming complete", color.END

def get_feasible_combinations(vnf_list, vnf_schain):
	print color.MAGENTA, vnf_list, color.END
	ac = [ vnf_schain[v].get_feasible_actions(v) for v in vnf_list ]
	print color.YELLOW, "Feasible actions lists", ac, color.END
	feasible_actions = [ element for element in itertools.product(*ac) ]
	return feasible_actions


def rehome_vnfs(schains, hosts, merit):
	"""
	:param schains: service chain objects
	:type schain: list of SChain
	:param hosts: list of hostnames
	:type hosts: list
	:param merit: merit object containing cost models
	:type merit: MERIT
	"""
	vnfs_to_move = []
	vnf_schain = {} # map to keep track of schain object for each VNF - later used to get properties from right object
	for chain_name in schains:
		vnfs_in_chain = schains[chain_name].get_vnfs_on_hosts(hosts)
		vnfs_to_move.extend(vnfs_in_chain)
		for v in vnfs_in_chain:
			vnf_schain[v] = schains[chain_name]
	if len(vnfs_to_move)<1:
		return None
	action_combinations = get_feasible_combinations(vnfs_to_move, vnf_schain) # list of combinations
	print color.BOLD + "REHOMING: %d Combinations identified:\n"%len(action_combinations) + color.END, color.GREEN, action_combinations, color.END
	combination_cost = []
	targets=[]
	vnf_combination_dict = {}
	vnf_action = {}
	for combination in action_combinations:
		vnf_action = dict(zip(vnfs_to_move, combination))
		print color.UNDERLINE, color.WHITE, "Evaluating combination:", vnf_action, color.END
		vnf_targets = orchestrator.get_candidate_hosts(vnf_action,hosts)
		rehoming_cost = merit.predict_rehoming_cost(vnf_action,vnf_targets, vnf_schain)
		print "Rehoming cost", rehoming_cost
		combination_cost.append(rehoming_cost)
		targets.append(vnf_targets)

	index, cost = min(enumerate(combination_cost), key=operator.itemgetter(1)) # pick combination with minimum cost
	selected_combination = action_combinations[index]

	return (dict(zip(vnfs_to_move, selected_combination)), targets[index])


def evacuate_hosts(hosts,chains, merit):
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
	rehoming_policy = rehome_vnfs(chains, hosts, merit)
	if not rehoming_policy:
		print color.RED, "No VNFs to be rehomed", color.END
		return 0
	for chain_name in chains:
		print color.BOLD+"Rehoming policy for %s : \n"%(chain_name)+color.END, color.YELLOW, rehoming_policy, color.END
		# TODO does not this need to be fixed based on only the vnfs that belong to this chain instead of passing the whole policy
		t = threading.Thread(target = schedule_rehoming, args=(rehoming_policy[0], chains[chain_name], rehoming_policy[1], ))
		t.start()
		t.join() # TODO remove later
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
							# TODO make sure the hosts have fqdn
							rc = evacuate_hosts(hosts, chain_list, merit)
							if rc==0:
								connection.send('Host is empty')
							else:
								connection.send('Rehoming in progress')
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
