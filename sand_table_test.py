import RPi.GPIO as GPIO
from DRV8825 import DRV8825
import threading
from time import sleep

from os import listdir
from os.path import isfile, join

Motor1 = DRV8825(dir_pin=13, step_pin=19, enable_pin=12, mode_pins=(16, 17, 20))
Motor2 = DRV8825(dir_pin=24, step_pin=18, enable_pin=4, mode_pins=(21, 22, 27))

def run_MRot(num_steps, delay):
    Motor1.SetMicroStep('software','halfstep')
    if num_steps > 0:
        Motor1.TurnStep(Dir='forward', steps=num_steps, stepdelay = 0.005)
    else:
        Motor1.TurnStep(Dir='backward', steps=abs(num_steps), stepdelay = 0.005)
    Motor1.Stop()

def run_MLin(num_steps, delay):
    Motor2.SetMicroStep('software','halfstep')
    if num_steps > 0:
        Motor2.TurnStep(Dir='forward', steps=num_steps, stepdelay = 0.005)
    else:
        Motor2.TurnStep(Dir='backward', steps=abs(num_steps), stepdelay = 0.005)
    Motor2.Stop()

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

mypath = "files/"

default_speed = 200
max_speed = 500

try:
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
            if abs(nextPos[1]) / elapsed_time <= max_speed:
                Rot_delay = 1 / default_speed
                Lin_delay = elapsed_time / abs(nextPos[1])
            else:
                max_time = abs(nextPos[1]) / max_speed
                Rot_delay = max_time / abs(nextPos[0])
                Lin_delay = 1 / max_speed

            MRot = threading.Thread(target=run_MRot, args=(nextPos[0], Rot_delay,))
            MLin = threading.Thread(target=run_MLin, args=(nextPos[1], Lin_delay,))

            print("...")
            MRot.start()
            MLin.start()

            MRot.join()
            MLin.join()

            print("--------------------\n")
            sleep(0.5)

        sleep(2)

except KeyboardInterrupt:
    print("\nMotors stopped")
    Motor1.Stop()
    Motor2.Stop()
    GPIO.cleanup()
    print("Exiting...")
    exit()