#! /usr/bin/python2
import os
import paho.mqtt.client as mqtt
import time
import sys

import RPi.GPIO as GPIO
#import * from ledpi
from hx711 import HX711
# Constants
TOPIC = 'cat/food'
PORT = 8883
QOS = 0
KEEPALIVE = 60
MESSAGE_EMPTY = '0'
MESSAGE_FULL = '1'
CERTS='/etc/ssl/certs/ca-certificates.crt'

# Set hostname for MQTT broker
BROKER = 'iot.cs.calvin.edu'

# Indicates whether broker requires authentication.
# Set to True for authenticaion, set to False for anonymous brokers
BROKER_AUTHENTICATION = True

# Note: these constants must be set if broker requires authentication
USERNAME = 'cs326'   # broker authentication username (if required)
PASSWORD = 'piot'   # broker authentication password (if required)

# Callback when a connection has been established with the MQTT broker
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print(f'Connected to {BROKER} successful.')
    else:
        print(f'Connection to {BROKER} failed. Return code={rc}')

# Callback function when weight is low
def weight_callback(val):
    global client

    if (val < 0.01):
        (result, num) = client.publish(TOPIC, MESSAGE_EMPTY, qos=QOS)
        if result == 0:
            print(f'MQTT message published -> topic:{TOPIC}, message:{MESSAGE_EMPTY}')
        else:
            print(f'PUBLISH returned error: {result}')
    else:
        (result, num) = client.publish(TOPIC, MESSAGE_FULL, qos=QOS)
        if result == 0:
            print(f'MQTT message published -> topic:{TOPIC}, message:{MESSAGE_FULL}')
        else:
            print(f'PUBLISH returned error: {result}')
    #client.disconnect()

def measure_weight():
    # EMULATE_HX711=False

    # referenceUnit = 1

    # if not EMULATE_HX711:
    #     import RPi.GPIO as GPIO
    #     from hx711 import HX711
    # else:
    #     from emulated_hx711 import HX711



    hx = HX711(5, 6)

    # I've found out that, for some reason, the order of the bytes is not always the same between versions of python, numpy and the hx711 itself.
    # Still need to figure out why does it change.
    # If you're experiencing super random values, change these values to MSB or LSB until to get more stable values.
    # There is some code below to debug and log the order of the bits and the bytes.
    # The first parameter is the order in which the bytes are used to build the "long" value.
    # The second paramter is the order of the bits inside each byte.
    # According to the HX711 Datasheet, the second parameter is MSB so you shouldn't need to modify it.
    hx.set_reading_format("MSB", "MSB")

    # HOW TO CALCULATE THE REFFERENCE UNIT
    # To set the reference unit to 1. Put 1kg on your sensor or anything you have and know exactly how much it weights.
    # In this case, 92 is 1 gram because, with 1 as a reference unit I got numbers near 0 without any weight
    # and I got numbers around 184000 when I added 2kg. So, according to the rule of thirds:
    # If 2000 grams is 184000 then 1000 grams is 184000 / 2000 = 92.
    hx.set_reference_unit(336500)
    #hx.set_reference_unit(referenceUnit)

    hx.reset()

    hx.tare()

    print("Tare done! Add weight now...")

    # to use both channels, you'll need to tare them both
    #hx.tare_A()
    #hx.tare_B()

    while True:
        try:
            # These three lines are usefull to debug wether to use MSB or LSB in the reading formats
            # for the first parameter of "hx.set_reading_format("LSB", "MSB")".
            # Comment the two lines "val = hx.get_weight(5)" and "print val" and uncomment these three lines to see what it prints.
            
            # np_arr8_string = hx.get_np_arr8_string()
            # binary_string = hx.get_binary_string()
            # print binary_string + " " + np_arr8_string
            
            # Prints the weight. Comment if you're debbuging the MSB and LSB issue.
            time.sleep(5) #every 5 seconds, take mesaurement
            val = hx.get_weight(5)
            print(val)

            weight_callback(val)
            print("hello")
            # To get weight from both channels (if you have load cells hooked up 
            # to both channel A and B), do something like this
            #val_A = hx.get_weight_A(5)
            #val_B = hx.get_weight_B(5)
            #print "A: %s  B: %s" % ( val_A, val_B )

            hx.power_down()
            hx.power_up()
            time.sleep(0.1)

        except (KeyboardInterrupt, SystemExit):
            cleanAndExit()

# Setup MQTT client and callbacks
client = mqtt.Client()
if BROKER_AUTHENTICATION:
    client.username_pw_set(USERNAME,password=PASSWORD)
client.tls_set(CERTS)
client.on_connect=on_connect
client.connect(BROKER, PORT, KEEPALIVE)
time.sleep(5)
measure_weight()



def cleanAndExit():
    print("Cleaning...")

    # if not EMULATE_HX711:
    GPIO.cleanup()
        
    print("Bye!")
    sys.exit()
try:
    client.loop_forever()
except KeyboardInterrupt:
    client.disconnect()
    GPIO.cleanup()
    print('Done')