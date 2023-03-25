import time
import pigpio
import paho.mqtt.client as mqtt
import RPi.GPIO as GPIO
import asyncio
# Constants
PWM = 18 # Use hardware PWM on BCM 18
DELAY = 0.5
FOOD_INTERVAL = 5
global FOOD
FOOD = 0

TOPIC = 'cat/food'
PORT = 1883
QOS = 0
KEEPALIVE = 60
MESSAGE = 'FOOD RUNNING LOW'

# Set hostname for MQTT broker
BROKER = 'iot.cs.calvin.edu'

# Indicates whether broker requires authentication.
# Set to True for authenticaion, set to False for anonymous brokers
BROKER_AUTHENTICATION = True

# Note: these constants must be set if broker requires authentication
USERNAME = 'cs326'   # broker authentication username (if required)
PASSWORD = 'piot'   # broker authentication password (if required)

lastDispensedTime = time.time()
timeInterval = 5 #seconds


pi = pigpio.pi() # connect to the pigpio service
if not pi.connected:
 exit(0)  
pi.set_PWM_frequency(PWM,50); # Set PWM frequency to 50Hz

def isIntervalComplete():
    if time.time() - lastDispensedTime >= timeInterval:
        return True
    return False

def setFoodStatus(status):
    global FOOD
    FOOD = status

def getFoodStatus():
    return FOOD

def dispense():

    try:
        print(f"FOOD status: {FOOD}")

        print('setting angle = -90 degrees')
        pi.set_servo_pulsewidth(PWM, 1000)
        time.sleep(DELAY)
        print('setting angle = 90 degrees')
        pi.set_servo_pulsewidth(PWM, 2000)
        time.sleep(FOOD_INTERVAL)
        lastDispensedTime = time.time()

    except KeyboardInterrupt:
        pi.set_servo_pulsewidth(PWM, 0) # turn pulses off
        pi.stop()
        
# Callback when a connection has been established with the MQTT broker
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print(f'Connected to {BROKER} successful.')
    else:
        print(f'Connection to {BROKER} failed. Return code={rc}')

# Callback when client receives a message from the broker
def on_message(client, data, msg):
    if (msg.topic ==  TOPIC):
        print(f'Received msg: Food status = {msg.payload}')
        if int(msg.payload) == 1:
            print("THERE IS FOOD")
            print(int(msg.payload))
            setFoodStatus(1)
            print(f"FOOD status 2: {getFoodStatus()}")
        else:
            print("NO FOOD")
            setFoodStatus(0)
            print(f"FOOD status 2: {getFoodStatus()}")
    
# Setup MQTT client and callbacks 
client = mqtt.Client()
if BROKER_AUTHENTICATION:
    client.username_pw_set(USERNAME, password=PASSWORD)
client.on_connect = on_connect
client.on_message = on_message

# Connect to MQTT broker and subscribe to the button topic
try:
    client.connect(BROKER, PORT, KEEPALIVE)
    client.loop_start()
except:
    print("couldn't connect")
client.subscribe(TOPIC, qos=QOS)



# try:
#     client.loop_forever()
# except KeyboardInterrupt:
#     client.disconnect()
#     GPIO.cleanup()
#     print('Done')

while True:
    if FOOD == 0 and isIntervalComplete():
            dispense()



# def main():
#     # dispense()

# main()
client.disconnect()