import RPi.GPIO as GPIO
from DRV8825 import DRV8825
import threading
import math
from time import sleep

from rpi_ws281x import PixelStrip, Color
import led_strip # from led_strip.py

from utils.process_files import process_files

stop_motor_threads = False # Flag for stopping motors at collision
stop_all_threads = False # Flag for stopping all threads
MRot_done = False
MLin_done = False

# Motor driver object init
M_Rot = DRV8825(dir_pin=13, step_pin=19, enable_pin=12, mode_pins=(16, 17, 20), stop_event=False)
M_Lin = DRV8825(dir_pin=24, step_pin=18, enable_pin=4, mode_pins=(21, 22, 27), stop_event=False)

# Create NeoPixel object with appropriate configuration.
strip = led_strip.strip_init()

# Setup for limit switches
outer_switch = 5
inner_switch = 6

GPIO.setmode(GPIO.BCM)
GPIO.setup(outer_switch, GPIO.IN)
GPIO.setup(inner_switch, GPIO.IN)


# Run through the LED strip routine
def run_LedStrip():
    print("LED state: {}".format(not stop_all_threads))
    strip.begin()

    while not stop_all_threads:
        print('LED Color wipe')
        led_strip.colorWipe(strip, led_strip.Color(255, 0, 0))  # Red wipe
        led_strip.colorWipe(strip, led_strip.Color(0, 255, 0))  # Blue wipe
        led_strip.colorWipe(strip, led_strip.Color(0, 0, 255))  # Green wipe
        print('LED Theater chase')
        led_strip.theaterChase(strip, led_strip.Color(127, 127, 127))  # White theater chase
        led_strip.theaterChase(strip, led_strip.Color(127, 0, 0))  # Red theater chase
        led_strip.theaterChase(strip, led_strip.Color(0, 0, 127))  # Blue theater chase
        print('LED Rainbow animations')
        led_strip.rainbow(strip)
        led_strip.rainbowCycle(strip)
        led_strip.theaterChaseRainbow(strip)

    print("LED state: {}".format(not stop_all_threads))


# Functions defined for each motor thread
def run_MRot(steps, delay):
    print("M_Rot state: {}".format(not stop_motors))
    M_Rot.set_microstep('software','1/4step')

    if (steps > 0):
        M_Rot.turn_steps(Dir='forward', steps=steps, stepdelay=delay)
    else:
        M_Rot.turn_steps(Dir='backward', steps=steps, stepdelay=delay)
    M_Rot.stop()

    MRot_done = True

    print("M_Rot done!")
    print("M_Rot state: {}".format(not stop_motors))


def run_MLin(steps, delay):
    print("M_Lin state: {}".format(not stop_motors))
    M_Rot.set_microstep('software','1/4step')

    if (steps > 0):
        M_Lin.turn_steps(Dir='forward', steps=steps, stepdelay=delay)
    else:
        M_Lin.turn_steps(Dir='backward', steps=steps, stepdelay=delay)

    M_Lin.stop()

    MLin_done = True

    print("M_Lin done!")
    print("M_Lin state: {}".format(not stop_motors))


# Calibrates the linear slide arm before starting the main program routine
def calibrate_slide():
    delay = 0.001
    center_to_min = 20
    outer_to_max = 20

    calibrated = False

    while not calibrated:
        minPos = M_Lin.turn_until_switch(Dir='backward', limit_switch=inner_switch, stepdelay=delay)
        maxPos = M_Lin.turn_until_switch(Dir='forward', limit_switch=outer_switch, stepdelay=delay) + minPos

        print((minPos, maxPos))
        totalDist = maxPos - minPos - center_to_min - outer_to_max
        print ("Travel distance: " + str(totalDist))

        sleep(.5)
        test_inner = M_Lin.turn_check_cali(Dir='backward', steps=totalDist + outer_to_max, limit_switch=inner_switch, stepdelay=delay)
        sleep(.5)
        test_outer = M_Lin.turn_check_cali(Dir='forward', steps=totalDist, limit_switch=outer_switch, stepdelay=delay)

        if test_inner and test_outer:
            calibrated = True
            print("Calibration Passed!")
            sleep(.5)
            M_Lin.turn_steps(Dir='backward', steps=totalDist, stepdelay=delay)
        else:
            print("Calibration Failed! Trying again...")

    return totalDist


# Stops the motors and LED strip, and joins the threads
def stop_program():
    stop_all_threads = True

    led_strip.colorWipe(strip, Color(0, 0, 0), 10)
    MRot.join()
    MLin.join()
    LStrip.join()

    M_Rot.stop()
    M_Lin.stop()
    print("\nMotors stopped")
    GPIO.cleanup()
    print("Exiting...")
    exit()


def stop_motors():
    MRot_done = True
    MLin_done = True


def check_collision():
        if GPIO.input(inner_switch) == 0 or GPIO.input(outer_switch) == 0:
            stop_motors()
            M_Rot.stop()
            M_Lin.stop()


# Create seperate threads
MRot = threading.Thread(target=run_MRot)
MLin = threading.Thread(target=run_MLin)
LStrip = threading.Thread(target=run_LedStrip)


def main():
    tracks = process_files()

    try:
        maxDisp = calibrate_slide() - 200

        # LStrip.start()

        for track in tracks:
            for step in track:
                print(step)

                MLin_done = False
                MRot_done = False

                MRot = threading.Thread(target=run_MRot, args=(step[0], step[2],))
                MLin = threading.Thread(target=run_MLin, args=(step[1], step[3],))

                print("...")
                MRot.start()
                MLin.start()

                while MRot_done or MLin_done:
                    check_collision()

                MRot.join()
                MLin.join()

    except KeyboardInterrupt:
        stop_program()


main()