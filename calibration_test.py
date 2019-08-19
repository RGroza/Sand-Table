import RPi.GPIO as GPIO
from DRV8825 import DRV8825
from time import sleep

# M_Rot = DRV8825(dir_pin=13, step_pin=19, enable_pin=12, mode_pins=(16, 17, 20))
M_Lin = DRV8825(dir_pin=24, step_pin=18, enable_pin=4, mode_pins=(21, 22, 27))

GPIO.setmode(GPIO.BCM)
GPIO.setup(5, GPIO.IN)
GPIO.setup(6, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

delay = 0.001
pos = 0
center_to_min = 80
outer_to_max = 50

minPos = M_Lin.Turn(Dir='forward', limit_switch=5, stepdelay=delay)

maxPos = M_Lin.Turn(Dir='forward', limit_switch=6, stepdelay=delay)

positions = (minPos, maxPos)
print(positions)
totalDist = maxPos - minPos - center_to_min - outer_to_max
print ("Travel Distance: " + str(totalDist))

sleep(2)

test_inner = M_Lin.TurnStep_test(Dir='backward', steps=totalDist + outer_to_max, stepdelay=delay)
minPos = 0
sleep(2)
test_outer = M_Lin.TurnStep_test(Dir='forward', steps=totalDist, stepdelay=delay)
maxPos = totalDist
