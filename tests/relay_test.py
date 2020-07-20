import RPi.GPIO as GPIO
from time import sleep

GPIO.setmode(GPIO.BOARD)
GPIO.setup(16, GPIO.OUT)
GPIO.setup(22, GPIO.OUT)

GPIO.output(16, GPIO.LOW)
print("Motors ON")
sleep(2)
GPIO.output(16, GPIO.HIGH)
print("Motors OFF")

sleep(1)

GPIO.output(22, GPIO.LOW)
print("LEDs ON")
sleep(2)
GPIO.output(22, GPIO.HIGH)
print("LEDs OFF")

GPIO.cleanup()