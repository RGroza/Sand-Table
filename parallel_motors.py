import RPi.GPIO as GPIO
from utils.DRV8825 import DRV8825
import threading
from time import sleep


M_Rot = DRV8825(dir_pin=13, step_pin=19, enable_pin=12, mode_pins=(16, 17, 20))
M_Lin = DRV8825(dir_pin=24, step_pin=18, enable_pin=4, mode_pins=(21, 22, 27))

class MotorThreads:

    def __init__(self):
        self.running = True

    def run_MRot(self, delay, step_size):
        M_Rot.set_microstep('software', step_size)

        while self.running:
            M_Rot.turn_steps(Dir='forward', steps=1, stepdelay=delay)

        M_Rot.stop()

    def run_MLin(self, delay, step_size):
        M_Lin.set_microstep('software', step_size)

        M_Lin.turn_steps(Dir='forward', steps=1800, stepdelay=delay)
        sleep(1)
        M_Lin.turn_steps(Dir='backward', steps=1800, stepdelay=delay)

        M_Lin.stop()
        self.running = False

delays = [0.01, 0.004, 0.003, 0.002, 0.001, 0.0005]
step_sizes = ['fullstep', '1/4step', '1/32step']

try:
    motors = MotorThreads()
    for d in delays:
        print("Delays: {}".format(d))

        MRot = threading.Thread(target=motors.run_MRot, args=(d, 'fullstep',))
        MLin = threading.Thread(target=motors.run_MLin, args=(d, 'fullstep',))

        print("...")
        MRot.start()
        MLin.start()

        MRot.join()
        MLin.join()

        sleep(3)
        motors.running = True
except KeyboardInterrupt:
    print("\nMotors stopped")
    M_Rot.stop()
    M_Lin.stop()
    GPIO.cleanup()
    print("Exiting...")
    exit()
