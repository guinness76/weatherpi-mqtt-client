#!/usr/bin/python3
from sensors import DS18B20

tempSensor = DS18B20()
print("Temp probe: %s C" % tempSensor.read_temp())
print("----- Temp probe test complete -----")