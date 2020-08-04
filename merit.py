import pprint
import numpy as np
from sklearn import preprocessing
from sklearn import svm
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import KFold
from scipy.stats.mstats import gmean
from sklearn.neural_network import MLPRegressor
from sklearn.metrics import r2_score
from sklearn.metrics import recall_score
from sklearn.metrics import precision_score
import time
from timeit import default_timer as timer
from statistics import mean, median
from collections import defaultdict
from sklearn.covariance import EllipticEnvelope
from sklearn.svm import OneClassSVM
import pickle
import sys, os
import warnings
import random
from color import color

class MERIT:
	def __init__(self, chain_list, orchesterator):
		self.features = {}
		with open('merit.ini','r') as conf_file:
			for line in conf_file:
				toks = line.strip().split()
				self.features[toks[0]] = toks[1:]
		print self.features
		# TODO check if model files are present?
		# TODO if model files not available, then train and save. AT and DT separate. Maybe shared vs NS?
		self.available_actions = self.features.keys()
		self.orch = orchesterator
                #self.create_feature_vec(chain_list)
		self.actiontime_model = {}
		self.downtime_model = {}

		for k in self.available_actions:
			with open('model_%s_shared_AT.pkl'%(k),'rb') as fid:
				self.actiontime_model[k] = pickle.load(fid)
			with open('model_%s_shared_DT.pkl'%(k),'rb') as fid:
				self.downtime_model[k] = pickle.load(fid)


	def do_predict(self,action,feature_vec):
		at_m, at_xscaler, at_yscaler = self.actiontime_model[action] # 3-tuple, list
		dt_m, dt_xscaler, dt_yscaler = self.downtime_model[action] #

		data = np.array(feature_vec)
		data = data.reshape(1,-1)

		at_X_s = at_xscaler.transform(data)
		dt_X_s = dt_xscaler.transform(data)

		at_prd = at_m.predict(at_X_s)
		dt_prd = dt_m.predict(dt_X_s)

		at_prd = at_yscaler.inverse_transform(at_prd)
		dt_prd = dt_yscaler.inverse_transform(dt_prd)

		return (at_prd[0], max(dt_prd[0],0.1))

	def do_modeling(self,actions,data_files,pref_model):
		# TODO This code will be a slightly modified version of do_regression from local copy
		# use prebuilt models for now
		pass

	def remove_outliers(self,X):
		classifiers = {
			"Empirical Covariance": EllipticEnvelope(support_fraction=.99,
														contamination=0.1),
			"Robust Covariance (Minimum Covariance Determinant)":
					EllipticEnvelope(support_fraction=.8, contamination=0.1),
			"OCSVM": OneClassSVM(nu=0.1, gamma=0.001)}

		predictions={}
		# Learn a frontier for outlier detection with several classifiers
		for i, (clf_name, clf) in enumerate(classifiers.items()):
			clf.fit(X)
			y_prd=clf.predict(X)
			predictions[i]=y_prd
			print("\tOutliers",sum(y_prd==-1))
			print("\tInliers",sum(y_prd==1))
		y_prd=predictions[0]
		return y_prd==1

	def load_data(self,dataset_path):
		with open(dataset_path, 'r') as fp:
			rows = fp.readlines()
			schema = rows[0].strip().split(',')
			rows = rows[1:]
			rows = np.array([[float(v) for v in row.strip().split(',')] for row in rows])

		return rows[:,[-2,-1]] # only using last feature and label for outliers


	def load_dataset(self,dataset_path):
	    with open(dataset_path, 'r') as fp:
	        rows = fp.readlines()
	        schema = rows[0].strip().split(',')
	        rows = rows[1:]
	        rows = np.array([[float(v) for v in row.strip().split(',')] for row in rows])

	    X=rows[:,:-1]
	    y=rows[:,-1]
	    return schema, X, y

	def load_datasetX(self,dataset_path):
	    with open(dataset_path, 'r') as fp:
	        rows = fp.readlines()
	        schema = rows[0].strip().split(',')
	        rows = rows[1:]
	        rows = np.array([[float(v) for v in row.strip().split(',')] for row in rows])

	    return schema, rows

	def predict_rehoming_cost(self, vnf_actions, vnf_targets, vnf_schain):
#		return random.randint(0, 20) # Generate a random cost to test out different actions
		# to predict costs, we need the feature vecs

		# get vnf_prop dictionary with all the required data for each VNF
		vnfs_props = {}
		for vnf in vnf_actions:
			vnfs_props[vnf] = vnf_schain[vnf].get_vnf_prop(vnf,self.orch)
		# create feature vec, call do predict on everyone of the VNF
		AT_preds = {}
		DT_preds = defaultdict(int)
		for vnf in vnf_actions:
			fv = self.create_feature_vec(vnfs_props[vnf], vnf_actions[vnf], vnfs_props, vnf_actions, vnf_targets)
			print color.YELLOW, "Feature vector created for %s: "%(vnf), " and action: %s"%(vnf_actions[vnf]), fv, color.END
			p_at, p_dt = self.do_predict(vnf_actions[vnf],fv)
			AT_preds[vnf] = p_at
			DT_preds[vnf] = p_dt
			print color.GREEN, "Predicted costs: AT=%0.2f\tDT=%0.2f"%(p_at,p_dt), color.END
			# store in schain as well
			vnf_schain[vnf].set_feature_vec(vnf, vnf_actions[vnf], fv)
			vnf_schain[vnf].add_feature_vec(vnf, vnf_actions[vnf], [p_at, p_dt])

		# combination rehoming cost is then sum(AT) and max(DT)
		comb_AT = sum(AT_preds.values())
		comb_DT = []
		# identify unique paths for DT: identify unique chains involved, for each chain find the number of unique paths
		uniq_chains = set(vnf_schain.values())
		for chain in uniq_chains:
			paths = chain.get_dt_paths()
			paths_DT = []
			for path in paths:
				path_DT = max([DT_preds[i] for i in path])
				paths_DT.append(path_DT)
			print color.DARKCYAN, "\tTwo predicted Downtimes are:", paths_DT, color.END
			comb_DT.append(sum(paths_DT)/len(paths_DT)) # average DT across chain
		print color.YELLOW, "Combination costs \n\tAT=%0.2f\tDT="%(comb_AT),comb_DT,color.END
		# chain rehoming cost is sum(AT)*max(DT)
		return (comb_AT,comb_DT,self.orch.calculate_rehoming_cost(comb_AT,comb_DT)) # orchesterator provided generic cost function

	def create_feature_vec(self, vnf_prop, action, other_vnfs_prop, other_actions, vnf_targets):
		# TODO use predefined configuration feature vec keys to extract the corresponding values from vnf_prop
		# and in case of BW features: check the other_vnfs_actions if they contend with the action of this VM
		# in case of contention, estimate BW and related features using the other_vnfs_prop
		vec = []
		calc_bw = -1
		for f in self.features[action]: # list of ordered features
			if f == 'bw':
				# check if other actions and targets affect BW, if they do calculate using formula
				# same target or same source -
				# MR does not cause contention, CM causes contention and LM causes contention
				# state sizes: CM - disk, LM - RAM
				cur_vnf = vnf_prop['vnf_name']
				if action=='moverebuild':
					calc_bw = min(self.orch.get_bw_at_host(vnf_prop['src_host'],'out'),self.orch.get_bw_at_host(vnf_targets[cur_vnf],'in'))
					vec.append(calc_bw)
				elif action=='migrate':
					cur_state_size = vnf_prop['disk']
					n_cmn = 1
					state_sizes = []
					for v, ov_prop in other_vnfs_prop.items():
						# other vnfs doing CM
						if v!=cur_vnf and other_actions[v]=='migrate':
							n_cmn += 1
							if ov_prop['disk']<=cur_state_size:
								state_sizes.append(ov_prop['disk'])
					try:
						factor = float(cur_state_size) / (sum(state_sizes) + (n_cmn - len(state_sizes))*cur_state_size )
					except ZeroDivisionError as error:
						print color.WHITE, "Division by zero detected - create_feature_vec CM", color.END
						factor = 1
					print color.GREEN, "Cold Migrate Factor: %0.2f "%(factor), color.END
					calc_bw = min( self.orch.get_bw_at_host('cp-1','out')*factor , self.orch.get_bw_at_host('cp-1','in')*factor)
					vec.append(calc_bw)

				elif action=='livemigrate':
					n_cmn_src = n_cmn_dst = 1
					state_sizes_src = []
					state_sizes_dst = []
					cur_state_size = vnf_prop['mem']
					print "-- my state size:",cur_state_size

					for v, ov_prop in other_vnfs_prop.items():
						# other vnfs with same SRC host and doing LM
						if v!=cur_vnf and vnf_prop['src_host']==ov_prop['src_host'] and other_actions[v]=='livemigrate':
							n_cmn_src += 1
							if ov_prop['mem']<=cur_state_size:
								state_sizes_src.append(ov_prop['mem'])

						# other vnfs with same DST host and doing LM
						if v!=cur_vnf and vnf_targets[cur_vnf]==vnf_targets[v] and other_actions[v]=='livemigrate':
							n_cmn_dst += 1
							if ov_prop['mem']<=cur_state_size:
								state_sizes_dst.append(ov_prop['mem'])

					print color.CYAN, "SRC state sizes: \n", color.GREEN, state_sizes_src, color.CYAN, "DST state sizes: \n", color.GREEN, state_sizes_dst, color.END

					try:
						src_factor = float(cur_state_size) / (sum(state_sizes_src) + (n_cmn_src - len(state_sizes_src))*cur_state_size )
					except ZeroDivisionError as error:
						print color.WHITE, "Division by zero detected - create_feature_vec LM", color.END
						src_factor = 1

					try:
						dst_factor = float(cur_state_size) / (sum(state_sizes_dst) + (n_cmn_dst - len(state_sizes_dst))*cur_state_size )
					except ZeroDivisionError as error:
						print color.WHITE, "Division by zero detected - create_feature_vec LM", color.END
						dst_factor = 1

					print color.GREEN, "LM SRC F: %0.2f -- DST F: %0.2f "%(src_factor,dst_factor), color.END
					calc_bw = min(self.orch.get_bw_at_host(vnf_prop['src_host'],'out')*src_factor , self.orch.get_bw_at_host(vnf_targets[cur_vnf],'in')*dst_factor)
					vec.append(calc_bw)
				else:
					print color.RED, "Unkown Action in create_feature_vec", color.END
			elif f == 'pdr/bw':
				# simple division, by this point BW should already be calculated
				vec.append(vnf_prop['pdrmin']/calc_bw)
			elif f == 'disk/bw':
				vec.append(vnf_prop['disk']/calc_bw)
			else:
				vec.append(vnf_prop[f])

		#print color.MAGENTA, "Feature Vector for",cur_vnf," : ", vec, color.END

		return vec

if __name__ == "__main__":
	m = MERIT()
