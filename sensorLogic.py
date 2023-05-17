#!/usr/bin/env python3
import PCF8591 as ADC
import RPi.GPIO as GPIO
import time
from datetime import datetime

from connection import iothub_send_msg, init_connection

#IO LOCATION VARIABLES
REDLED = 17
GREENLED = 27
SOUNDSENSOR = 0    # Sound sensor is on ADC channel 0
PRESSURESENSOR = 1 # Pressure sensor is on ADC channel 1


def setup():
	init_connection() # Connect to Azure IoT Hub

	ADC.setup(0x48) # Analogue to digital IO for sound sensor
	# IO settings
	GPIO.setmode(GPIO.BCM)
	GPIO.setup(REDLED, GPIO.OUT)   # Dual LED RED
	GPIO.setup(GREENLED, GPIO.OUT)   # Dual LED GREEN


def sendEvent(eventType, dataType, data):
	eventTime = datetime.now()

	iothub_send_msg(eventType, eventTime, dataType, data)

	time.sleep(0.5)

def sensorloop():
	count = 0
	pressureBool = False

	pressureTotalTime = 0.0
	pressureStartTime = 0.0

	while True:
		voiceValue = ADC.read(SOUNDSENSOR)
		pressureValue = ADC.read(PRESSURESENSOR)
		
		# Pressure logic:
		# Will send data if pressure is taken off of sensor (disturbance)
		if pressureValue > 30:
			if pressureBool == False:
				pressureStartTime = time.time()

			pressureBool = True 
			GPIO.output(GREENLED, GPIO.HIGH)  # Set pin to HIGH to turn on led

		elif pressureValue < 30 and pressureBool == True:
			# Calculate time elapsed since pressureBool was set to True
			elapsed_time = time.time() - pressureStartTime
			pressureTotalTime += elapsed_time

			sendEvent("pressure", "timeElapsed", pressureTotalTime)

			pressureBool = False
			GPIO.output(GREENLED, GPIO.LOW)

		else:
			pressureBool = False
			GPIO.output(GREENLED, GPIO.LOW)
			
		# Sound logic:
		# Will send data if sound less than threshold is detected
		if voiceValue < 50:
			count += 1
			sendEvent("sound", "count", count)


if __name__ == '__main__':
	try:
		setup()
		sensorloop()
	except KeyboardInterrupt: 
		GPIO.output(REDLED, GPIO.LOW)  # Set pin to off
		GPIO.output(GREENLED, GPIO.LOW)  # Set pin to off
		pass	
