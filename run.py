import RPi.GPIO as GPIO
from utils.DRV8825 import DRV8825
import threading
import math
from time import sleep
from random import shuffle

from rpi_ws281x import PixelStrip, Color
from led_strip import *

from utils.process_files import get_files, process_new_files, read_track, get_max_disp
from utils.i2c_lcd_driver import *

MRot_done = False
MLin_done = False

# Motor driver object init
M_Rot = DRV8825(dir_pin=13, step_pin=19, enable_pin=12, mode_pins=(16, 17, 20))
M_Lin = DRV8825(dir_pin=24, step_pin=18, enable_pin=4, mode_pins=(21, 22, 27))

# Setting microstep size to 1/8
M_Rot.set_microstep('software','1/4step')
M_Lin.set_microstep('software','1/4step')

# Create NeoPixel object with appropriate configuration.
strip = strip_init()
strip_thread = LedStripThread()

# Setup for limit switches
outer_switch = 5
inner_switch = 6
motor_relay = 23
led_relay = 25

GPIO.setmode(GPIO.BCM)
GPIO.setup(outer_switch, GPIO.IN)
GPIO.setup(inner_switch, GPIO.IN)
GPIO.setup(motor_relay, GPIO.OUT)
GPIO.setup(led_relay, GPIO.OUT)

# Slide thresholds
center_to_min = 250
outer_to_max = 250
max_disp = 0


# Run through the LED strip routine
def run_LedStrip():
    strip.begin()

    if not strip_thread.running: return
    print('LED Color wipe')
    strip_thread.colorWipe(strip, Color(255, 0, 0))  # Red wipe
    strip_thread.colorWipe(strip, Color(0, 255, 0))  # Blue wipe
    strip_thread.colorWipe(strip, Color(0, 0, 255))  # Green wipe
    print('LED Theater chase')
    if not strip_thread.running: return
    strip_thread.theaterChase(strip, Color(127, 127, 127))  # White theater chase
    strip_thread.theaterChase(strip, Color(127, 0, 0))  # Red theater chase
    strip_thread.theaterChase(strip, Color(0, 0, 127))  # Blue theater chase
    print('LED Rainbow animations')
    if not strip_thread.running: return
    strip_thread.rainbow(strip)
    strip_thread.rainbowCycle(strip)
    strip_thread.theaterChaseRainbow(strip)


# Functions defined for each motor thread
def run_MRot(steps, delay, debug=False):
    if steps != 0 and delay >= 0:
        if steps > 0:
            M_Rot.turn_steps(Dir='forward', steps=abs(steps), stepdelay=delay)
        else:
            M_Rot.turn_steps(Dir='backward', steps=abs(steps), stepdelay=delay)

    M_Rot.stop()
    MRot_done = True

    if debug:
        print("M_Rot done!")


def run_MRot_until(Dir, delay, debug=False):
    if delay >= 0:
        while M_Rot.running:
            M_Rot.turn_steps(Dir=Dir, steps=1, stepdelay=delay)

    M_Rot.stop()
    MRot_done = True

    if debug:
        print("M_Rot done!")


def run_MLin(steps, delay, debug=False):
    if steps != 0 and delay >= 0:
        if steps > 0:
            M_Lin.turn_steps(Dir='forward', steps=abs(steps), stepdelay=delay)
        else:
            M_Lin.turn_steps(Dir='backward', steps=abs(steps), stepdelay=delay)

    M_Lin.stop()
    MLin_done = True

    if debug:
        print("M_Lin done!")


def run_MLin_until(steps, delay, debug=False):
    run_MLin(steps, delay, debug=debug)
    M_Rot.running = True


# Calibrates the linear slide arm before starting the main program routine
def calibrate_slide():

    calibrated = False

    while not calibrated:
        minPos = M_Lin.turn_until_switch(Dir='backward', limit_switch=inner_switch, stepdelay=0.0002)
        maxPos = M_Lin.turn_until_switch(Dir='forward', limit_switch=outer_switch, stepdelay=0.0002) + minPos

        print((minPos, maxPos))
        totalDist = maxPos - minPos - center_to_min - outer_to_max
        print ("Travel distance: " + str(totalDist))

        sleep(.5)
        test_inner = M_Lin.turn_check_cali(Dir='backward', steps=totalDist + outer_to_max, limit_switch=inner_switch, stepdelay=0.0002)
        # sleep(.5)
        # test_outer = M_Lin.turn_check_cali(Dir='forward', steps=totalDist, limit_switch=outer_switch, stepdelay=0.0002)

        if test_inner:
            calibrated = True
            print("Calibration Passed!")
            # sleep(.5)
            # M_Lin.turn_steps(Dir='backward', steps=totalDist, stepdelay=0.0002)
        else:
            print("Calibration Failed! Trying again...")

    return totalDist


def erase_out_to_in():
    M_Lin.turn_until_switch(Dir='forward', limit_switch=outer_switch, stepdelay=0.0002)
    
    MRot = threading.Thread(target=run_MRot_until, args=('forward', 0.0002,))
    MLin = threading.Thread(target=run_MLin_until, args=(max_disp + outer_to_max, 0.1,))

    print("Erasing...")
    MRot.start()
    MLin.start()

    MRot.join()
    MLin.join()


def erase_in_to_out():
    M_Lin.turn_until_switch(Dir='backward', limit_switch=inner_switch, stepdelay=0.0002)
    
    MRot = threading.Thread(target=run_MRot_until, args=('forward', 0.0002,))
    MLin = threading.Thread(target=run_MLin_until, args=(-max_disp - center_to_min, 0.1,))

    print("Erasing...")
    MRot.start()
    MLin.start()

    MRot.join()
    MLin.join()


# Stops the motors and LED strip, and joins the threads
def stop_program():
    lcd_display.lcd_clear()
    lcd_display.lcd_display_string("  Program stopped!  ")

    stop_motors()

    strip_thread.running = False
    strip_thread.colorWipe(strip, Color(0, 0, 0))
    LStrip.join()

    GPIO.cleanup()
    print("Exiting...")
    exit()


def stop_motors():
    M_Rot.running = False
    M_Lin.running = False
    M_Rot.stop()
    M_Lin.stop()
    print("\n---------- Motors Stopped! ----------")


def check_collision():
    if GPIO.input(inner_switch) == 0 or GPIO.input(outer_switch) == 0:
        print("\n---------- Collision Detected! ----------")
        stop_motors()


# def check_button():
#     if GPIO.input(exit_button) == 0


# Create Button thread
# button_thread = threading.Thread(target=check_button)

# Create LStrip thread
LStrip = threading.Thread(target=run_LedStrip)
lcd_display = lcd()

def main():
    try:
        GPIO.output(motor_relay, GPIO.LOW)
        GPIO.output(led_relay, GPIO.LOW)

        LStrip.start()
        lcd_display.lcd_clear()

        lcd_display.lcd_display_string(" Calibrating slide! ", 2)
        max_disp = calibrate_slide()
        lcd_display.lcd_clear()

        lcd_display.lcd_display_string("        ....        ", 2)
        process_new_files()

        files = get_files()
        shuffle(files)

        lcd_display.lcd_clear()

        first_file = True

        for f in files:
            track = read_track(f)

            if not first_file:
                lcd_display.lcd_clear()
                lcd_display.lcd_display_string("  Erasing Drawing!  ", 2)

                if round(track[0][1] / get_max_disp()) > 0:
                    erase_in_to_out()
                else:
                    erase_out_to_in()

            for i, step in enumerate(track):
                print(step)
                lcd_display.lcd_clear()
                lcd_display.lcd_display_string("Currently running:", 1)
                lcd_display.lcd_display_string(f, 2)
                lcd_display.lcd_display_string("Progress: {}/{}".format(i+1, track.shape[0]), 4)

                MLin_done = False
                MRot_done = False

                # Create motor threads
                MRot = threading.Thread(target=run_MRot, args=(step[0], step[2],))
                MLin = threading.Thread(target=run_MLin, args=(step[1], step[3],))

                print("...")
                MRot.start()
                MLin.start()

                while MRot_done or MLin_done:
                    check_collision()

                MRot.join()
                MLin.join()

            first_file = False

    except KeyboardInterrupt:
        stop_program()


if __name__ == '__main__':
    main()
