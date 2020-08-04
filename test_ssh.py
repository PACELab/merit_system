import subprocess, sys, os

vm = sys.argv[1]
try:
	subprocess.check_output('ssh -i ~/graybox.pem ubuntu@%s "ls"'%(vm), shell=True)
except subprocess.CalledProcessError as grepexc:
	print "SSH threw error code", grepexc.returncode, grepexc.output
	print "\t\tVM IP:",vm

