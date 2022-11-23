#!/usr/bin/python3
from sensors import TempProbe
tempProbe = TempProbe()

print("Temp probe: %s C" % tempProbe.read_temp())
print("----- Temp probe test complete -----")
