import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setup(5, GPIO.IN)
GPIO.setup(6, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

while True:
    print(str(GPIO.input(5)) + "-" + str(GPIO.input(6)))
