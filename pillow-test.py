#!/usr/bin/env python3
import PCF8591 as ADC
import RPi.GPIO as GPIO
import time
from datetime import datetime

# IO settings
GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.OUT)   # Dual LED RED
GPIO.setup(27, GPIO.OUT)   # Dual LED GREEN

GPIO.output(17, GPIO.LOW)  # Set pins to LOW(0V) to off led
GPIO.output(27, GPIO.LOW)  # Set pins to LOW(0V) to off led



def setup():
	ADC.setup(0x48)
	
def soundAction():
	print("@: ", datetime.now())
	GPIO.output(27, GPIO.HIGH)  # Set pin to HIGH to turn on led
	time.sleep(0.5)
	GPIO.output(27, GPIO.LOW)  # Set pin to LOW to turn off led



def loop():
	count = 0
	while True:
		voiceValue = ADC.read(0)
		pressureValue = ADC.read(1)
		
		if pressureValue:
			if pressureValue > 30:
				GPIO.output(17, GPIO.HIGH)  # Set pin to HIGH to turn on led
				print ("Pressure:", pressureValue)
			else:
				GPIO.output(17, GPIO.LOW)
			
		if voiceValue < 50:
			print("\n--Sound Event! (count, value)", count, voiceValue)
			soundAction()
			count += 1

if __name__ == '__main__':
	try:
		setup()
		loop()
	except KeyboardInterrupt: 
		GPIO.output(17, GPIO.LOW)  # Set pin to off
		GPIO.output(27, GPIO.LOW)  # Set pin to off


		pass	
