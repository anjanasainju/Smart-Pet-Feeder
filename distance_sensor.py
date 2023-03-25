import RPi.GPIO as GPIO
import time
# import paho.mqtt.client as mqtt
import smtplib

#ultrasonic sensor code:
#https://tutorials-raspberrypi.com/raspberry-pi-ultrasonic-sensor-hc-sr04/

#GPIO Mode (BOARD / BCM)
GPIO.setmode(GPIO.BCM)
 
#set GPIO Pins
GPIO_TRIGGER = 18
GPIO_ECHO = 24
 
#set GPIO direction (IN / OUT)
GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
GPIO.setup(GPIO_ECHO, GPIO.OUT)
GPIO.output(GPIO_ECHO, False)


# creates SMTP session
s = smtplib.SMTP('smtp.office365.com', 587)
 
# start TLS for security
s.starttls()
 
# Authentication
s.login("autopetfeederiot@outlook.com", "comeMiloeat")
 
# message to be sent   
SUBJECT = "Pet Feeder Low on food"   
TEXT = "Your pet feeder is almost empty. Fill it so your pet doesn't starve."
 
message = 'Subject: {}\n\n{}'.format(SUBJECT, TEXT)

CHECK_TIME = 10

def distance():
    # set Trigger to HIGH
    GPIO.output(GPIO_TRIGGER, True)
    GPIO.setup(GPIO_ECHO, GPIO.IN)     
#     GPIO.output(GPIO_ECHO, False)

    # set Trigger after 0.01ms to LOW
    time.sleep(0.00001)
    GPIO.output(GPIO_TRIGGER, False)
 
    StartTime = time.time()
    StopTime = time.time()
 
    # save StartTime
    while GPIO.input(GPIO_ECHO) == 0:
        StartTime = time.time()
 
    # save time of arrival
    while GPIO.input(GPIO_ECHO) == 1:
        StopTime = time.time()
 
    # time difference between start and arrival
    TimeElapsed = StopTime - StartTime
    # multiply with the sonic speed (34300 cm/s)
    # and divide by 2, because there and back
    distance = (TimeElapsed * 34300) / 2
 
    return distance
 

try:
    
    while True:
        time.sleep(CHECK_TIME)
        dist = distance()
        print ("Measured Distance = %.1f cm" % dist)
        if (dist > 30):
            s.sendmail("autopetfeederiot@outlook.com", "anwesha03@hotmail.com", message)
            print("Email has been sent!")
    # Reset by pressing CTRL + C
except KeyboardInterrupt:
    print("Measurement stopped by User")
    GPIO.cleanup()

# terminating the session
s.quit()