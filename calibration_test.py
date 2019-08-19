import RPi.GPIO as GPIO
from DRV8825 import DRV8825
from time import sleep

# M_Rot = DRV8825(dir_pin=13, step_pin=19, enable_pin=12, mode_pins=(16, 17, 20))
M_Lin = DRV8825(dir_pin=24, step_pin=18, enable_pin=4, mode_pins=(21, 22, 27))

outer_switch = 5
inner_switch = 6

GPIO.setmode(GPIO.BCM)
GPIO.setup(outer_switch, GPIO.IN)
GPIO.setup(inner_switch, GPIO.IN)

delay = 0.001
pos = 0
center_to_min = 80
outer_to_max = 50

minPos = M_Lin.Turn(Dir='backward', limit_switch=inner_switch, stepdelay=delay)

maxPos = M_Lin.Turn(Dir='forward', limit_switch=outer_switch, stepdelay=delay)

positions = (minPos, maxPos)
print(positions)
totalDist = maxPos - minPos - center_to_min - outer_to_max
print ("Travel Distance: " + str(totalDist))

sleep(2)

test_inner = M_Lin.TurnStep_test(Dir='backward', steps=totalDist + outer_to_max, limit_switch=inner_switch, stepdelay=delay)
minPos = 0
sleep(2)
test_outer = M_Lin.TurnStep_test(Dir='forward', steps=totalDist, limit_switch=outer_switch, stepdelay=delay)
maxPos = totalDist
