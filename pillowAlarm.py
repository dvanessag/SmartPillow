from datetime import datetime, timedelta
from collections import deque
import os
import threading
import time

# RPI Sensor Imports
import RPi.GPIO as GPIO
import PCF8591 as ADC

# PIN SETUP (LOCATION ON EXTENSION BOARD)
RoAPin = 16    # CLK Pin
RoBPin = 20    # DT Pin
BtnPin = 21    # Button Pin

REDLED = 17    # Dual LED RED
BUZZER = 18    # Buzzer Pin

#converts user selected time string to datetime object
def convert_time_string(time_str):
    time_format = "%I:%M%p"
    datetime_obj = datetime.strptime(time_str, time_format)
    return datetime_obj.time()

# function takes in set time, sleeps until that time, then activates alarm
def Alarm(alarmTime):
    current_time = datetime.now().time()
    alarmTime = convert_time_string(alarmTime)

    # if alarm time is less than current time, set alarm for tomorrow
    if alarmTime <= current_time:
        tomorrow = datetime.now() + timedelta(days=1)
        alarmTime = datetime.combine(tomorrow.date(), alarmTime)
    else:
        alarmTime = datetime.combine(datetime.now().date(), alarmTime)


    print("Alarm set for:", alarmTime.strftime("%a %d @ %I:%M%p"), "\n")
    print("Hold down the encoder to deactivate the alarm.\n\n")

    time.sleep(0.5) # timing safety for encoder press (prevents double press)

    while True:
        if GPIO.input(BtnPin) == GPIO.LOW: # Check whether the button is pressed or not.
            print("\n\nAlarm deactivated.\n\n")
            break
        # check to see if time is current time
        # if so, activate alarm
        now = datetime.now()
        if now >= alarmTime:
            os.system('clear') # clear screen
            print("ALARM!!! ", alarmTime, "\n")
            print("Hold down the encoder to deactivate the alarm.\n\n")

            # activate alarm
            buzz.start(50) # start buzzer
            while True:
                GPIO.output(REDLED, GPIO.HIGH)  
                buzz.ChangeFrequency(440)	
                time.sleep(0.5)		
                
                GPIO.output(REDLED, GPIO.LOW)  
                buzz.ChangeFrequency(329)	
                time.sleep(0.5)	

                if GPIO.input(BtnPin) == GPIO.LOW: # Check whether the button is pressed or not.
                    break	

            buzz.stop()
            break
        else:
            time.sleep(1)

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
    print("Activating sensor tracking...\n")


    # create new thread for sensor tracking
    # daemon is true so when main program exits, this thread will exit
    sensor_thread = threading.Thread(target=SensorTracking, daemon=True)
    sensor_thread.start()

    # Main thread runs alarm logic
    Alarm(alarmTime)



def setup():
    ADC.setup(0x48)

    # IO settings
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)     # Numbers GPIOs by physical location (# location on board)
    GPIO.setup(17, GPIO.OUT)   # Dual LED RED
    GPIO.setup(27, GPIO.OUT)   # Dual LED GREEN

    # Rotary Encoder setup
    GPIO.setup(RoAPin, GPIO.IN)    # input mode
    GPIO.setup(RoBPin, GPIO.IN)
    GPIO.setup(BtnPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    # Buzzer setup
    GPIO.setup(BUZZER, GPIO.OUT)
    global buzz 
    buzz = GPIO.PWM(BUZZER, 440) # 440 Hz



def inputDisplay(alarmTime):
    os.system('clear') # clear screen
    print("\nPillow Alarm Clock.\n-------------------\n\n")
    print("Please select a time for your alarm by rotating the encoder. \n")
    print("Press the endoder down to confirm your selection. \n")

    print("Set Alarm Time: ", alarmTime)

def inputLoop():
    testtimes = ['%s:%02d%s' % (h, m, ap) for ap in ('am', 'pm') for h in ([12] + list(range(1, 12))) for m in range(0, 60)]
    times = ['%s:%s%s' % (h, m, ap) for ap in ('am', 'pm') for h in ([12] + list(range(1,12))) for m in ('00','15','30','45')]
    d = deque(testtimes); # rotatable list for potentiometer input
    #d.rotate(-32) # set initial time to 08:00am
    d.rotate(-570) 

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
