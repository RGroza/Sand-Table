import RPi.GPIO as GPIO
from utils.i2c_lcd_driver import *


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

    def check_all_switches(self):
        while self.running:
            sleep(.1)

            if not self.collision_detected:
                self.check_collision()

            if GPIO.input(main_button) == 1:
                if not self.main_pressed:
                    self.main_pressed = True
                    self.main_start_time = int(round(time.time() * 1000))

            if not self.displaying_options:
                if self.main_pressed and GPIO.input(main_button) == 0:
                    if int(round(time.time() * 1000)) - self.main_start_time > 4000:
                        self.stop_program = True
                        self.running = False
                        stop_motors()
                    else:
                        self.displaying_options = True
                        self.main_pressed = False
                        self.display_options()
            else:
                if self.main_pressed and GPIO.input(main_button) == 0:
                    if int(round(time.time() * 1000)) - self.main_start_time > 2000:
                        self.select_option()
                    else:
                        self.selected_option = (self.selected_option + 1) % 3
                        self.display_options()


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


    def display_options(self):
        lcd_display.lcd_clear()
        for o in self.options:
            if o == self.selected_option:
                lcd_display.lcd_display_string("[ {} ]".format(self.options[o]), o + 1, round((16 - len(self.options[o])) / 2))
            else:
                lcd_display.lcd_display_string(self.options[o], o + 1, round((20 - len(self.options[o])) / 2))