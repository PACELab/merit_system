class color:
	PURPLE = '\033[94m'
	CYAN = '\033[96m'
	DARKCYAN = '\033[36m'
	BLUE = '\033[91m'
	GREEN = '\033[92m'
	YELLOW = '\033[93m'
	RED = '\033[31m'
	WHITE = '\033[97m'
	MAGENTA = '\033[35m'
	BOLD = '\033[1m'
	UNDERLINE = '\033[4m'
	END = '\033[0m'

if __name__ == "__main__":
	print color.BOLD + 'Hello World !' + color.END
	for i in range(0,257):
		print '\033[38;5;%im'%(i), i , color.END,
		if i%20==0:
			print
