import csv,sys
from datetime import datetime as dt

#PING 10.10.3.2 (10.10.3.2) 56(84) bytes of data.
#[1578438032.475569] 64 bytes from 10.10.3.2: icmp_seq=1 ttl=62 time=1.88 ms
#[1578438032.675391] 64 bytes from 10.10.3.2: icmp_seq=2 ttl=62 time=1.42 ms
#[1578438032.876311] 64 bytes from 10.10.3.2: icmp_seq=3 ttl=62 time=1.52 ms
#[1578439236.990540] From 10.10.3.2 icmp_seq=4442 Destination Host Unreachable                                                                                                                                                                                                                                                                                     [74/1877]
#[1578439236.990636] From 10.10.3.2 icmp_seq=4443 Destination Host Unreachable
#[1578439286.568815] 64 bytes from 10.10.3.2: icmp_seq=4682 ttl=62 time=5.10 ms
#[1578439286.765406] 64 bytes from 10.10.3.2: icmp_seq=4683 ttl=62 time=1.29 ms
#[1578439286.966164] 64 bytes from 10.10.3.2: icmp_seq=4684 ttl=62 time=1.47 ms

def main(logfile):
	gap=0
	down=False
	first=True
	st_et=[]
	dt_pairs=[]
	lt=-1
	prv_line=-1
	with open(logfile,'r') as lf:
		for line in lf:
			tokens=line.split()
			if tokens[0]=='PING':
				continue
			t = float(tokens[0].strip('[]')) # else it will always be a timestamp

			if first:
				first=False
				st_et.append(t)
			else:
				diff = t-lt
				if diff > 1: # capture possible gaps if bigger than a second
					if "Unreachable" not in line or "Unreachable" not in prv_line: # demorgans for saying if not in either lines
						gap+=diff
			if "Unreachable" in line and not down:
				# record downtime start
				down=True
				dt_pairs.append(t)
			if "bytes" in line and down:
				# ping is back up, record downtime end
				down=False
				dt_pairs.append(lt)
			lt=t
#			prev_icmp_seq = icmp_seq
			prv_line=line

		st_et.append(lt)

	downtime=0
	try:
		for i in range(0,len(dt_pairs),2):
			downtime+=(dt_pairs[i+1]-dt_pairs[i])
	except:
		print "\033[91m", "There was some bad error in ping parsing downtime calculation", "\033[0m"
		downtime=-1
	print "Downtime: %0.2f (unreachable) + %0.2f (gap) = %0.2f"%(downtime,gap,downtime+gap)


if __name__ == "__main__":
	main(sys.argv[1])
