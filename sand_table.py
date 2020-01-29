import RPi.GPIO as GPIO
from DRV8825 import DRV8825
import threading
import math
from time import sleep
import keyboard

from rpi_ws281x import PixelStrip, Color
import led_strip # from led_strip.py


stop_threads = False # Flag for stopping all threads

# Motor driver object init
M_Rot = DRV8825(dir_pin=13, step_pin=19, enable_pin=12, mode_pins=(16, 17, 20), False)
M_Lin = DRV8825(dir_pin=24, step_pin=18, enable_pin=4, mode_pins=(21, 22, 27), False)

# Create NeoPixel object with appropriate configuration.
strip = led_strip.strip_init()

# Setup for limit switches
outer_switch = 5
inner_switch = 6

GPIO.setmode(GPIO.BCM)
GPIO.setup(outer_switch, GPIO.IN)
GPIO.setup(inner_switch, GPIO.IN)

# Run through the LED strip routine
def run_LedStrip(stop_event):
    print("LED stop_threads: " + str(stop_threads))
    strip.begin()

    while isStillMoving:
        print('Color wipe animations.')
        led_strip.colorWipe(strip, led_strip.Color(255, 0, 0))  # Red wipe
        led_strip.colorWipe(strip, led_strip.Color(0, 255, 0))  # Blue wipe
        led_strip.colorWipe(strip, led_strip.Color(0, 0, 255))  # Green wipe
        print('Theater chase animations.')
        led_strip.theaterChase(strip, led_strip.Color(127, 127, 127))  # White theater chase
        led_strip.theaterChase(strip, led_strip.Color(127, 0, 0))  # Red theater chase
        led_strip.theaterChase(strip, led_strip.Color(0, 0, 127))  # Blue theater chase
        print('Rainbow animations.')
        led_strip.rainbow(strip)
        led_strip.rainbowCycle(strip)
        led_strip.theaterChaseRainbow(strip)
    print("LED stop_threads: " + str(stop_threads))


# Functions defined for each motor thread
def run_MRotate():
    print("ROT stop_threads: " + str(stop_threads))
    M_Rot.SetMicroStep('software','1/4step')
    rot_delay = 0.0015
    rot_steps = 3200 # One full revolution
    while not stop_threads:
        M_Rot.TurnStep_ROT(Dir='forward', steps=rot_steps, stepdelay=rot_delay)
    M_Rot.Stop()
    print("ROT stop_threads: " + str(stop_threads))


def run_MLinear(num_steps, delay):
    M_Lin.SetMicroStep('software','1/4step')
    if num_steps > 0:
        M_Lin.TurnStep(stop_event, Dir='forward', steps=num_steps, stepdelay=delay)
    else:
        M_Lin.TurnStep(stop_event, Dir='backward', steps=abs(num_steps), stepdelay=delay)


# Calibrates the linear slide arm before starting the main program routine
def calibrate_slide():
    delay = 1 / 1000
    center_to_min = 20
    outer_to_max = 20

    calibrated = False

    while not calibrated:
        minPos = M_Lin.Turn_until_switch(Dir='backward', limit_switch=inner_switch, stepdelay=delay)
        maxPos = M_Lin.Turn_until_switch(Dir='forward', limit_switch=outer_switch, stepdelay=delay) + minPos

        positions = (minPos, maxPos)
        print(positions)
        totalDist = maxPos - minPos - center_to_min - outer_to_max
        print ("Travel dist: " + str(totalDist))

        sleep(.5)

        test_inner = M_Lin.Turn_check_cali(Dir='backward', steps=totalDist + outer_to_max, limit_switch=inner_switch, stepdelay=delay)
        minPos = 0
        sleep(.5)
        test_outer = M_Lin.Turn_check_cali(Dir='forward', steps=totalDist, limit_switch=outer_switch, stepdelay=delay)
        maxPos = totalDist
        test_inner = M_Lin.Turn_check_cali(Dir='backward', steps=totalDist, limit_switch=inner_switch, stepdelay=delay)

        if test_inner and test_outer:
            calibrated = True
        else:
            print("Calibration Failed! Trying again...")
    print("Calibration Passed!")

    return totalDist


# Stops the motors and LED strip, and joins the threads
def stop_program():
    stop_threads = True

    led_strip.colorWipe(strip, Color(0, 0, 0), 10)
    MRot.join()
    LStrip.join()
    End_stops.join()

    M_Rot.Stop()
    M_Lin.Stop()
    print("\nMotors stopped")
    GPIO.cleanup()
    print("Exiting...")
    exit()

def stop_all_threads():
    stop_threads = True
    MRot.stop_thread()

# Create a function and return the linear postion for the arm (r coordinate val)
def draw_function(maxDisp, currentTheta, rev_steps):
    # Function that can be modified to create different patterns
    pos = round(maxDisp * abs(math.cos(math.radians(360 * currentTheta / rev_steps))))
    return pos

def check_collision():
        if GPIO.input(inner_switch) == 0 or GPIO.input(outer_switch) == 0:
            M_Rot.Stop()
            M_Lin.Stop()
            stop_all_threads()


# Main function for the program
def main():
    # Sand Table hardware constants
    rev_steps = 3200

    currentTheta = 0 # Theta coordinate val - currently just an incrementer
    theta_steps = 100
    linPos = 0
    lastLinPos = 0
    lin_delay = 0.00125

    try:
        maxDisp = calibrate_slide() - 200

        # Start rotation, split into 3 threads (the main thread will process linear movements for MLin)
        global MRot
        MRot = threading.Thread(target=run_MRotate)
        global LStrip
        LStrip = threading.Thread(target=run_LedStrip)
        global End_stops
        End_stops = threading.Thread(target=check_collision)

        MRot.start()
        print("\nROT Thread Started")
        LStrip.start()
        print("\nLed Strip Thread Started")
        End_stops.start()
        print("\nChecking collision")

        while not stop_threads:
            lastLinPos = linPos
            linPos = draw_function(maxDisp, currentTheta, rev_steps) # Set the LinPos to the calculated position
            currentTheta += theta_steps

            print(str(linPos))

            nextPos = linPos - lastLinPos
            run_MLinear(nextPos, lin_delay)

    except KeyboardInterrupt:
        stop_program()

main()
