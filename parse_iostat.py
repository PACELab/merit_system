import sys

def mean(data):
	"""Return the sample arithmetic mean of data."""
	n = len(data)
 	if n < 1:
		raise ValueError('mean requires at least one data point')
	return sum(data)/float(n) # in Python 2 use sum(data)/float(n)

def _ss(data):
	"""Return sum of square deviations of sequence data."""
	c = mean(data)
	ss = sum((x-c)**2 for x in data)
	return ss

def stddev(data, ddof=0):
	"""Calculates the population standard deviation
	by default; specify ddof=1 to compute the sample
    standard deviation."""
	n = len(data)
	if n < 2:
		raise ValueError('variance requires at least two data points')
	ss = _ss(data)
	pvar = ss/(n-ddof)
	return pvar**0.5

def parse_iostat_file(fn):
	tps={"sda":[],"sdb":[]}
	reads={"sda":[],"sdb":[]}
	writes={"sda":[],"sdb":[]}
	dict_list=[tps,reads,writes]
	try:
		with open(fn,'r') as f:
			for line in f:
				if line == ' ':
					continue
				toks=line.strip().split()
				sda=toks[1].split(',')
				sdb=toks[2].split(',')
				for i in range(3):
					dict_list[i]["sda"].append(float(sda[i+1]))
					dict_list[i]["sdb"].append(float(sdb[i+1]))
	#			print dict_list
	#			break
		print "%0.2f,%0.2f,%0.2f"%(mean(dict_list[0]['sda']+dict_list[0]['sdb']),mean(dict_list[1]['sda']+dict_list[1]['sdb']),mean(dict_list[2]['sda']+dict_list[2]['sdb']))
	except:
		print "-1,-1,-1"

def parse_iostat_stdin():
	tps={"sda":[],"sdb":[]}
	reads={"sda":[],"sdb":[]}
	writes={"sda":[],"sdb":[]}
	dict_list=[tps,reads,writes]
	try:
		for line in sys.stdin:
			toks=line.strip().split()
			sda=toks[1].split(',')
			sdb=toks[2].split(',')
			for i in range(3):
				dict_list[i]["sda"].append(float(sda[i+1]))
				dict_list[i]["sdb"].append(float(sdb[i+1]))
#			print dict_list
#			break
		print "%0.2f %0.2f %0.2f"%(mean(dict_list[0]['sda']+dict_list[0]['sdb']),mean(dict_list[1]['sda']+dict_list[1]['sdb']),mean(dict_list[2]['sda']+dict_list[2]['sdb']))
	except:
		print "-1 -1 -1"


if __name__=="__main__":
	if len(sys.argv)<2:
		parse_iostat_stdin()
	else:
		parse_iostat_file(sys.argv[1])
