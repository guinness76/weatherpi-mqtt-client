#!/usr/bin/python3
import os, glob, time

# add the lines below to /etc/modules (reboot to take effect)
# w1-gpio
# w1-therm

# Watherproof temperature probe (DS18B20), connected directly to GPIO:
# V+ connected to pin 1 (3.3v)
# Ground connected to pin 6 (ground)
# Data wire connected to pin 7 (GPIO 4)
class DS18B20(object):
    def __init__(self):
        devices = glob.glob("/sys/bus/w1/devices/28*")
        if len(devices) == 0:
            self.device_file = None
        else:
            self.device_file = glob.glob("/sys/bus/w1/devices/28*")[0] + "/w1_slave"
        
    def read_temp_raw(self):
        f = open(self.device_file, "r")
        lines = f.readlines()
        print(lines)
        f.close()
        return lines
        
    def crc_check(self, lines):
        return lines[0].strip()[-3:] == "YES"
        
    def read_temp(self):
        if self.device_file is None:
            print("Temp sensor probe is not connected!")
            return -255

        temp_c = -255
        attempts = 0
        
        lines = self.read_temp_raw()
        success = self.crc_check(lines)
        
        while not success and attempts < 3:
            time.sleep(.2)
            lines = self.read_temp_raw()            
            success = self.crc_check(lines)
            attempts += 1
        
        if success:
            temp_line = lines[1]
            equal_pos = temp_line.find("t=")            
            if equal_pos != -1:
                temp_string = temp_line[equal_pos+2:]
                temp_c = float(temp_string)/1000.0
        
        return temp_c


tempSensor = DS18B20()
print("Temp probe: %s C" % tempSensor.read_temp())