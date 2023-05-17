from datetime import datetime
from collections import deque
import os
import threading
import time

import RPi.GPIO as GPIO
import PCF8591 as ADC


# PIN SETUP (LOCATION ON EXTENSION BOARD)
RoAPin = 16    # CLK Pin
RoBPin = 20    # DT Pin
BtnPin = 21    # Button Pin



# function takes in set time, sleeps until that time, then activates alarm
def Alarm(alarmTime):
    print("Alarm activated at ", alarmTime, "\n\n")
    while True:
        # check to see if time is current time
        # if so, activate alarm
        now = datetime.now()
        if now == alarmTime:
            # activate alarm
            print("Alarm activated at ", alarmTime, "\n\n")
            # turn off alarm
            break
        else:
            print("alarm thread sleeping")
            time.sleep(5)

def SensorTracking():
    # import sensorLogic.py methods
    with open("sensorLogic.py") as f:
        exec(f.read(), globals())

# this acitvates when user presses button and confirms time.
# runs alarm thread
# runs sensor tracking thread
def ActivateAlarm(alarmTime):
    # This will take confirmed time, make sure it is valid, then run alarm
    # thread and sensor tracking thread

    os.system('clear') # clear screen
    print("\nPillow Alarm Clock.\n-------------------\n\n")
    print("Alarm will activate at ", alarmTime, "\n\n")

    print("Activating Pressure sensor tracking...\n")
    print("Activating Noise Sensor tracking...\n\n")

    print("Press down the encoder to deactivate alarm.\n\n")

    #check to see if time set is valid for today, or change to tomorrow
    now = datetime.now()


    # create thread for alarm
    alarm_thread = threading.Thread(target=Alarm, args=(alarmTime, ))
    alarm_thread.start()

    # create thread for sensor tracking
    sensor_thread = threading.Thread(target=SensorTracking)
    sensor_thread.start()



def setup():
    ADC.setup(0x48)

    # IO settings
    GPIO.setmode(GPIO.BCM)     # Numbers GPIOs by physical location (# location on board)
    GPIO.setup(17, GPIO.OUT)   # Dual LED RED
    GPIO.setup(27, GPIO.OUT)   # Dual LED GREEN

    # Rotary Encoder setup
    GPIO.setup(RoAPin, GPIO.IN)    # input mode
    GPIO.setup(RoBPin, GPIO.IN)
    GPIO.setup(BtnPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)


def inputDisplay(alarmTime):
    os.system('clear') # clear screen
    print("\nPillow Alarm Clock.\n-------------------\n\n")
    print("Please select a time for your alarm by rotating the encoder. \n")
    print("Press the endoder down to confirm your selection. \n")

    print("Set Alarm Time: ", alarmTime)

def inputLoop():
    times = ['%s:%s%s' % (h, m, ap) for ap in ('am', 'pm') for h in ([12] + list(range(1,12))) for m in ('00', '30')]
    d = deque(times); # rotatable list for potentiometer input
    d.rotate(-16) # set initial time to 12:00am

    inputDisplay(d[0]) # print current time to screen

    while True:
        flag = 0
        Last_RoB_Status = 0
        Current_RoB_Status = 0

        Last_RoB_Status = GPIO.input(RoBPin)
        while(not GPIO.input(RoAPin)):
            Current_RoB_Status = GPIO.input(RoBPin)
            flag = 1
        if flag == 1:
            flag = 0
            if (Last_RoB_Status == 0) and (Current_RoB_Status == 1):
                d.rotate(1)
            if (Last_RoB_Status == 1) and (Current_RoB_Status == 0):
                d.rotate(-1)

            inputDisplay(d[0]) # update current time

        if GPIO.input(BtnPin) == GPIO.LOW: # Check whether the button is pressed or not.
            print("Button pressed")
            ActivateAlarm(d[0]) # activate alarm
            break




if __name__ == '__main__':
    try:
        setup()
        inputLoop()
    except KeyboardInterrupt:
        # disable sensors
        GPIO.output(17, GPIO.LOW)
        GPIO.output(27, GPIO.LOW)