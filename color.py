class color:
	PURPLE = '\033[94m'
	CYAN = '\033[96m'
	DARKCYAN = '\033[36m'
	BLUE = '\033[34m'
	GREEN = '\033[92m'
	DARKGREEN = '\033[32m'
	YELLOW = '\033[93m'
	ORANGE = '\033[33m'
	RED = '\033[31m'
	LIGHTRED = '\033[91m'
	WHITE = '\033[97m'
	GRAY = '\033[90m'
	MAGENTA = '\033[35m'
	LIGHTMAGENTA = '\033[95m'
	BOLD = '\033[1m'
	UNDERLINE = '\033[4m'
	END = '\033[0m'

if __name__ == "__main__":
	print color.YELLOW + 'Hello World ! yellow' + color.END
	print color.ORANGE + 'Hello World ! darkyellow' + color.END
	print color.PURPLE + 'Hello World ! purple' + color.END
	print color.CYAN + 'Hello World ! cyan' + color.END
	print color.DARKCYAN + 'Hello World ! darkcyan' + color.END
	print color.BLUE + 'Hello World ! blue' + color.END
	print color.GREEN + 'Hello World ! green' + color.END
	print color.DARKGREEN + 'Hello World ! dark green' + color.END
	print color.RED + 'Hello World ! red' + color.END
	print color.LIGHTRED + 'Hello World ! lightred' + color.END
	print color.WHITE + 'Hello World ! white' + color.END
	print color.MAGENTA + 'Hello World ! magenta' + color.END
	print color.LIGHTMAGENTA + 'Hello World ! lightmagenta' + color.END
	print color.BOLD + 'Hello World ! bold' + color.END
	print color.UNDERLINE + 'Hello World ! underline' + color.END

#	for i in range(0,257):
#		print '\033[38;5;%im'%(i), i , color.END,
#		if i%20==0:
#			print
#	for i in range(0,257):
#		print '\033[%im'%(i), i , color.END,
#		if i%20==0:
#			print
