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

def mean_low3(data):
#	print sorted(data)[:3]
	return mean(sorted(data)[:3])

def mean_less10k(data):
	filt=[i for i in data if i < 10000]
	if len(filt)>0:
		return mean(filt)
#	print filt
	return 0

def main(fn):
	stats={}
	with open(fn,'r') as profiler_log:
		for line in profiler_log:
			toks=line.strip().split(',')
			try:
				stats[toks[0]]=[int(toks[i]) for i in range(1,len(toks))]
			except:
				stats[toks[0]]=[float(toks[i]) for i in range(1,len(toks))]
	print "%0.2f,%0.2f,%0.2f,%0.2f,%0.2f,%0.2f,%0.2f,%0.2f,%0.2f,%0.2f"%(mean(stats['pdr']),stddev(stats['pdr']),min(stats['pdr']),mean_low3(stats['pdr']),mean(stats['wss']),max(stats['wss']), mean(stats['mwp']),min(stats['mwp']),stats['ws_entropy'][0],stats['nws_entropy'][0])

def parse_profiler_stdin():
	stats={}
	for line in sys.stdin:
		toks=line.strip().split(',')
		try:
			stats[toks[0]]=[int(toks[i]) for i in range(1,len(toks))]
		except:
			stats[toks[0]]=[float(toks[i]) for i in range(1,len(toks))]
	print "%0.2f %0.2f %0.2f %0.2f %0.2f %0.2f %0.2f %0.2f %0.2f %0.2f"%(mean(stats['pdr']),stddev(stats['pdr']),min(stats['pdr']),mean_low3(stats['pdr']),mean(stats['wss']),max(stats['wss']), mean(stats['mwp']),min(stats['mwp']),stats['ws_entropy'][0],stats['nws_entropy'][0])

if __name__ == "__main__":
	if len(sys.argv)>1:
		main(sys.argv[1])
	else:
		parse_profiler_stdin()
