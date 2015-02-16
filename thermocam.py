import RPi.GPIO as GPIO
import sys

import control
import uart
	
GPIO.setmode(GPIO.BCM)

if  __name__ =='__main__':
	sw_on = True

	stepperUpDown = control.stepper( 18, 23, 24, 25 )
	stepperTurn = control.stepper( 4, 17, 27, 22 )
	
	thermo1 = uart.thermo_layser()
	thermo1.start()
	thermo1.led_on()

	while sw_on:
		c = sys.stdin.read(1)
		if c == 'e': sw_on = False

		stepperUpDown.forward( 90.0 )
		stepperTurn.forward( 90.0 )
		stepperUpDown.reward( 90.0 )
		stepperTurn.reward( 90.0 )

	thermo1.led_off()
	
	thermo1.stop()
	GPIO.cleanup()
