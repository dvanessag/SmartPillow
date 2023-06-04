# Install below packages
'''
sudo pip3 install azure-iot-device
sudo pip3 install azure-iot-hub
sudo pip3 install azure-iothub-service-client
sudo pip3 install azure-iothub-device-client
'''

# Run below on Azure CLI
'''
#### below to add extension
az extension add --name azure-cli-iot-ext

### Below to start device monitor to check incoming telemetry data
az iot hub monitor-events --hub-name smartPillow --device-id raspberryDi

'''
import random
import time

# Using the Python Device SDK for IoT Hub:
#   https://github.com/Azure/azure-iot-sdk-python
# The sample connects to a device-specific MQTT endpoint on your IoT Hub.
from azure.iot.device import IoTHubDeviceClient, Message

# The device connection string to authenticate the device with your IoT hub.
# Using the Azure CLI:
# az iot hub device-identity show-connection-string --hub-name {YourIoTHubName} --device-id MyNodeDevice --output table
CONNECTION_STRING = "HostName=smartPillow.azure-devices.net;DeviceId=raspberryDi;SharedAccessKey=beaC6GNja8zSEFSRGYI3VlhKZK9zmzWxoTjO61Ixf4Q="


# Define the JSON message to send to IoT Hub.
PRESSURE1 = 20.0
PRESSURE2 = 60
NOISE = 40
#MSG_TXT = '{date}, {time}, Pressure Sensor 1: {pressure1}, Pressure Sensor 2: {pressure2}, Noise Sensor: {noise}'

##option 2 : 

MSG_TXT = '{{ "time": {time}, "type": {dataType}, "value": {value} }}'


def init_connection():
    # Create an IoT Hub client
    try:
        global client 
        client = IoTHubDeviceClient.create_from_connection_string(CONNECTION_STRING)
        print("Connection to Azure IoT Hub successful")
    except:
        print("Error connecting to Azure IoT Hub")

def iothub_send_msg(eventType, eventTime, dataType, data):
    msgFormat = MSG_TXT.format(eventType=eventType, time=eventTime, dataType=dataType, value=data)
    message = Message(msgFormat)
  
    message.custom_properties[eventType] = eventType

    try:
        client.send_message(message)
        #print("Message sent: {}".format(message))
        time.sleep(2)
    except Exception as e: 
        print("Azure message error: ", e)


def iothub_client_telemetry_sample_run():

    try:
        client = iothub_client_init()
        print ( "IoT Hub device sending periodic messages, press Ctrl-C to exit" )
        while True:
            # Build the message with simulated telemetry values.
            pressure1 = PRESSURE1 + (random.random() * 15)
            pressure2 = PRESSURE2 + (random.random() * 20)
            noise = NOISE   + (random.random() * 50)
            msg_txt_formatted = MSG_TXT.format(temperature=pressure1, pressure2=pressure2)
            message = Message(msg_txt_formatted)

            # Add a custom application property to the message.
            # An IoT hub can filter on these properties without access to the message body.
            if noise > 30:
              message.custom_properties["noiseAlert"] = "true"
            else:
              message.custom_properties["noiseAlert"] = "false"

            # Send the message.
            print( "Sending message: {}".format(message) )
            client.send_message(message)
            print ( "Message successfully sent" )
            time.sleep(3)

    except KeyboardInterrupt:
        print ( "IoTHubClient sample stopped" )

if __name__ == '__main__':
    print ( "IoT Hub Samrt Pillow " )
    print ( "Press Ctrl-C to exit" )
    #iothub_client_telemetry_sample_run()