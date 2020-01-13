import sys
import csv

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

def parse_mpstat(file):
	mxlist=[]
	nonzlist=[]
	avglist=[]
        metrics = []
	with open(file,'r') as mpfile:
		for line in mpfile:
			toks=line.strip().split(',')
			mxlist.append(float(toks[1]))
			nonzlist.append(float(toks[2]))
			avglist.append(float(toks[3]))
	print "%0.2f,%0.2f"%(mean(avglist),stddev(avglist))
	return (mean(avglist),stddev(avglist))
#	metrics.append(mean(avglist))
#	metrics.append(stddev(avglist))
#	with open("training_data.csv", "a") as csvfile:
#		filewriter = csv.writer(csvfile)
#		filewriter.writerow(["avm", metrics[0]])
#		filewriter.writerow(["avs", metrics[1]])

def parse_mpstat_stdin():
	mxlist=[]
	nonzlist=[]
	avglist=[]
        metrics = []
# with open(file,'r') as mpfile:
	for line in sys.stdin:
		toks=line.strip().split(',')
		mxlist.append(float(toks[1]))
		nonzlist.append(float(toks[2]))
		avglist.append(float(toks[3]))
	print "%0.2f %0.2f"%(mean(avglist),stddev(avglist))


if __name__=="__main__":
	if len(sys.argv) < 2:
		parse_mpstat_stdin()
	else:
		parse_mpstat(sys.argv[1])
