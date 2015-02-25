#!/usr/bin/env python
from twisted.internet import reactor
from txosc import osc
from txosc import dispatch
from txosc import async

import RPi.GPIO as GPIO
import sys
import os
import time
from datetime import datetime
import math

import numpy as np
import matplotlib as mpl

# we are running headless, use "Agg" as backend for matplotlib
mpl.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.cm as cm

import control
import uart
import key

GPIO.setmode(GPIO.BCM)

res_list = [ [50,50], [90,90], [50,90], [180,50], [180,90], [360,90] ]
res = res_list[0]
	
lastTemp = 0.0
data=np.zeros((res[0], res[1]))

stepperUpDown = control.stepper( 18, 23, 24, 25 )
stepperTurn = control.stepper( 4, 17, 27, 22 )

thermo1 = uart.thermo_layser()
thermo1.start()
thermo1.led_on()
time.sleep( 2 )

def render_image( data ):
	# Generate heatmap from data array
	cmap = cm.get_cmap('jet')
	plt.clf()
	plt.imshow(data, interpolation="nearest", cmap=cmap)
	plt.axis('off')
	# add temp colorbar
	cb = plt.colorbar()
	date_disp = datetime.now().strftime("%Y-%m-%d  %H:%M")
	cb.set_label('Temp (in C)  ' + date_disp)

	date_string = datetime.now().strftime("%Y-%m-%d--%H-%M")
	plt.savefig('static/heatmap' + date_string + '.png')

def find_new_data():
	time.sleep( 0.12 )
	thermo1.reset_new_data()
	while not thermo1.is_new_data:
		time.sleep( 0.001 )
	return round(thermo1.target_temp, 2)

def do( prog ):
	global lastTemp
	global data
	data=np.zeros((res[0], res[1]))

	if prog == 't':
		stepperUpDown.forward( res[1] )
		stepperTurn.forward( res[0] )
		stepperUpDown.reward( res[1] )
		stepperTurn.reward( res[0] )
	elif prog == 'w':
		stepperUpDown.forward( 1 )
	elif prog == 'a':
		stepperTurn.forward( 1 )
	elif prog == 's':
		stepperUpDown.reward( 1 )
	elif prog == 'd':
		stepperTurn.reward( 1 )
	elif prog == 'e':
		thermo1.led_off()
		thermo1.stop()
		GPIO.cleanup()
		os.system("sudo shutdown -h now")
		sys.exit()
	elif prog == 'p':
		starttime = time.time()
		direction = True
		for i in range( res[0] ):
			if i > 0:
				if direction:
					direction = False
				else:
					direction = True

				stepperUpDown.forward( 1.0 )

			for n in range( res[1] ):
				if n > 0:
					if direction:
						stepperTurn.forward( 1.0 )
					else:
						stepperTurn.reward( 1.0 )
				else: 
					lastTemp=find_new_data()
					
				tdat=find_new_data()
				while math.fabs(tdat-lastTemp) > 0.8:
					print( "repeat" )
					lastTemp = tdat
					tdat=find_new_data()
					
				if direction:
					data[(res[0]-1)-i,(res[1]-1)-n]=tdat
					print( "x:%d y:%d - %.2f" % ( (res[0]-1)-i, (res[1]-1)-n, tdat ) )
				else:
					data[(res[0]-1)-i,n]=tdat
					print( "x:%d y:%d - %.2f" % ( (res[0]-1)-i, n, tdat ) )
					
		stepperUpDown.reward( res[1] ) 
		render_image( data )
		print( "It takes %f" % (time.time()-starttime) )		
							
def up_down_handler(message, address):
    if message.getValues()[0] == 1:
	do( "w" )
    else:
	do( "s" )

def turn_handler(message, address):
    if message.getValues()[0] == 1:
	do( "d" )
    else:
	do( "a" )

def test_handler(message, address):
    if message.getValues()[0] == 1:
	do( "t" )
def scan_handler(message, address):
    if message.getValues()[0] == 1:
	do( "p" )
def shutdown_handler(message, address):
    if message.getValues()[0] == 1:
	do( "e" )

def resolution1_handler(message, address):
    do_resolution( 1, message.getValues()[0] )
def resolution2_handler(message, address):
    do_resolution( 2, message.getValues()[0] )
def resolution3_handler(message, address):
    do_resolution( 3, message.getValues()[0] )
def resolution4_handler(message, address):
    do_resolution( 4, message.getValues()[0] )
def resolution5_handler(message, address):
    do_resolution( 5, message.getValues()[0] )
def resolution6_handler(message, address):
    do_resolution( 6, message.getValues()[0] )
def resolution7_handler(message, address):
    do_resolution( 7, message.getValues()[0] )

def do_resolution( num, sw ):
    print( "num: %d sw: %d res:%s" % ( num, sw, res_list[num-1] ) )
    if sw == 1:
	global res
        res = res_list[num-1]

class UDPReceiverApplication(object):
    """
    Example that receives UDP OSC messages.
    """
    def __init__(self, port):
        self.port = port
        self.receiver = dispatch.Receiver()
        self._server_port = reactor.listenUDP(self.port, async.DatagramServerProtocol(self.receiver))
        print("Listening on osc.udp://localhost:%s" % (self.port))
        self.receiver.addCallback("/thermocam/1/up_down", up_down_handler)
        self.receiver.addCallback("/thermocam/1/turn", turn_handler)
        self.receiver.addCallback("/thermocam/1/test_scan", test_handler)
        self.receiver.addCallback("/thermocam/1/scan", scan_handler)
        self.receiver.addCallback("/thermocam/1/shutdown", shutdown_handler)
        self.receiver.addCallback("/thermocam/1/resolution/1/*", resolution1_handler)
        self.receiver.addCallback("/thermocam/1/resolution/2/*", resolution2_handler)
        self.receiver.addCallback("/thermocam/1/resolution/3/*", resolution3_handler)
        self.receiver.addCallback("/thermocam/1/resolution/4/*", resolution4_handler)
        self.receiver.addCallback("/thermocam/1/resolution/5/*", resolution5_handler)
        self.receiver.addCallback("/thermocam/1/resolution/6/*", resolution6_handler)
        self.receiver.addCallback("/thermocam/1/resolution/7/*", resolution7_handler)

if __name__ == "__main__":
    app = UDPReceiverApplication(7700)
    reactor.run()

