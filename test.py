import RPi.GPIO as GPIO
import time
from DRV8825 import DRV8825


try:

    Motor1 = DRV8825(dir_pin=13, step_pin=19, enable_pin=12, mode_pins=(16, 17, 20))
    Motor2 = DRV8825(dir_pin=24, step_pin=18, enable_pin=4, mode_pins=(21, 22, 27))

    """
    # 1.8 degree: nema23, nema14
    # software Control :
    # 'fullstep': A cycle = 200 steps
    # 'halfstep': A cycle = 200 * 2 steps
    # '1/4step': A cycle = 200 * 4 steps
    # '1/8step': A cycle = 200 * 8 steps
    # '1/16step': A cycle = 200 * 16 steps
    # '1/32step': A cycle = 200 * 32 steps
    """
    Motor2.SetMicroStep('software','fullstep')
    Motor2.TurnStep_test(Dir='forward', steps=500, stepdelay = 1/500)
    time.sleep(0.5)
    Motor2.SetMicroStep('software','1/4step')
    Motor2.TurnStep_test(Dir='backward', steps=500, stepdelay = 1/500)
    Motor2.Stop()

    """
    # 28BJY-48:
    # hardware Control :
    # 'fullstep': A cycle = 2048 steps
    # 'halfstep': A cycle = 2048 * 2 steps
    # '1/4step': A cycle = 2048 * 4 steps
    # '1/8step': A cycle = 2048 * 8 steps
    # '1/16step': A cycle = 2048 * 16 steps
    # '1/32step': A cycle = 2048 * 32 steps
    """
    Motor2.SetMicroStep('software','fullstep')
    Motor2.TurnStep_test(Dir='forward', steps=500, stepdelay = 1/250)
    time.sleep(0.5)
    Motor2.SetMicroStep('software','1/4step')
    Motor2.TurnStep_test(Dir='backward', steps=500, stepdelay = 1/250)
    Motor2.Stop()

except KeyboardInterrupt:
    print("\nMotor stop")
    Motor1.Stop()
    Motor2.Stop()
    GPIO.cleanup()
    exit()
