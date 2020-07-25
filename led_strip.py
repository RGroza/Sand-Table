#!/usr/bin/env python3
# NeoPixel library strandtest example
# Author: Tony DiCola (tony@tonydicola.com)
#
# Direct port of the Arduino NeoPixel library strandtest example.  Showcases
# various animations on a strip of NeoPixels.

import RPi.GPIO as GPIO
import time
from rpi_ws281x import PixelStrip, Color
import argparse

# LED strip configuration:
LED_COUNT = 52        # Number of LED pixels.
# LED_PIN = 18          # GPIO pin connected to the pixels (18 uses PWM!).
LED_PIN = 10        # GPIO pin connected to the pixels (10 uses SPI /dev/spidev0.0).
LED_FREQ_HZ = 1200000  # LED signal frequency in hertz (usually 800khz)
LED_DMA = 10          # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = 255  # Set to 0 for darkest and 255 for brightest
LED_INVERT = False    # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53

GPIO.setwarnings(False)

led_relay = 25
GPIO.setmode(GPIO.BCM)
GPIO.setup(led_relay, GPIO.OUT)

class LedStripThread():

    def __init__(self):
        self.running = True

    # Define functions which animate LEDs in various ways.
    def colorWipe(self, strip, color, wait_ms=50):
        """Wipe color across display a pixel at a time."""
        if not self.running: return
        for i in range(strip.numPixels()):
            if not self.running: break
            strip.setPixelColor(i, color)
            strip.show()
            time.sleep(wait_ms / 1000.0)

    def theaterChase(self, strip, color, wait_ms=50, iterations=10):
        """Movie theater light style chaser animation."""
        if not self.running: return
        for j in range(iterations):
            for q in range(3):
                if not self.running: break
                for i in range(0, strip.numPixels(), 3):
                    if not self.running: break
                    strip.setPixelColor(i + q, color)
                strip.show()
                time.sleep(wait_ms / 1000.0)
                for i in range(0, strip.numPixels(), 3):
                    if not self.running: break
                    strip.setPixelColor(i + q, 0)

    def wheel(self, pos):
        """Generate rainbow colors across 0-255 positions."""
        if not self.running: return
        if pos < 85:
            return Color(pos * 3, 255 - pos * 3, 0)
        elif pos < 170:
            pos -= 85
            return Color(255 - pos * 3, 0, pos * 3)
        else:
            pos -= 170
            return Color(0, pos * 3, 255 - pos * 3)

    def rainbow(self, strip, wait_ms=20, iterations=1):
        """Draw rainbow that fades across all pixels at once."""
        if not self.running: return
        for j in range(256 * iterations):
            if not self.running: break
            for i in range(strip.numPixels()):
                if not self.running: break
                strip.setPixelColor(i, self.wheel((i + j) & 255))
            strip.show()
            time.sleep(wait_ms / 1000.0)

    def rainbowCycle(self, strip, wait_ms=20, iterations=5):
        """Draw rainbow that uniformly distributes itself across all pixels."""
        if not self.running: return
        for j in range(256 * iterations):
            if not self.running: break
            for i in range(strip.numPixels()):
                if not self.running: break
                strip.setPixelColor(i, self.wheel(
                    (int(i * 256 / strip.numPixels()) + j) & 255))
            strip.show()
            time.sleep(wait_ms / 1000.0)

    def theaterChaseRainbow(self, strip, wait_ms=50):
        """Rainbow movie theater light style chaser animation."""
        if not self.running: return
        for j in range(256):
            for q in range(3):
                if not self.running: break
                for i in range(0, strip.numPixels(), 3):
                    if not self.running: break
                    strip.setPixelColor(i + q, self.wheel((i + j) % 255))
                strip.show()
                time.sleep(wait_ms / 1000.0)
                for i in range(0, strip.numPixels(), 3):
                    if not self.running: break
                    strip.setPixelColor(i + q, 0)


def strip_init():
    return PixelStrip(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)

# Main program logic follows:
if __name__ == '__main__':
    GPIO.output(led_relay, GPIO.LOW)

    time.sleep(.5)

    # Process arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--clear', action='store_true', help='clear the display on exit')
    args = parser.parse_args()

    # Create NeoPixel object with appropriate configuration.
    strip = PixelStrip(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
    # Intialize the library (must be called once before other functions).
    strip.begin()

    strip_thread = LedStripThread()

    print('Press Ctrl-C to quit.')
    if not args.clear:
        print('Use "-c" argument to clear LEDs on exit')

    try:

        while True:
            print('Color wipe animations.')
            strip_thread.colorWipe(strip, Color(255, 0, 0))  # Red wipe
            strip_thread.colorWipe(strip, Color(0, 255, 0))  # Blue wipe
            strip_thread.colorWipe(strip, Color(0, 0, 255))  # Green wipe
            print('Theater chase animations.')
            strip_thread.theaterChase(strip, Color(127, 127, 127))  # White theater chase
            strip_thread.theaterChase(strip, Color(127, 0, 0))  # Red theater chase
            strip_thread.theaterChase(strip, Color(0, 0, 127))  # Blue theater chase
            print('Rainbow animations.')
            strip_thread.rainbow(strip)
            strip_thread.rainbowCycle(strip)
            strip_thread.theaterChaseRainbow(strip)

    except KeyboardInterrupt:
        GPIO.output(led_relay, GPIO.HIGH)
        if args.clear:
            strip_thread.colorWipe(strip, Color(0, 0, 0), 10)
