import RPi.GPIO as GPIO
import time

MotorDir = [
    'forward',
    'backward',
]

ControlMode = [
    'hardware',
    'software',
]

class DRV8825():
    def __init__(self, dir_pin, step_pin, enable_pin, mode_pins):
        self.dir_pin = dir_pin
        self.step_pin = step_pin
        self.enable_pin = enable_pin
        self.mode_pins = mode_pins

        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(self.dir_pin, GPIO.OUT)
        GPIO.setup(self.step_pin, GPIO.OUT)
        GPIO.setup(self.enable_pin, GPIO.OUT)
        GPIO.setup(self.mode_pins, GPIO.OUT)

    def digital_write(self, pin, value):
        GPIO.output(pin, value)

    def Stop(self):
        self.digital_write(self.enable_pin, 1)

    def SetMicroStep(self, mode, stepformat):
        """
        (1) mode
            'hardware' :    Use the switch on the module to control the microstep
            'software' :    Use software to control microstep pin levels
                Need to put the All switch to 0
        (2) stepformat
            ('fullstep', 'halfstep', '1/4step', '1/8step', '1/16step', '1/32step')
        """
        microstep = {'fullstep': (0, 0, 0),
                     'halfstep': (1, 0, 0),
                     '1/4step': (0, 1, 0),
                     '1/8step': (1, 1, 0),
                     '1/16step': (0, 0, 1),
                     '1/32step': (1, 0, 1)}

        print("Control mode: ",mode)
        if (mode == ControlMode[1]):
            print("set pins")
            self.digital_write(self.mode_pins, microstep[stepformat])

    def TurnStep(self, stop_event, Dir, steps, stepdelay=0.005):
        if (Dir == MotorDir[0]):
            print("forward")
            self.digital_write(self.enable_pin, 0)
            self.digital_write(self.dir_pin, 0)
        elif (Dir == MotorDir[1]):
            print("backward")
            self.digital_write(self.enable_pin, 0)
            self.digital_write(self.dir_pin, 1)
        else:
            print("the dir must be : 'forward' or 'backward'")
            self.digital_write(self.enable_pin, 1)
            return

        if (steps == 0):
            return

        print("turn step: ",steps)
        for i in range(steps):
            self.digital_write(self.step_pin, True)
            time.sleep(stepdelay)
            self.digital_write(self.step_pin, False)
            if stop_event.wait(stepdelay):
                return

    def TurnStep_cali(self, Dir, steps, limit_switch, stepdelay=0.005):
        if (Dir == MotorDir[0]):
            # print("forward")
            self.digital_write(self.enable_pin, 0)
            self.digital_write(self.dir_pin, 0)
        elif (Dir == MotorDir[1]):
            # print("backward")
            self.digital_write(self.enable_pin, 0)
            self.digital_write(self.dir_pin, 1)
        else:
            # print("the dir must be : 'forward' or 'backward'")
            self.digital_write(self.enable_pin, 1)
            return

        if (steps == 0):
            return

        # print("turn step: ",steps)
        while steps > 0:
            if GPIO.input(limit_switch) == 0:
                return False
            self.digital_write(self.step_pin, True)
            time.sleep(stepdelay)
            self.digital_write(self.step_pin, False)
            time.sleep(stepdelay)
            steps -= 1

        return True

    def TurnStep_ROT(self, Dir, steps, stepdelay=0.005):
        if (Dir == MotorDir[0]):
            # print("forward")
            self.digital_write(self.enable_pin, 0)
            self.digital_write(self.dir_pin, 0)
        elif (Dir == MotorDir[1]):
            # print("backward")
            self.digital_write(self.enable_pin, 0)
            self.digital_write(self.dir_pin, 1)
        else:
            # print("the dir must be : 'forward' or 'backward'")
            self.digital_write(self.enable_pin, 1)
            return

        if (steps == 0):
            return

        # print("turn step: ",steps)
        while steps > 0:
            self.digital_write(self.step_pin, True)
            time.sleep(stepdelay)
            self.digital_write(self.step_pin, False)
            time.sleep(stepdelay)
            steps -= 1

        return True

    def TurnStep_test(self, Dir, steps, stepdelay=0.005):
        if (Dir == MotorDir[0]):
            # print("forward")
            self.digital_write(self.enable_pin, 0)
            self.digital_write(self.dir_pin, 0)
        elif (Dir == MotorDir[1]):
            # print("backward")
            self.digital_write(self.enable_pin, 0)
            self.digital_write(self.dir_pin, 1)
        else:
            # print("the dir must be : 'forward' or 'backward'")
            self.digital_write(self.enable_pin, 1)
            return

        if (steps == 0):
            return

        # print("turn step: ",steps)
        while steps > 0:
            self.digital_write(self.step_pin, True)
            time.sleep(stepdelay)
            self.digital_write(self.step_pin, False)
            time.sleep(stepdelay)
            steps -= 1

        return True

    def Turn(self, Dir, limit_switch, stepdelay=0.005):
        if (Dir == MotorDir[0]):
            # print("forward")
            self.digital_write(self.enable_pin, 0)
            self.digital_write(self.dir_pin, 0)
        elif (Dir == MotorDir[1]):
            # print("backward")
            self.digital_write(self.enable_pin, 0)
            self.digital_write(self.dir_pin, 1)
        else:
            # print("the dir must be : 'forward' or 'backward'")
            self.digital_write(self.enable_pin, 1)
            return

        # print("turn step: ",steps)
        pos = 0
        while GPIO.input(limit_switch) == 1:
            self.digital_write(self.step_pin, True)
            time.sleep(stepdelay)
            self.digital_write(self.step_pin, False)
            time.sleep(stepdelay)
            pos += 1

        if Dir == MotorDir[0]:
            return pos
        else:
            return -1*pos