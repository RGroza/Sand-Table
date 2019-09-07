import RPi.GPIO as GPIO
from DRV8825 import DRV8825
import threading
from time import sleep
import keyboard

from os import listdir
from os.path import isfile, join

M_Rot = DRV8825(dir_pin=13, step_pin=19, enable_pin=12, mode_pins=(16, 17, 20))
M_Lin = DRV8825(dir_pin=24, step_pin=18, enable_pin=4, mode_pins=(21, 22, 27))

def run_MRot(num_steps, delay, stop_event):
    M_Rot.SetMicroStep('software','fullstep')
    if num_steps > 0:
        M_Rot.TurnStep(stop_event, Dir='forward', steps=num_steps, stepdelay = delay)
    else:
        M_Rot.TurnStep(stop_event, Dir='backward', steps=abs(num_steps), stepdelay = delay)
    M_Rot.Stop()

def run_MLin(num_steps, delay, stop_event):
    M_Lin.SetMicroStep('software','fullstep')
    if num_steps > 0:
        M_Lin.TurnStep(stop_event, Dir='forward', steps=num_steps, stepdelay = delay)
    else:
        M_Lin.TurnStep(stop_event, Dir='backward', steps=abs(num_steps), stepdelay = delay)
    M_Lin.Stop()

def get_files(mypath):
    onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]
    print("Files found: " + str(onlyfiles).replace('[', '').replace(']', ''))

    return onlyfiles

def get_coordinates(filename, mypath):
    with open(mypath + filename, "r") as f:
        content = f.readlines()

    lines = [line.rstrip('\n') for line in content]

    coor = []
    for c in lines:
        coor.append((int(c[:c.find(" ")]), int(c[c.find(" ")+1:])))

    return coor

def calibrate_slide():
    outer_switch = 5
    inner_switch = 6

    GPIO.setmode(GPIO.BCM)
    GPIO.setup(outer_switch, GPIO.IN)
    GPIO.setup(inner_switch, GPIO.IN)

    delay = 1 / 1000
    pos = 0
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

        test_inner = M_Lin.TurnStep_test(Dir='backward', steps=totalDist + outer_to_max, limit_switch=inner_switch, stepdelay=delay)
        minPos = 0
        sleep(2)
        test_outer = M_Lin.TurnStep_test(Dir='forward', steps=totalDist, limit_switch=outer_switch, stepdelay=delay)
        maxPos = totalDist
        if test_inner and test_outer:
            calibrated = True
        else:
            print("Calibration Failed! Trying again...")
    print("Calibration Passed!")
    return totalDist

def stop_program(threading_event):
    threading_event.set()
    MRot.join()
    MLin.join()
    print("\nMotors stopped")
    M_Rot.Stop()
    M_Lin.Stop()
    GPIO.cleanup()
    print("Exiting...")
    exit()

mypath = "files/"

default_speed = 1000
max_speed = 2000

try:
    #maxDisp = calibrate_slide()
    threading_event = threading.Event()
    files = get_files(mypath)
    for f in files:
        coor = get_coordinates(f, mypath)
        print("Running file: " + f)
        n = 0
        for c in range(len(coor)):
            print(str(coor[c]))

            if c == 0:
                nextPos = (coor[c][0], coor[c][1])
            else:
                nextPos = (coor[c][0]-coor[c-1][0], coor[c][1]-coor[c-1][1])

            elapsed_time = abs(nextPos[0]) / default_speed
            if elapsed_time > 0 and abs(nextPos[1]) / elapsed_time <= max_speed:
                Rot_delay = 1 / default_speed
                Lin_delay = elapsed_time / abs(nextPos[1]) if nextPos[1] != 0 else Lin_delay = 0
            else:
                max_time = abs(nextPos[1]) / max_speed
                Rot_delay = max_time / abs(nextPos[0]) if nextPos[0] != 0 else Rot_delay = 0
                Lin_delay = 1 / max_speed

            print("MRot speed: " + str(1/Rot_delay))
            print("MLin speed: " + str(1/Lin_delay))

            MRot = threading.Thread(target=run_MRot, args=(nextPos[0], Rot_delay, threading_event,))
            MLin = threading.Thread(target=run_MLin, args=(nextPos[1], Lin_delay, threading_event,))

            print("...")
            MRot.start()
            MLin.start()

            MRot.join()
            MLin.join()

            print("--------------------\n")
            #sleep(0.5)

        #sleep(2)

except KeyboardInterrupt:
    stop_program(threading_event)
