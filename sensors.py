#!/usr/bin/python3
import os, glob, time
import math
from gpiozero import Button,MCP3008
from signal import pause
from time import sleep

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

# Argent Data Systems wind speed and wind direction sensors- read via SPI bus on the Pi
# Wind speed connected to pin 29 (GPIO 5) and ground
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

# Wind direction vane: uses MCP3008 analog to digital converter as the Pi cannot handle analog inputs directly.
# It converts the current resistance of the vane to one of 16 different voltage readings that correspond to the 
# angle of the vane.
# Vin (3.3v) 
# Pin 1 (CH0) of MCP3008
#
# Other MCP3008 connections:
# Pins 16 and 15 (VDD and VRef) : connected to Vin (3.3v)
# Pin 14 (AGND): connected to ground
# Pin 13 (CLK): connected to SCLK/GPIO 11 (pin 23) on Pi
# Pin 12 (DOUT): connected to MISO/GPIO 9 (pin 21) on Pi
# Pin 11 (DIN): connected to MOSI/GPIO 10 (pin 19) on Pi
# Pin 10 (CS/SHDN): connected to CE0/GPIO 8 (pin 24) on Pi
# Pin 9 (DGND): connected to ground
# Pins 2-7 are other channel pins and remain unconnected
class WindVane():
    def __init__(self):
        self.adc = MCP3008(channel=0)
        self.vref = 3.3
    
        # Values are calculated based on the Vout = Vin * R2/(R1 + R2) where 3.3 volts is used as Vin.
        # More info on the data sheet: https://www.argentdata.com/files/80422_datasheet.pdf
        self.angles = {}
        self.angles[0.4]=0
        self.angles[1.4]=22.5
        self.angles[1.2]=45
        self.angles[2.8]=67.5
        self.angles[2.7]=90
        self.angles[2.9]=112.5
        self.angles[2.2]=135
        self.angles[2.3]=157.5
        self.angles[1.8]=180
        self.angles[2.0]=202.5
        self.angles[0.7]=225
        self.angles[0.8]=247.5
        self.angles[0.1]=270
        self.angles[0.3]=292.5
        self.angles[0.2]=315
        self.angles[0.6]=337.5

    def getVoltage(self):
        # The current value * 3.3 volts, makes it easier to measure with a meter. Rounded to 1 decimal place
        return round(self.adc.value * self.vref, 1)

    # Returns the direction that the front of the wind vane is current pointing at. Returns -1 if the
    # supplied voltage is not in the map of voltages
    def getAngle(self):
        vout = self.getVoltage()
        if (vout in self.angles):
            return self.angles[vout]
        else:
            return -1

# Argent Data Systems rain volume sensor
# Connected to GPIO 6 (pin 31) and ground (pin 39 for convenience)
class RainVolume():
    def __init__(self):
        self.interval_secs=5
        self.drops = 0
        self.rainBucket = Button(6)
        self.rainBucket.when_pressed = self.onBucketDrop

    def onBucketDrop(self):
        self.drops = self.drops + 1
        # print("onBucketDrop fired")

    def getBucketDrops(self):
        return self.drops

    def resetBucketDrops(self):
        self.rotationCount = 0