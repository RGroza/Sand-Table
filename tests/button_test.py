import RPi.GPIO as GPIO
from time import sleep

GPIO.setmode(GPIO.BCM)
GPIO.setup(26, GPIO.IN)

while True:
    print(GPIO.input(26))