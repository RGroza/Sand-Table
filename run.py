import RPi.GPIO as GPIO
from utils.DRV8825 import DRV8825
import threading
import math
from time import sleep
from random import shuffle
from subprocess import call

from rpi_ws281x import PixelStrip, Color
from led_strip import *

from utils.process_files import get_files, process_new_files, read_track, get_max_disp
from utils.i2c_lcd_driver import *


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
exit_button = 26

GPIO.setmode(GPIO.BCM)
GPIO.setup(outer_switch, GPIO.IN)
GPIO.setup(inner_switch, GPIO.IN)
GPIO.setup(exit_button, GPIO.IN)
GPIO.setup(motor_relay, GPIO.OUT)
GPIO.setup(led_relay, GPIO.OUT)

# Slide thresholds
center_to_min = 250
outer_to_max = 250


# Run through the LED strip routine
def run_LedStrip():
    strip.begin()

    while strip_thread.running:
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
def run_MRot(steps, delay):
    if steps != 0 and delay >= 0:
        if steps > 0:
            M_Rot.turn_steps(Dir='forward', steps=abs(steps), stepdelay=delay)
        else:
            M_Rot.turn_steps(Dir='backward', steps=abs(steps), stepdelay=delay)

    M_Rot.stop()
    M_Rot.running = False

    # print("M_Rot done!")


def run_MRot_until(Dir, delay):
    if delay >= 0:
        while M_Rot.running:
            M_Rot.turn_steps(Dir=Dir, steps=1, stepdelay=delay)

    M_Rot.stop()

    # print("M_Rot done!")


def run_MLin(steps, delay):
    if steps != 0 and delay >= 0:
        if steps > 0:
            M_Lin.turn_steps(Dir='forward', steps=abs(steps), stepdelay=delay)
        else:
            M_Lin.turn_steps(Dir='backward', steps=abs(steps), stepdelay=delay)

    M_Lin.stop()
    M_Lin.running = False

    # print("M_Lin done!")


def run_MLin_until(steps, delay):
    run_MLin(steps, delay)
    M_Rot.running = False


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
    sleep(1)
    M_Lin.turn_until_switch(Dir='forward', limit_switch=outer_switch, stepdelay=0.0002)
    M_Lin.turn_steps(Dir='backward', steps=outer_to_max, stepdelay=0.0002)
    print("Found edge")

    sleep(.5)
    MRot = threading.Thread(target=run_MRot_until, args=('forward', 0.00025,))
    MLin = threading.Thread(target=run_MLin_until, args=(-max_disp, 0.01,))

    print("Erasing...")
    MRot.start()
    MLin.start()

    MRot.join()
    MLin.join()


def erase_in_to_out():
    sleep(1)
    M_Lin.turn_until_switch(Dir='backward', limit_switch=inner_switch, stepdelay=0.0002)
    M_Lin.turn_steps(Dir='forward', steps=center_to_min, stepdelay=0.0002)
    print("Found edge")

    sleep(.5)
    MRot = threading.Thread(target=run_MRot_until, args=('forward', 0.00025,))
    MLin = threading.Thread(target=run_MLin_until, args=(max_disp, 0.01,))

    print("Erasing...")
    MRot.start()
    MLin.start()

    MRot.join()
    MLin.join()


class SwitchesThread():

    def __init__(self):
        self.running = True
        self.start_time = None
        self.switch_pressed = False
        self.shutdown_pressed = False
        self.collision_detected = False
        self.stop_program = False


    def check_all_switches(self):
        while self.running:
            sleep(.25)

            if not self.collision_detected:
                check_collision(self)

            if GPIO.input(exit_button) == 1:
                if not self.shutdown_pressed:
                    self.shutdown_pressed = True

            if self.shutdown_pressed and GPIO.input(exit_button) == 0:
                # Shutdown
                print("Shutdown pressed!")
                self.stop_program = True
                self.running = False
                stop_motors()


def check_collision(thread):
    if GPIO.input(inner_switch) == 0 or GPIO.input(outer_switch) == 0:
        if not thread.switch_pressed:
            thread.start_time = int(round(time.time() * 1000))
            thread.switch_pressed = True

        if thread.switch_pressed and thread.start_time != None:
            if int(round(time.time() * 1000)) - thread.start_time > 2000:
                print("\n---------- Collision Detected! ----------")
                lcd_display.lcd_clear()
                lcd_display.lcd_display_string("Collision Detected", 2, 1)

                stop_motors()
                thread.collision_detected = True
    else:
        thread.switch_pressed = False


# Stops the motors and LED strip, and joins the threads
def stop_program(shutdown=False):
    lcd_display.lcd_clear()
    lcd_display.lcd_display_string("  Program stopped!  ", 2)

    stop_motors()

    strip_thread.running = False
    strip_thread.colorWipe(strip, Color(0, 0, 0))
    LStrip.join()

    switches_thread.join()

    GPIO.cleanup()

    if shutdown:
        call("sudo shutdown -h now", shell=True)
    else:
        print("Exiting...")
        exit()


def stop_motors():
    M_Rot.running = False
    M_Lin.running = False
    M_Rot.stop()
    M_Lin.stop()
    print("\n---------- Motors Stopped! ----------")


# Switches thread object init
switches = SwitchesThread()

# Create switches thread
switches_thread = threading.Thread(target=switches.check_all_switches)

# Create LStrip thread
LStrip = threading.Thread(target=run_LedStrip)
lcd_display = lcd()

def main():
    global max_disp

    try:
        GPIO.output(motor_relay, GPIO.LOW)
        GPIO.output(led_relay, GPIO.LOW)

        LStrip.start()
        lcd_display.lcd_clear()

        lcd_display.lcd_display_string("Calibrating slide!", 2, 1)
        max_disp = calibrate_slide()
        lcd_display.lcd_clear()

        lcd_display.lcd_display_string("....", 2, 8)
        process_new_files()

        files = get_files()
        shuffle(files)

        lcd_display.lcd_clear()
        switches_thread.start()

        first_file = True

        for f in files:
            if not first_file:
                lcd_display.lcd_clear()
                lcd_display.lcd_display_string("Erasing Drawing!", 2, 2)

                switches.collision_detected = True
                M_Rot.running = True
                M_Lin.running = True

                erase_out_to_in()

                # if round(track[0][1] / get_max_disp()) > 0:
                #     erase_in_to_out()
                # else:
                #     erase_out_to_in()

                switches.collision_detected = False

            track = read_track(f)

            lcd_display.lcd_display_string("Currently running:", 1)
            lcd_display.lcd_display_string(f, 2)
            lcd_display.lcd_display_string("Progress: ", 4)

            for i, step in enumerate(track):
                print(step)

                lcd_display.lcd_display_string("          ", 4, 10)
                lcd_display.lcd_display_string("{}/{}".format(i+1, track.shape[0]), 4, 10)

                # Create motor threads
                MRot = threading.Thread(target=run_MRot, args=(step[0], step[2],))
                MLin = threading.Thread(target=run_MLin, args=(step[1], step[3],))

                print("...")
                M_Rot.running = True
                M_Lin.running = True
                MRot.start()
                MLin.start()

                MRot.join()
                MLin.join()

                if switches.collision_detected:
                    switches.switch_pressed = False
                    break

                if switches.stop_program:
                    stop_program(shutdown=True)

                print("Motors done!")

            first_file = False

    except KeyboardInterrupt:
        stop_program()


if __name__ == '__main__':
    main()
