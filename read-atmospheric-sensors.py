#!/usr/bin/python3
import os, glob, time
import adafruit_bme680
import board

# BME680 sensor, communicating over the board's default I2C bus
# Vin connected to pin 17 (3.3v)
# Ground connected to pin 9 (ground)
# SDA connected to pin 3 (GPIO 2)
# SCL connected to pin 5 (GPIO 3)

# add the lines below to /etc/modules (reboot to take effect)
# w1-gpio
# w1-therm

# Create sensor object, communicating over the board's default I2C bus
i2c = board.I2C()   # uses board.SCL and board.SDA

try:
    bme680 = adafruit_bme680.Adafruit_BME680_I2C(i2c)

    # change this to match the location's pressure (hPa) at sea level
    bme680.sea_level_pressure = 1013.25

    print("\nTemperature: %0.1f C" % bme680.temperature)
    print("Gas: %d ohm" % bme680.gas)
    print("Humidity: %0.1f %%" % bme680.relative_humidity)
    print("Pressure: %0.3f hPa" % bme680.pressure)
    print("Altitude = %0.2f meters" % bme680.altitude)
except ValueError as e:
    print("Exception thrown: %s" % e)