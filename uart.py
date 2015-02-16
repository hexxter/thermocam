import serial
import threading

class thermo_layser(threading.Thread):
	
	def __init__(self, serialport="/dev/ttyUSB0", baud=115200, timeout=1):
		threading.Thread.__init__(self)
		self.serialport = serialport
		self.baud = baud
		self.timeout = timeout
		self.stopped = threading.Event()
		self.ser = serial.Serial( self.serialport, self.baud, timeout=self.timeout )
		self.ser.open()
		self.ser.flushInput()
		self.res = bytes()
		self.lock = threading.Lock()
		self.enviroment_temp = 0.0
		self.target_temp = 0.0

	def write(self, txt):
		output = str.encode(txt)
		self.lock.acquire()
		self.ser.write(output)
		self.lock.release()

	def led_on(self):
		self.write('l')

	def led_off(self):
		self.write('n')

	def _parseline(self):
		#line = self.res.decode().replace( '\\x00','' )
		print( self.res.decode() )

	def run(self):
		self.ser.flushInput()
		while not self.stopped.wait(0.001):
			if self.ser.inWaiting() > 0:
				income = self.ser.read(1)
				if income.decode() == '\n':
					self._parseline()
					self.res = bytes()
				else:
					self.res += income
		
		self.ser.close()
						
		
	def stop(self):
		self.stopped.set()


if  __name__ =='__main__':

	import time

	thermo1 = thermo_layser()
	thermo1.start()
	
	thermo1.led_on()
	time.sleep( 60*60*5 )
	thermo1.led_off()
	
	thermo1.stop()
