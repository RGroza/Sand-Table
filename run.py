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
main_button = 26

GPIO.setmode(GPIO.BCM)
GPIO.setup(outer_switch, GPIO.IN)
GPIO.setup(inner_switch, GPIO.IN)
GPIO.setup(main_button, GPIO.IN)
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
    lcd_display.lcd_clear()
    lcd_display.lcd_display_string("Erasing Drawing!", 2, 2)

    interface.collision_detected = True
    M_Rot.running = True
    M_Lin.running = True

    sleep(1)
    M_Lin.turn_until_switch(Dir='forward', limit_switch=outer_switch, stepdelay=0.0002)
    M_Lin.turn_steps(Dir='backward', steps=outer_to_max, stepdelay=0.0002)
    print("Found edge")

    sleep(.5)
    MRot = threading.Thread(target=run_MRot_until, args=('forward', 0.0005,))
    MLin = threading.Thread(target=run_MLin_until, args=(-max_disp, 0.01,))

    print("Erasing...")
    MRot.start()
    MLin.start()

    MRot.join()
    MLin.join()

    interface.collision_detected = False


# def erase_in_to_out():
#     sleep(1)
#     M_Lin.turn_until_switch(Dir='backward', limit_switch=inner_switch, stepdelay=0.0002)
#     M_Lin.turn_steps(Dir='forward', steps=center_to_min, stepdelay=0.0002)
#     print("Found edge")

#     sleep(.5)
#     MRot = threading.Thread(target=run_MRot_until, args=('forward', 0.00035,))
#     MLin = threading.Thread(target=run_MLin_until, args=(max_disp, 0.01,))

#     print("Erasing...")
#     MRot.start()
#     MLin.start()

#     MRot.join()
#     MLin.join()


def wait_for_erase():
    lcd_display.lcd_clear()
    lcd_display.lcd_display_string("Drawing will be", 2, 2)
    lcd_display.lcd_display_string("erased in... ", 2, 2)
    for i in range(60):
        lcd_display.lcd_display_string(str(60 - i), 2, 17)
        sleep(1)


class InterfaceThread():

    def __init__(self):
        self.running = True
        self.collision_start_time = None
        self.main_start_time = None
        self.limit_pressed = False
        self.main_pressed = False
        self.collision_detected = False
        self.next_drawing = False
        self.stop_program = False
        self.displaying_options = False

        self.options = {0: "Back", 1: "Shutdown", 2: "Stop/erase"}
        self.selected_option = 0

        self.currently_displayed = []

    def check_all_switches(self):
        while self.running:
            sleep(.1)

            if not self.main_pressed and GPIO.input(main_button) == 1:
                self.main_pressed = True
                self.main_start_time = int(round(time.time() * 1000))

            if not self.displaying_options and self.main_pressed:
                # if GPIO.input(main_button) == 1 and int(round(time.time() * 1000)) - self.main_start_time > 3000:
                #     self.main_pressed = False
                #     self.stop_program = True
                #     self.running = False
                #     print("Shutdown!")
                #     # stop_motors()

                if GPIO.input(main_button) == 0:
                    self.main_pressed = False
                    self.displaying_options = True
                    self.display_options()

            if self.displaying_options and self.main_pressed:
                if GPIO.input(main_button) == 0 and int(round(time.time() * 1000)) - self.main_start_time > 2000:
                    self.main_pressed = False
                    self.select_option()
                elif GPIO.input(main_button) == 0:
                    self.main_pressed = False
                    self.selected_option = (self.selected_option + 1) % 3
                    self.display_options()


    def display_options(self):
        lcd_display.lcd_clear()
        for o in self.options:
            if o == self.selected_option:
                lcd_display.lcd_display_string("[ {} ]".format(self.options[o]), o + 1, round((16 - len(self.options[o])) / 2))
            else:
                lcd_display.lcd_display_string(self.options[o], o + 1, round((20 - len(self.options[o])) / 2))


    def select_option(self):
        lcd_display.lcd_clear()
        self.displaying_options = False

        if self.selected_option == 0:
            print("Back")
            if (len(self.currently_displayed) > 0):
                for n in self.currently_displayed:
                    lcd_display.lcd_display_string(n[0], n[1], n[2])
        elif self.selected_option == 1:
            self.stop_program = True
            self.running = False
            print("Shutdown!")
            stop_motors()
        else:
            self.next_drawing = True
            print("Erasing!")
            lcd_display.lcd_clear()


    def check_collision(self):
        if GPIO.input(inner_switch) == 0 or GPIO.input(outer_switch) == 0:
            if not self.limit_pressed:
                self.collision_start_time = int(round(time.time() * 1000))
                self.limit_pressed = True

            if self.limit_pressed and self.collision_start_time != None:
                if int(round(time.time() * 1000)) - self.collision_start_time > 2000:
                    print("\n---------- Collision Detected! ----------")
                    lcd_display.lcd_clear()
                    lcd_display.lcd_display_string("Collision Detected", 2, 1)

                    stop_motors()
                    self.collision_detected = True
        else:
            self.limit_pressed = False


# Stops the motors and LED strip, and joins the threads
def stop_program(shutdown=False):
    if shutdown:
        lcd_display.lcd_clear()
        lcd_display.lcd_display_string("Shutting down...", 2, 2)
    else:
        lcd_display.lcd_clear()
        lcd_display.lcd_display_string("Program stopped!", 2, 2)

    stop_motors()

    strip_thread.running = False
    strip_thread.colorWipe(strip, Color(0, 0, 0))
    LStrip.join()

    interface.running = False
    interface_thread.join()

    if shutdown:
        sleep(2)

        lcd_display.lcd_clear()
        GPIO.cleanup()

        lcd_display.lcd_clear()
        lcd_display.lcd_display_string("Wait at least 10 sec", 2)
        lcd_display.lcd_display_string("before restarting!", 3, 1)
        sleep(3)
        lcd_display.lcd_clear()
        lcd_display.backlight(0)

        call("sudo shutdown -h now", shell=True)
    else:
        GPIO.cleanup()
        print("Exiting...")
        exit()


def stop_motors():
    M_Rot.running = False
    M_Lin.running = False
    M_Rot.stop()
    M_Lin.stop()
    print("\n---------- Motors Stopped! ----------")


# Switches thread object init
interface = InterfaceThread()

# Create switches thread
interface_thread = threading.Thread(target=interface.check_all_switches)

# Create LStrip thread
LStrip = threading.Thread(target=run_LedStrip)
lcd_display = lcd()

def main():
    global max_disp

    try:
        lcd_display.backlight(1)

        GPIO.output(motor_relay, GPIO.LOW)
        GPIO.output(led_relay, GPIO.LOW)

        LStrip.start()

        lcd_display.lcd_clear()
        lcd_display.lcd_display_string("....", 2, 8)
        process_new_files(Dir="/home/pi/Sand-Table/")

        # files = get_files(Dir="/home/pi/Sand-Table/")
        with open("/home/pi/Sand-Table/filenames.txt", "r") as f:
            content = f.readlines()
        files = [line.rstrip('\n') for line in content]
        shuffle(files)

        interface_thread.start()

        if not interface.displaying_options:
            lcd_display.lcd_clear()
            lcd_display.lcd_display_string("Calibrating slide!", 2, 1)

        interface.currently_displayed.clear()
        interface.currently_displayed.extend((("Calibrating slide!", 2, 1)))

        max_disp = calibrate_slide()

        if not interface.displaying_options:
            lcd_display.lcd_clear()

        if len(files) == 0:
            lcd_display.lcd_display_string("Files not found!", 2, 2)
            interface.currently_displayed.clear()
            interface.currently_displayed.extend((("Files not found!", 2, 2)))

        first_file = True

        while not interface.stop_program:

            for f in files:
                if interface.stop_program:
                    break

                if not first_file:
                    if not interface.next_drawing:
                        wait_for_erase()
                    erase_out_to_in()

                    if interface.stop_program:
                        break

                print("Running: {}".format(f))
                if not interface.displaying_options:
                    lcd_display.lcd_clear()
                    lcd_display.lcd_display_string("Reading file....", 2)
                    lcd_display.lcd_display_string(f, 3)

                interface.currently_displayed.clear()
                interface.currently_displayed.extend((("Reading file....", 2, 0), (f, 3, 0)))

                track = read_track(f, Dir="/home/pi/Sand-Table/")

                if not interface.displaying_options:
                    lcd_display.lcd_clear()

                # prog_disp_interrupted = False

                if not interface.displaying_options:
                    lcd_display.lcd_display_string("Currently running:", 1)
                    lcd_display.lcd_display_string(f, 2)
                    lcd_display.lcd_display_string("Progress: ", 4)
                # else:
                #     prog_disp_interrupted = True

                interface.currently_displayed.clear()
                interface.currently_displayed.extend((("Currently running:", 1, 0), (f, 2, 0), ("Progress: ", 4, 0)))

                first_step = True

                for i, step in enumerate(track):
                    print(step)

                    # if interface.displaying_options:
                    #     prog_disp_interrupted = True

                    # if prog_disp_interrupted and not interface.displaying_options:
                    #     lcd_display.lcd_display_string("Currently running:", 1)
                    #     lcd_display.lcd_display_string(f, 2)
                    #     lcd_display.lcd_display_string("Progress: ", 4)
                    #     prog_disp_interrupted = False

                    if not interface.displaying_options:
                        lcd_display.lcd_display_string("          ", 4, 10)
                        lcd_display.lcd_display_string("{}/{}".format(i+1, track.shape[0]), 4, 10)

                    if first_step:
                        interface.currently_displayed.extend((("          ", 4, 10), ("{}/{}".format(i+1, track.shape[0]), 4, 10)))
                    else:
                        interface.currently_displayed[3] = ("          ", 4, 10)
                        interface.currently_displayed[4] = ("{}/{}".format(i+1, track.shape[0]), 4, 10)

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

                    if interface.collision_detected:
                        interface.limit_pressed = False
                        break

                    if interface.stop_program or interface.next_drawing:
                        break

                    # print("Motors done!")
                    first_step = False

                first_file = False
                interface.currently_displayed.clear()

        if interface.stop_program:
            stop_program(shutdown=True)

    except KeyboardInterrupt:
        stop_program()


if __name__ == '__main__':
    main()
