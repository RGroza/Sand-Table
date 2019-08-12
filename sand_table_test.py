import RPi.GPIO as GPIO
from DRV8825 import DRV8825
import threading

Motor1 = DRV8825(dir_pin=13, step_pin=19, enable_pin=12, mode_pins=(16, 17, 20))
Motor2 = DRV8825(dir_pin=24, step_pin=18, enable_pin=4, mode_pins=(21, 22, 27))

def run_mRot(nextPos):
    steps = nextPos[0]
    Motor1.SetMicroStep('software','halfstep')
    if (steps > 0):
        Motor1.TurnStep(Dir='forward', steps=steps, stepdelay = 0.005)
    else:
        Motor1.TurnStep(Dir='backward', steps=abs(steps), stepdelay = 0.005)
    Motor1.Stop()

def run_mLin(nextPos):
    steps = nextPos[1]
    Motor2.SetMicroStep('software','halfstep')
    if (steps > 0):
        Motor2.TurnStep(Dir='forward', steps=steps, stepdelay = 0.005)
    else:
        Motor2.TurnStep(Dir='backward', steps=abs(steps), stepdelay = 0.005)
    Motor2.Stop()

try:
    while True:
        inputStr = input("Input: ")
        
        mRot_steps = int(inputStr[:inputStr.find(" ")])
        mLin_steps = int(inputStr[inputStr.find(" "):])
        
        mRot = threading.Thread(target=runM1, args=((mRot_steps, mLin_steps),))
        mLin = threading.Thread(target=runM2, args=((mRot_steps, mLin_steps),))
        
        print("...")
        mRot.start()
        mLin.start()
        
        mRot.join()
        mLin.join()
        
        print("--------------------\n")
    
except KeyboardInterrupt:
    print("\nMotors stopped")
    Motor1.Stop()
    Motor2.Stop()
    GPIO.cleanup()
    print("Exiting...")
    exit()