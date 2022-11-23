#!/usr/bin/python3
import os, glob, time
import math
from gpiozero import Button,MCP3008
from signal import pause
from time import sleep
import board
import adafruit_bme680
import DS18B20 as DS

# BME680 sensor, communicating over the board's default I2C bus
# Vin connected to pin 17 (3.3v)
# Ground connected to pin 9 (ground)
# SDA connected to pin 3 (GPIO 2)
# SCL connected to pin 5 (GPIO 3)
#
# Add the lines below to /etc/modules (reboot to take effect)
# w1-gpio
# w1-therm
class BME680():
    def __init__(self):
        # Create sensor object, communicating over the board's default I2C bus
        i2c = board.I2C()   # uses board.SCL and board.SDA

        try:
            self.bme680 = adafruit_bme680.Adafruit_BME680_I2C(i2c)

            # change this to match the location's pressure (hPa) at sea level
            self.bme680.sea_level_pressure = 1013.25
        except ValueError as e:
            print("Exception thrown while initializing atmospheric sensors: %s" % e)
            self.bme680 = None

    # Returns ambient temperature in Centigrade
    def getTemperature(self):
        if self.bme680 is not None:
            return self.bme680.temperature
        else:
            return -255

    # Returns the gas reading as ohms. This will need some work to determine how useful this value really is.
    def getGas(self):
        if self.bme680 is not None:
            return self.bme680.gas
        else:
            return -1

    # Returns the humidity as a percentage between 0 and 100 percent.
    def getHumidity(self):
        if self.bme680 is not None:
            return self.bme680.relative_humidity
        else:
            return -1.0

    # Returns the barometric pressure as millibars (hPa)
    def getPressure(self):
        if self.bme680 is not None:
            return self.bme680.pressure
        else:
            return -1.0

# Watherproof temperature probe (DS18B20), connected directly to GPIO:
# V+ (red wire from sensor) connected to pin 1 (3.3v)
# Ground (blue wire from sensor) connected to pin 6 (ground)
# Data wire (yellow wire from sensor) connected to pin 7 (GPIO 4)
class TempProbe():
    def __init__(self):
        # We are using GPIO 4
        self.sensors = DS.scan(4)

        if len(self.sensors) == 0:
            print ("Temp probe was not found!")
        else:
            DS.pinsStartConversion([4])
            self.tempProbe = self.sensors[0]

    def read_temp(self):
        if self.tempProbe is None:
            print ("Temp probe was not found!")
            return -255
        else:
            return "{:.3f}".format(DS.read(False,4,self.tempProbe))

# !!!DEPRECATED!!!
# Watherproof temperature probe (DS18B20), connected directly to GPIO:
# V+ connected to pin 1 (3.3v)
# Ground connected to pin 6 (ground)
# Data wire connected to pin 7 (GPIO 4)
class DS18B20_Deprecated():
    def __init__(self):
        devices = glob.glob("/sys/bus/w1/devices/28*")
        if len(devices) == 0:
            self.device_file = None
        else:
            self.device_file = glob.glob("/sys/bus/w1/devices/28*")[0] + "/w1_slave"

    def read_temp_raw(self):
        f = open(self.device_file, "r")
        lines = f.readlines()
        #print(lines)
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
    def __init__(self, interval_secs):
        self.radius_cm = 9.0
        self.interval_secs=interval_secs
        self.anemometor_factor=1.18	# Used to compensate for the mass of the anemometer
        self.circumference_cm = ((2.0 * self.radius_cm) * math.pi)
        self.anemometer = Button(5)
        self.rotationCount = 0
        self.anemometer.when_pressed = self.onSpin

    def onSpin(self):
        self.rotationCount = self.rotationCount + 1
        #print("onSpin fired")

    def getRotationCount(self):
        return self.rotationCount

    def getKmPerHour(self):
        dist_cm = self.circumference_cm * (self.rotationCount)
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
        self.last_angle = -1

        # Values are calculated based on the Vout = Vin * R2/(R1 + R2) where 3.3 volts is used as Vin.
        # More info on the data sheet: https://www.argentdata.com/files/80422_datasheet.pdf
        # TODO Instant angle is -1! Measured voltage=2.600000 volts
        # TODO Instant angle is -1! Measured voltage=1.700000 volts
        # TODO Instant angle is -1! Measured voltage=1.900000 volts
        self.angles = {}
        self.angles[0.4]=0
        self.angles[1.4]=22.5
        self.angles[1.2]=45
        self.angles[2.8]=67.5
        self.angles[2.7]=90
        self.angles[2.9]=112.5
        self.angles[2.2]=135
        self.angles[2.3]=157.5
        self.angles[2.5]=169
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
            #print("Instant angle is -1! Measured voltage=%f volts" % vout)
            return -1

    # TODO Deprecated, will use average of the last 10 measurements instead
    def calculateAvgAngleInternal(self, angle0, angle1):
        # First, we need to find the quadrant of the 1st angle
        radian0 = math.radians(angle0)
        sin0 = math.sin(radian0)
        cos0 = math.cos(radian0)

        quadrant0 = 0
        if sin0 >= 0 and cos0 >= 0:
            quadrant0 = 1
        elif sin0 >= 0 and cos0 < 0:
            quadrant0 = 2
        elif sin0 < 0 and cos0 < 0:
            quadrant0 = 3
        else:
            quadrant0 = 4

        # Next, we need to find the quadrant of the 2nd angle
        radian1 = math.radians(angle1)
        sin1 = math.sin(radian1)
        cos1 = math.cos(radian1)

        quadrant1 = 0
        if sin1 >= 0 and cos1 >= 0:
            quadrant1 = 1
        elif sin1 >= 0 and cos1 < 0:
            quadrant1 = 2
        elif sin1 < 0 and cos1 < 0:
            quadrant1 = 3
        else:
            quadrant1 = 4

        if quadrant1 < quadrant0:
            # We have gone past 0 degrees. Need to compensate, otherwise we get incorrect values.
            angle0Mod = angle0 + 360
            calcMod = (angle0Mod+angle1)/2
            return calcMod % 360
        else:
            return (angle0+angle1)/2

    def getAvgAngle(self):
        theAngle = self.getAngle()
        if theAngle is not -1:
            # Only track the angle if it is a legit value
            if self.last_angle < 0:
                self.last_angle = theAngle
                return theAngle
            else:
                oldAngle = self.last_angle
                self.last_angle = theAngle
                avgAngle = self.calculateAvgAngleInternal(oldAngle, theAngle)
                # print ("Instant angle='%d' degrees, avg angle='%d' degrees, previous angle='%d' degrees" % (theAngle, avgAngle, oldAngle))
                return avgAngle


# Argent Data Systems rain volume sensor
# Connected to GPIO 6 (pin 31) and ground (pin 39 for convenience)
class RainVolume():
    def __init__(self):
        self.inches_per_drop = 0.011
        self.drops = 0
        self.rainBucket = Button(6)
        self.rainBucket.when_pressed = self.onBucketDrop

    def onBucketDrop(self):
        self.drops = self.drops + 1
        # print("onBucketDrop fired")

    def getBucketDrops(self):
        return self.drops

    # Returns the volume in inches that has been recorded since the last reset.
    def getVolumeInches(self):
        return self.drops * self.inches_per_drop

    def resetBucketDrops(self):
        self.drops = 0

class PiLightSensor():
    def __init__(self):
        self.adc = MCP3008(channel=1)
        self.vref = 3.3

    def getVoltage(self):
        # The current value * 3.3 volts, makes it easier to measure with a meter. Rounded to 1 decimal place
        return round(self.adc.value * self.vref, 1)