import sys
from datetime import datetime

def getTimeDiff(end_timestamp, start_timestamp):
	fmt = '%H:%M:%S'
	end_time_stamp_fmt = datetime.strptime(end_timestamp, fmt)
	start_time_stamp_fmt = datetime.strptime(start_timestamp, fmt)
	return int(round((end_time_stamp_fmt - start_time_stamp_fmt).total_seconds()))

def checkHigh(network_traffic, threshold):
	if int(network_traffic[-1]) > threshold:
		return -1
	elif int(network_traffic[-2]) > threshold:
		return -2
	elif int(network_traffic[-3]) > threshold:
		return -3
	elif int(network_traffic[-4]) > threshold:
		return -4
	return 0

def getCol(index):
	if index == -1:
		return "last"
	elif index == -2:
		return "second_last"
	elif index == -3:
		return "third_last"
	elif index == -4:
		return "fourth_last"
	return "ERROR!"

if len(sys.argv) < 2:
	print("File name not provides")
	sys.exit()

file_name = sys.argv[1]

f = open(file_name, "r")

lines = f.readlines()
threshold = 500
start_timestamp, start_recording  = None, 0
index = 0

with open(file_name, 'r') as f:
	for line in f:
		line_contents = line.split()
		if start_recording == 0:
			index = checkHigh(line_contents, threshold)
			if index < 0:
				start_timestamp = line_contents[0]
				start_recording = 1
		elif start_recording == 1:
			if int(line_contents[index]) < threshold:
				print(getCol(index), ":", start_timestamp, line_contents[0], getTimeDiff(line_contents[0], start_timestamp))
				start_timestamp = None
				start_recording = 0
				index = 0
