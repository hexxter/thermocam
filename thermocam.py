import RPi.GPIO as GPIO
import sys
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
	
GPIO.setmode(GPIO.BCM)

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
	plt.savefig('heatmap' + date_string + '.png')

if  __name__ =='__main__':
	sw_on = True
	step_count = 90
	lastTemp = 0.0
	data=np.zeros((step_count, step_count))

	#log = open( "log_%f.dat" % time.time(), "w" )

	#list1 = []
	#list2 = []

	stepperUpDown = control.stepper( 18, 23, 24, 25 )
	stepperTurn = control.stepper( 4, 17, 27, 22 )
	
	thermo1 = uart.thermo_layser()
	thermo1.start()
	thermo1.led_on()
	time.sleep( 2 )

	def find_new_data():
		time.sleep( 0.12 )
		thermo1.reset_new_data()
		while not thermo1.is_new_data:
			time.sleep( 0.001 )
		return round(thermo1.target_temp, 2)

	while True:
		c = sys.stdin.read(1)
		if c == 't':
			stepperUpDown.forward( step_count )
			stepperTurn.forward( step_count )
			stepperUpDown.reward( step_count )
			stepperTurn.reward( step_count )
		elif c == 'e':
			break
		elif c == 's':
			starttime = time.time()
			direction = True
			for i in range( step_count ):
				if i > 0:
					if direction:
						#for m in range( len(list1) ):
						#	log.write( list1[m] )
						#log.write( "\n" )
						direction = False
						#list1 = []
					else:
						direction = True
						#for m in range( len(list2) ):
						#	log.write( list2[(len(list2)-1)-m] )
						#log.write( "\n" )
						#list2 = []

					stepperUpDown.forward( 1.0 )

				for n in range( step_count ):
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
						data[(step_count-1)-i,(step_count-1)-n]=tdat
						print( "x:%d y:%d - %.2f" % ( (step_count-1)-i, (step_count-1)-n, tdat ) )
						#list1.append( "%02X" % tdat )
					else:
						data[(step_count-1)-i,n]=tdat
						print( "x:%d y:%d - %.2f" % ( (step_count-1)-i, n, tdat ) )
						#list2.append( "%02X" % tdat )
						
			stepperUpDown.reward( step_count ) 
			render_image( data )
			print( "It takes %f" % (time.time()-starttime) )		
							

	thermo1.led_off()
	
	thermo1.stop()
	#log.close()
	GPIO.cleanup()
