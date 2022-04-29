#!/usr/bin/python3
import json
import configparser
from datetime import datetime
import time
import paho.mqtt.client as mqtt
from sensors import BME680, DS18B20, WindSpeed, WindVane, RainVolume

# Read weatherpi.properties
config = configparser.RawConfigParser()
config.read('/home/pi/weatherpi-mqtt-client/weatherpi.properties')
mqtt_settings = dict(config.items("mqtt"))

broker_address=mqtt_settings["broker_address"]
username=mqtt_settings["username"]
password=mqtt_settings["password"]

# First part of the path is the topic. This value needs to be defined in Subscriptions in the MQTT engine custom namespace.
topic = "sensors"
measure_interval_secs = 5

tempProbe = DS18B20()
bme680 = BME680()
windSpeed = WindSpeed(measure_interval_secs)
windVane = WindVane()
bucket = RainVolume()

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
    tagDict = {}

    # Atmospheric sensors
    tagDict["bme680/ambientTemp"]=bme680.getTemperature() # Temp is Centrigrade
    tagDict["bme680/humidity"]=bme680.getHumidity() # Humidity is a float percentage between 0% and 100%
    tagDict["bme680/gas"]=bme680.getGas() # Gas is ohms
    tagDict["bme680/pressure"]=bme680.getPressure() # Pressure is hPa

    # Temperature probe
    tagDict["temp-probe/temperature"]=tempProbe.read_temp()

    # Wind sensors
    tagDict["wind/speed"]=windSpeed.getKmPerHour()
    tagDict["wind/direction"]=windVane.getAngle()

    # Rain sensor
    tagDict["rain/lastFiveSecs"]=bucket.getBucketDrops()
    
    # Last updated timestamp
    tagDict["diagnostics/lastUpdate"]=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    client.publish(topic, json.dumps(tagDict))

    # Reset the wind and rain objects, since they measure a quantity collected every 5 seconds
    windSpeed.resetRotationCount()
    bucket.resetBucketDrops()

    time.sleep(measure_interval_secs)