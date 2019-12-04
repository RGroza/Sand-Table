import RPi.GPIO as GPIO
import time

hall_pin = 29
delay = 300
detect_count = 0

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)

GPIO.setup(hall_pin, GPIO.IN)

start_time = time.time_ns()/1000000
while True:
    if GPIO.input(hall_pin) and (time.time_ns()/1000000 - start_time) > delay:
        detect_count += 1
        print(detect_count)
