import serial
import threading

class thermo_layser(threading.Thread):
	
	def __init__(self, serialport="/dev/ttyUSB0", baud=115200, timeout=None):
		threading.Thread.__init__(self)
		self.serialport = serialport
		self.baud = baud
		self.timeout = timeout
		self.stopped = threading.Event()
		self.ser = serial.Serial( self.serialport, self.baud, timeout=self.timeout )
		self.ser.open()
		self.res = bytes()
		self.lock = threading.Lock()
		self.enviroment_temp = 0.0
		self.target_temp = 0.0
		self.new_data = False

	def write(self, txt):
		output = str.encode(txt)
		self.lock.acquire()
		self.ser.write(output)
		self.lock.release()

	def led_on(self):
		self.write('l')

	def led_off(self):
		self.write('n')

	def reset_new_data(self):
		self.lock.acquire()
		self.new_data = False
		self.lock.release()

	def is_new_data(self):
		return self.new_data

	def _parseline(self):
		line = self.res.decode().replace( '\r', '' )
		data = line.split( ";" )
		self.lock.acquire()
		try:
			self.target_temp = float(data[1])
			self.enviroment_temp = float(data[2])
			self.new_data = True
		except (ValueError, IndexError) as e:
			self.new_data = False
			print( e )
			
		self.lock.release()

	def run(self):
		self.ser.flushInput()
		firstinput = True
		while not self.stopped.wait(0.001):
			income = self.ser.read()
			if '\n' in income.decode():
				if firstinput:
					firstinput = False
					self.res = bytes()
				else:
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

	oldtime = time.time()	

	thermo1.led_on()
	for i in range( 10000 ):
		if thermo1.is_new_data():
			thermo1.reset_new_data()
			print( "target: %f env: %f time delta: %f" % (thermo1.target_temp, thermo1.enviroment_temp, time.time()-oldtime) )
			oldtime = time.time()
		time.sleep( .002 )
	thermo1.led_off()
	
	thermo1.stop()
