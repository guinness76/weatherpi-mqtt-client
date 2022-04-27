#!/usr/bin/python3

import math
from gpiozero import Button,MCP3008
from signal import pause
from time import sleep

# Argent Data Systems wind speed and wind direction sensors- read via SPI bus on the Pi
# Wind speed connected to pin 29 (GPIO 5) and ground
# Wind direction connected to Vin (3.3v) and pin 1 (CH0) of MPC3008

# Other MPC3008 connections:
# Pins 16 and 15 (VDD and VRef) : connected to Vin (3.3v)
# Pin 14 (AGND): connected to ground
# Pin 13 (CLK): connected to SCLK/GPIO 11 (pin 23) on Pi
# Pin 12 (DOUT): connected to MISO/GPIO 9 (pin 21) on Pi
# Pin 11 (DIN): connected to MOSI/GPIO 10 (pin 19) on Pi
# Pin 10 (CS/SHDN): connected to CE0/GPIO 8 (pin 24) on Pi
# Pin 9 (DGND): connected to ground
# Pins 2-7 are other channel pins and remain unconnected


class WindSpeed():
    def __init__(self):
        self.radius_cm = 9.0
        self.interval_secs=5
        self.anemometor_factor=1.18	# Used to compensate for the mass of the anemometer
        self.circumference_cm = ((2.0 * self.radius_cm) * math.pi)
        self.anemometer = Button(5)
        self.rotationCount = 0
        self.anemometer.when_pressed = self.onSpin

    def onSpin(self):
        self.rotationCount = self.rotationCount + 1
        #print("onSpin fired")

    def getRotationCount(self):
        # Note that onSpin fires twice per rotation, so divide the total in 2
        return self.rotationCount / 2

    def getKmPerHour(self):
	# Note that onSpin fires twice per rotation, so divide the total rotations in 2
        dist_cm = self.circumference_cm * (self.rotationCount / 2.0)
        cm_per_sec = dist_cm / self.interval_secs
        cm_per_hour = cm_per_sec * 60 * 60
        km_per_hour = cm_per_hour / 100000.0
        return km_per_hour * self.anemometor_factor

    def resetRotationCount(self):
        self.rotationCount = 0

windSpeed = WindSpeed()
adc = MCP3008(channel=0)

print("Waiting for %d second wind speed test: spin the anemometer now" % windSpeed.interval_secs)
#pause()

acc = 0
while acc<windSpeed.interval_secs:
    sleep(1)
    acc += 1

kph = windSpeed.getKmPerHour()
rotations = windSpeed.getRotationCount()
print("At the end of %d seconds and %d rotation(s) . The wind speed was measured as %f kph, which converts to %f mph" % 
(windSpeed.interval_secs, rotations, kph, kph/1.609))

print("Waiting for 10 second wind direction test: move the wind vane now")

acc = 0
while(acc < 10):
    print("Wind vane voltage: %f" % round(adc.value * 3.3, 1))
    sleep(1)
    acc += 1