#!/usr/bin/python3

from sensors import WindSpeed, WindVane
from time import sleep

windSpeed = WindSpeed()
windVane = WindVane()

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
    print("Wind vane voltage: %f, corresponding to %d degrees" % (windVane.getVoltage(), windVane.getAngle()))
    sleep(1)
    acc += 1