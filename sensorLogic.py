#!/usr/bin/env python3
import PCF8591 as ADC
import RPi.GPIO as GPIO
import os
import time
import math
from datetime import datetime

from connection import iothub_send_msg, init_connection

#IO LOCATION VARIABLES
REDLED = 17            # Dual LED RED
GREENLED = 27          # Dual LED GREEN
SOUNDSENSOR = 0        # Sound sensor is on ADC channel 0
PRESSURESENSOR = 1     # Pressure sensor is on ADC channel 1
TEMPERATURESENSOR = 2  # Temperature sensor is on ADC channel 2



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

def printTemperature():
	temperatureValue = ADC.read(TEMPERATURESENSOR)
	Vr = 5 * float(temperatureValue) / 255
	Rt = 10000 * Vr / (5 - Vr)
	temp = 1/(((math.log(Rt / 10000)) / 3950) + (1 / (273.15+25)))
	temp = temp - 273.15
	fixedTemp = float("{:.2f}".format(temp/2))
	print("Temperature: " + str(fixedTemp) + " C")

def sensorloop():
	count = 0
	pressureBool = False
	lastPrintTime = 0


	pressureTotalTime = 0.0
	pressureStartTime = 0.0

	while True:
		voiceValue = ADC.read(SOUNDSENSOR)
		pressureValue = ADC.read(PRESSURESENSOR)

		#only print if 5 seconds have passes
		if time.time() - lastPrintTime >= 5:
			lastPrintTime = time.time()
			printTemperature()

		
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

			#sendEvent("pressure", "timeElapsed", pressureTotalTime)

			pressureBool = False
			GPIO.output(GREENLED, GPIO.LOW)

		else:
			pressureBool = False
			GPIO.output(GREENLED, GPIO.LOW)
			
		# Sound logic:
		# Will send data if sound less than threshold is detected
		if voiceValue < 50:
			count += 1
			#sendEvent("sound", "count", count)


if __name__ == '__main__':
	try:
		setup()
		sensorloop()
	except KeyboardInterrupt: 
		GPIO.output(REDLED, GPIO.LOW)  # Set pin to off
		GPIO.output(GREENLED, GPIO.LOW)  # Set pin to off
		pass	
