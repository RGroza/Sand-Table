import RPi.GPIO as GPIO
from DRV8825 import DRV8825
import threading
from time import sleep
import keyboard

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

coors = [0, 500, 1000]

for c in range(len(coors)):
    if c == 0:
        nextPos = coors[c]
    else:
        nextPos = coors[c]-coors[c-1]
    run_MLin(nextPos, 1/500)