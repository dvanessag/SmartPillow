#!/usr/bin/env python3
import PCF8591 as ADC
import RPi.GPIO as GPIO
import time
from datetime import datetime

# IO settings
GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.OUT)   # Set pins' mode is output
GPIO.output(17, GPIO.LOW)  # Set pins to LOW(0V) to off led


def setup():
	ADC.setup(0x48)
	
def soundAction():
	print("@: ", datetime.now())
	GPIO.output(17, GPIO.HIGH)  # Set pin to HIGH to turn on led
	time.sleep(0.5)
	GPIO.output(17, GPIO.LOW)  # Set pin to LOW to turn off led



def loop():
	count = 0
	while True:
		voiceValue = ADC.read(0)
		if voiceValue:
			#print ("Value:", voiceValue)
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

		pass	
