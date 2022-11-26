#!/usr/bin/python3
from sensors import TempProbe
tempProbe = TempProbe()
reading = tempProbe.read_temp()

if reading is None:
    print("Could not read temp probe")
else:
    print("Temp probe: %s C" % tempProbe.read_temp())
print("----- Temp probe test complete -----")
