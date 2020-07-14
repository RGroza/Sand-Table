import RPi.GPIO as GPIO
from utils.DRV8825 import DRV8825
import threading
from time import sleep

stop_threads = False

M_Rot = DRV8825(dir_pin=13, step_pin=19, enable_pin=12, mode_pins=(16, 17, 20))
M_Lin = DRV8825(dir_pin=24, step_pin=18, enable_pin=4, mode_pins=(21, 22, 27))

def run_MRot(delay, step_size):
    M_Rot.set_microstep('software', step_size)
    print("Step size: {}".format(step_size))

    while not stop_threads
        M_Rot.turn_steps(Dir='forward', steps=10, stepdelay=delay)

    M_Rot.stop()

def run_MLin(delay, step_size):
    M_Lin.turn_steps(Dir='forward', steps=1928, stepdelay=delay)
    sleep(1)
    M_Lin.turn_steps(Dir='backward', steps=1928, stepdelay=delay)

    M_Lin.stop()
    stop_threads = True

delays = [0.004, 0.003, 0.002, 0.001, 0.0005]
# step_sizes = ['fullstep', 'halfstep', '1/4step', '1/8step', '1/16step', '1/32step']

try:
    for delay in delays:
        print("Delay: {}".format(delay))

        MRot = threading.Thread(target=run_MRot, args=(step[0], step[2],))
        MLin = threading.Thread(target=run_MLin, args=(step[1], step[3],))

        print("...")
        MRot.start()
        MLin.start()

        MRot.join()
        MLin.join()

        sleep(3)
except KeyboardInterrupt:
    print("\nMotors stopped")
    M_Rot.Stop()
    M_Lin.Stop()
    GPIO.cleanup()
    print("Exiting...")
    exit()
