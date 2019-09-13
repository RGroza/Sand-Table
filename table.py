import RPi.GPIO as GPIO
from DRV8825 import DRV8825
import threading
import math
from time import sleep
import keyboard

from os import listdir
from os.path import isfile, join

M_Rot = DRV8825(dir_pin=13, step_pin=19, enable_pin=12, mode_pins=(16, 17, 20))
M_Lin = DRV8825(dir_pin=24, step_pin=18, enable_pin=4, mode_pins=(21, 22, 27))

isStillMoving = False #flag that motors are to be moving

def run_MRotate(stop_event):
    M_Rot.SetMicroStep('software','1/4step')
    rot_delay = 0.0015
    rot_steps = 3200
    while isStillMoving:
        M_Rot.TurnStep_ROT(Dir='forward', steps=rot_steps, stepdelay = rot_delay)
    M_Rot.Stop()

def run_MLinear(num_steps, delay, stop_event):
    M_Lin.SetMicroStep('software','1/4step')
    if num_steps > 0:
        M_Lin.TurnStep(stop_event, Dir='forward', steps=num_steps, stepdelay = delay)
    else:
        M_Lin.TurnStep(stop_event, Dir='backward', steps=abs(num_steps), stepdelay = delay)

def run_MLin(num_steps, delay, stop_event):
    M_Lin.SetMicroStep('software','1/4step')
    if num_steps > 0:
        M_Lin.TurnStep(stop_event, Dir='forward', steps=num_steps, stepdelay = delay)
    else:
        M_Lin.TurnStep(stop_event, Dir='backward', steps=abs(num_steps), stepdelay = delay)
    M_Lin.Stop()

def calibrate_slide():
    outer_switch = 5
    inner_switch = 6

    GPIO.setmode(GPIO.BCM)
    GPIO.setup(outer_switch, GPIO.IN)
    GPIO.setup(inner_switch, GPIO.IN)

    delay = 1 / 1000
    center_to_min = 20
    outer_to_max = 20

    calibrated = False

    while not calibrated:
        minPos = M_Lin.Turn(Dir='backward', limit_switch=inner_switch, stepdelay=delay)
        maxPos = M_Lin.Turn(Dir='forward', limit_switch=outer_switch, stepdelay=delay) + minPos

        positions = (minPos, maxPos)
        print(positions)
        totalDist = maxPos - minPos - center_to_min - outer_to_max
        print ("Travel Distance: " + str(totalDist))

        sleep(2)

        test_inner = M_Lin.TurnStep_cali(Dir='backward', steps=totalDist + outer_to_max, limit_switch=inner_switch, stepdelay=delay)
        minPos = 0
        sleep(2)
        test_outer = M_Lin.TurnStep_cali(Dir='forward', steps=totalDist, limit_switch=outer_switch, stepdelay=delay)
        maxPos = totalDist
        test_inner = M_Lin.TurnStep_cali(Dir='backward', steps=totalDist, limit_switch=inner_switch, stepdelay=delay)

        if test_inner and test_outer:
            calibrated = True
        else:
            print("Calibration Failed! Trying again...")
    print("Calibration Passed!")

    return totalDist

def stop_program(threading_event):
    threading_event.set()
    isStillMoving = False
    MRot.join()
    #MLin.join()
    print("\nMotors stopped")
    M_Rot.Stop()
    #M_Lin.Stop()
    GPIO.cleanup()
    print("Exiting...")
    exit()

default_speed = 750
max_speed = 1000
rev_steps = 3200
currentTheta = 0 # theta coordinate val - currently just incrementer
theta_steps = 100
LinPos = 0
LastLinPos = 0
Lin_delay = 0.00125

try:
    maxDisp = calibrate_slide() - 50
    threading_event = threading.Event()
    isStillMoving = True

    # start Rotation
    MRot = threading.Thread(target=run_MRotate, args=(threading_event,))
    MRot.start()
    print("\nROT Thread Started")
    while isStillMoving:
        LastLinPos = LinPos
        LinPos = round(maxDisp * abs(math.cos(math.radians(360 * currentTheta / rev_steps)))) # r coordinate val
        currentTheta += theta_steps

        print(str(LinPos))

        nextPos = LinPos - LastLinPos
        run_MLinear (nextPos, Lin_delay, threading_event,)

except KeyboardInterrupt:
    stop_program(threading_event)
