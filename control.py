import sys
from time import sleep
import RPi.GPIO as GPIO
		
GPIO.setmode(GPIO.BCM)

class stepper():

	GRAD_PER_STEP = 0.087890625

	def __init__(self, A, B, C, D ):

		self.A = A
		self.B = B
		self.C = C
		self.D = D

		# Pins aus Ausgaenge definieren
		GPIO.setup(self.A,GPIO.OUT)
		GPIO.setup(self.B,GPIO.OUT)
		GPIO.setup(self.C,GPIO.OUT)
		GPIO.setup(self.D,GPIO.OUT)
		GPIO.output(self.A, False)
		GPIO.output(self.B, False)
		GPIO.output(self.C, False)
		GPIO.output(self.D, False)

		self.time = 0.005
		self.laststep = 0		

		self.steplist = [ self._step1, self._step2, self._step3, self._step4, self._step5, self._step6, self._step7, self._step8 ]

	def _overrun(self):
		if(self.laststep >= 8): self.laststep = 0
		if(self.laststep < 0): self.laststep = 7
		#print( self.laststep )

	def next_step(self):
		
		self._overrun()
		self.steplist[self.laststep]()
		self.laststep += 1
	
	def before_step(self):

		self._overrun()
		self.steplist[self.laststep]()
		self.laststep -= 1

	def forward( self, grad ):

		steps = grad / self.GRAD_PER_STEP
		for i in range( int(steps) ):
			self.next_step()
	
	def reward( self, grad ):

		steps = grad / self.GRAD_PER_STEP
		for i in range( int(steps) ):
			self.before_step()

	# Schritte 1 - 8 festlegen
	def _step1(self):
		GPIO.output(self.D, True)
		sleep(self.time)
		GPIO.output(self.D, False)

	def _step2(self):
		GPIO.output(self.D, True)
		GPIO.output(self.C, True)
		sleep(self.time)
		GPIO.output(self.D, False)
		GPIO.output(self.C, False)

	def _step3(self):
		GPIO.output(self.C, True)
		sleep(self.time)
		GPIO.output(self.C, False)

	def _step4(self):
		GPIO.output(self.B, True)
		GPIO.output(self.C, True)
		sleep(self.time)
		GPIO.output(self.B, False)
		GPIO.output(self.C, False)

	def _step5(self):
		GPIO.output(self.B, True)
		sleep(self.time)
		GPIO.output(self.B, False)

	def _step6(self):
		GPIO.output(self.A, True)
		GPIO.output(self.B, True)
		sleep(self.time)
		GPIO.output(self.A, False)
		GPIO.output(self.B, False)

	def _step7(self):
		GPIO.output(self.A, True)
		sleep(self.time)
		GPIO.output(self.A, False)

	def _step8(self):
		GPIO.output(self.D, True)
		GPIO.output(self.A, True)
		sleep(self.time)
		GPIO.output(self.D, False)
		GPIO.output(self.A, False)


if  __name__ =='__main__':

	sw_on = True

	stepperUpDown = stepper( 18, 23, 24, 25 )
	stepperTurn = stepper( 4, 17, 27, 22 )

	while sw_on:
		c = sys.stdin.read(1)
		if c == 'e': sw_on = False

		stepperUpDown.forward( 90.0 )
		stepperTurn.forward( 90.0 )
		stepperUpDown.reward( 90.0 )
		stepperTurn.reward( 90.0 )

	GPIO.cleanup()
