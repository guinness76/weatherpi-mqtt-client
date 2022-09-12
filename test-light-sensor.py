#!/usr/bin/python3

from sensors import PiLightSensor
from time import sleep

sensor = PiLightSensor()

print("Waiting for 10 second light sensor test:")

acc = 0
while(acc < 10):
    # 0.0V = full sunlight
    # 3.3V = full darkness
    print("Light sensor voltage: %f" % (sensor.getVoltage()))
    sleep(1)
    acc += 1

print("----- Light sensor test complete -----")