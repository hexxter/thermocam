import termios, sys, os
#import termios, TERMIOS, sys, os
TERMIOS = termios
def getkey():
	fd = sys.stdin.fileno()
	old = termios.tcgetattr(fd)
	new = termios.tcgetattr(fd)
	new[3] = new[3] & ~TERMIOS.ICANON & ~TERMIOS.ECHO
	new[6][TERMIOS.VMIN] = 1
	new[6][TERMIOS.VTIME] = 0
	termios.tcsetattr(fd, TERMIOS.TCSANOW, new)
	c = None
	try:
		c = os.read(fd, 1)
	finally:
		termios.tcsetattr(fd, TERMIOS.TCSAFLUSH, old)
	try:
		res = c.decode()
	except UnicodeDecodeError as e:
		res = ""

	return res



if __name__ == '__main__':
        print('type something')
        s = ''
        while 1:
                c = getkey()
                if c == '\n':     ## break on a Return/Enter keypress
                        break
                print( 'got', c )
                s = s + c
        print(s)
