import RPi.GPIO as GPIO
from DRV8825 import DRV8825
import threading
import math
from time import sleep
import keyboard
from rpi_ws281x import PixelStrip, Color

    
isStillMoving = False #flag that motors are to be moving

# LED strip configuration:
LED_COUNT = 52        # Number of LED pixels.
# LED_PIN = 18          # GPIO pin connected to the pixels (18 uses PWM!).
LED_PIN = 10        # GPIO pin connected to the pixels (10 uses SPI /dev/spidev0.0).
LED_FREQ_HZ = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA = 10          # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = 255  # Set to 0 for darkest and 255 for brightest
LED_INVERT = False    # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53


M_Rot = DRV8825(dir_pin=13, step_pin=19, enable_pin=12, mode_pins=(16, 17, 20))
M_Lin = DRV8825(dir_pin=24, step_pin=18, enable_pin=4, mode_pins=(21, 22, 27))

# Create NeoPixel object with appropriate configuration.
strip = PixelStrip(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)


def run_LedStrip(stop_event):
    strip.begin()

    while isStillMoving:
        print('Color wipe animations.')
        colorWipe(strip, Color(255, 0, 0))  # Red wipe
        colorWipe(strip, Color(0, 255, 0))  # Blue wipe
        colorWipe(strip, Color(0, 0, 255))  # Green wipe
        print('Theater chase animations.')
        theaterChase(strip, Color(127, 127, 127))  # White theater chase
        theaterChase(strip, Color(127, 0, 0))  # Red theater chase
        theaterChase(strip, Color(0, 0, 127))  # Blue theater chase
        print('Rainbow animations.')
        rainbow(strip)
        rainbowCycle(strip)
        theaterChaseRainbow(strip)
    

def run_MRotate(stop_event):
    M_Rot.SetMicroStep('software','1/4step')
    rot_delay = 0.0015
    rot_steps = 3200
    while isStillMoving:
        M_Rot.TurnStep_ROT(Dir='forward', steps=rot_steps, stepdelay = rot_delay)
    M_Rot.Stop()

def run_MLinear(num_steps, delay, stop_event):
    M_Lin.SetMicroStep('software','1/4step')
    if num_steps > 0:
        M_Lin.TurnStep(stop_event, Dir='forward', steps=num_steps, stepdelay = delay)
    else:
        M_Lin.TurnStep(stop_event, Dir='backward', steps=abs(num_steps), stepdelay = delay)

def run_MLin(num_steps, delay, stop_event):
    M_Lin.SetMicroStep('software','1/4step')
    if num_steps > 0:
        M_Lin.TurnStep(stop_event, Dir='forward', steps=num_steps, stepdelay = delay)
    else:
        M_Lin.TurnStep(stop_event, Dir='backward', steps=abs(num_steps), stepdelay = delay)
    M_Lin.Stop()

def calibrate_slide():
    outer_switch = 5
    inner_switch = 6

    GPIO.setmode(GPIO.BCM)
    GPIO.setup(outer_switch, GPIO.IN)
    GPIO.setup(inner_switch, GPIO.IN)

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
        print ("Travel Distance: " + str(totalDist))

        sleep(2)

        test_inner = M_Lin.Turn_check_cali(Dir='backward', steps=totalDist + outer_to_max, limit_switch=inner_switch, stepdelay=delay)
        minPos = 0
        sleep(2)
        test_outer = M_Lin.Turn_check_cali(Dir='forward', steps=totalDist, limit_switch=outer_switch, stepdelay=delay)
        maxPos = totalDist
        test_inner = M_Lin.Turn_check_cali(Dir='backward', steps=totalDist, limit_switch=inner_switch, stepdelay=delay)

        if test_inner and test_outer:
            calibrated = True
        else:
            print("Calibration Failed! Trying again...")
    print("Calibration Passed!")

    return totalDist

# Define functions which animate LEDs in various ways.
def colorWipe(strip, color, wait_ms=50):
    """Wipe color across display a pixel at a time."""
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, color)
        strip.show()
        sleep(wait_ms / 1000.0)


def theaterChase(strip, color, wait_ms=50, iterations=10):
    """Movie theater light style chaser animation."""
    for j in range(iterations):
        for q in range(3):
            for i in range(0, strip.numPixels(), 3):
                strip.setPixelColor(i + q, color)
            strip.show()
            sleep(wait_ms / 1000.0)
            for i in range(0, strip.numPixels(), 3):
                strip.setPixelColor(i + q, 0)


def wheel(pos):
    """Generate rainbow colors across 0-255 positions."""
    if pos < 85:
        return Color(pos * 3, 255 - pos * 3, 0)
    elif pos < 170:
        pos -= 85
        return Color(255 - pos * 3, 0, pos * 3)
    else:
        pos -= 170
        return Color(0, pos * 3, 255 - pos * 3)


def rainbow(strip, wait_ms=20, iterations=1):
    """Draw rainbow that fades across all pixels at once."""
    for j in range(256 * iterations):
        for i in range(strip.numPixels()):
            strip.setPixelColor(i, wheel((i + j) & 255))
        strip.show()
        sleep(wait_ms / 1000.0)


def rainbowCycle(strip, wait_ms=20, iterations=5):
    """Draw rainbow that uniformly distributes itself across all pixels."""
    for j in range(256 * iterations):
        for i in range(strip.numPixels()):
            strip.setPixelColor(i, wheel(
                (int(i * 256 / strip.numPixels()) + j) & 255))
        strip.show()
        sleep(wait_ms / 1000.0)


def theaterChaseRainbow(strip, wait_ms=50):
    """Rainbow movie theater light style chaser animation."""
    for j in range(256):
        for q in range(3):
            for i in range(0, strip.numPixels(), 3):
                strip.setPixelColor(i + q, wheel((i + j) % 255))
            strip.show()
            sleep(wait_ms / 1000.0)
            for i in range(0, strip.numPixels(), 3):
                strip.setPixelColor(i + q, 0)


def stop_program(threading_event):
    threading_event.set()
    isStillMoving = False
    colorWipe(strip, Color(0, 0, 0), 10)
    MRot.join()
    LStrip.join()
    #MLin.join()
    print("\nMotors stopped")
    M_Rot.Stop()
    #M_Lin.Stop()
    GPIO.cleanup()
    print("Exiting...")
    exit()

default_speed = 750
max_speed = 1000
rev_steps = 3200
currentTheta = 0 # theta coordinate val - currently just incrementer
theta_steps = 100
LinPos = 0
LastLinPos = 0
Lin_delay = 0.00125

try:
    maxDisp = calibrate_slide() - 50
    threading_event = threading.Event()
    isStillMoving = True

    # start Rotation
    MRot = threading.Thread(target=run_MRotate, args=(threading_event,))
    LStrip = threading.Thread(target=run_LedStrip, args=(threading_event,))
    MRot.start()
    print("\nROT Thread Started")
    LStrip.start()
    print("\nLed Strip Thread Started")

    while isStillMoving:
        LastLinPos = LinPos
        LinPos = round(maxDisp * abs(math.cos(math.radians(360 * currentTheta / rev_steps)))) # r coordinate val
        currentTheta += theta_steps

        print(str(LinPos))

        nextPos = LinPos - LastLinPos
        run_MLinear (nextPos, Lin_delay, threading_event,)

except KeyboardInterrupt:
    stop_program(threading_event)