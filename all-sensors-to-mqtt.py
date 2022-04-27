#!/usr/bin/python3
import adafruit_bme680
import board
import os, sys, glob, json
from datetime import datetime
import time
import paho.mqtt.client as mqtt

broker_address="192.168.1.184"
username="pi"
password="brewme18"
topic = "sensors"

# Weatherproof temperature probe (DS18B20), connected directly to GPIO:
# V+ connected to pin 1 (3.3v)
# Ground connected to pin 6 (ground)
# Data wire connected to pin 7 (GPIO 4)
class DS18B20(object):
    def __init__(self):        
        self.device_file = glob.glob("/sys/bus/w1/devices/28*")[0] + "/w1_slave"
        
    def read_temp_raw(self):
        f = open(self.device_file, "r")
        lines = f.readlines()
        f.close()
        return lines
        
    def crc_check(self, lines):
        return lines[0].strip()[-3:] == "YES"
        
    def read_temp(self):
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

# BME680 sensor, communicating over the board's default I2C bus
# Vin connected to pin 17 (3.3v)
# Ground connected to pin 9 (ground)
# SDA connected to pin 3 (GPIO 2)
# SCL connected to pin 5 (GPIO 3)
i2c = board.I2C()   # uses board.SCL and board.SDA
bme680 = adafruit_bme680.Adafruit_BME680_I2C(i2c)

# change this to match the location's pressure (hPa) at sea level
bme680.sea_level_pressure = 1013.25

# def on_connect(client, userdata, flags, rc):
#     #print("connected with connection status: "+str(rc))
#     #time.sleep(5)   # Run forever until the script is stopped
#     #client.disconnect()

client = mqtt.Client("weatherpi")
client.username_pw_set(username=username, password=password)
#client.on_connect = on_connect
client.connect(broker_address, 1883)

# Needed to keep the process alive. Without this, the on_connect() never gets a chance to fire.
# For this example, we stop with client.disconnect() in the on_connect function.
#client.loop_forever()

client.loop_start()

while True:
    # First part of the path is the topic. This value needs to be defined in Subscriptions in the MQTT engine custom namespace.
    temp = bme680.temperature   # Temp is Centrigrade
    humidity = bme680.relative_humidity
    gas = bme680.gas    # Gas is ohms
    pressure = bme680.pressure  # Pressure is hPa
    #altitude = bme680.altitude

    tagDict = {}
    tagDict["bme680/ambientTemp"]= temp
    tagDict["bme680/humidity"]= humidity
    tagDict["bme680/gas"]=gas
    tagDict["bme680/pressure"]=pressure
    tagDict["ds18b20/temperature"]=tempSensor.read_temp()
    tagDict["diagnostics/lastUpdate"]=datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    client.publish(topic, json.dumps(tagDict))
    time.sleep(5)