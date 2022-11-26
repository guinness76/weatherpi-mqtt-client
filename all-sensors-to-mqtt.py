#!/usr/bin/python3
import json
import subprocess
import configparser
from datetime import datetime
import time
import paho.mqtt.client as mqtt
from sensors import BME680, TempProbe, WindSpeed, WindVane, RainVolume, PiLightSensor
from gpiozero import LED

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

tempProbe = TempProbe()
bme680 = BME680()
windSpeed = WindSpeed(measure_interval_secs)
windVane = WindVane()
bucket = RainVolume()
light = PiLightSensor()

mqtt_led = LED(12)

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

atmoSensorsEnabled = True
tempProbeEnabled = True
windSensorsEnabled = True
rainSensorEnabled = True
lightSensorEnabled = True

theResult = subprocess.run(["hostname", "-I"], stdout=subprocess.PIPE)
ipAddr = theResult.stdout.decode('utf-8')

while True:
    tagDict = {}
    # Turn off the LED. It will be turned on again when we confirm the message goes through.
    mqtt_led.off()

    # Atmospheric sensors
    if atmoSensorsEnabled:
        tagDict["bme680/ambientTemp"]=bme680.getTemperature() # Temp is Centrigrade
        tagDict["bme680/humidity"]=bme680.getHumidity() # Humidity is a float percentage between 0% and 100%
        tagDict["bme680/gas"]=bme680.getGas() # Gas is ohms
        tagDict["bme680/pressure"]=bme680.getPressure() # Pressure is hPa

    # Temperature probe
    if tempProbeEnabled:
        probeVal = tempProbe.read_temp()
        # Only send if we have a good reading. Otherwise a bad value screws up the history.
        if probeVal != "-255":
            tagDict["temp-probe/temperature"]=probeVal

    # Wind sensors
    if windSensorsEnabled:
        tagDict["wind/speed"]=windSpeed.getKmPerHour()
        tagDict["wind/direction"]=windVane.getAngle()

    # Rain sensor
    if rainSensorEnabled:
        tagDict["rain/inchesLastFiveSecs"]=bucket.getVolumeInches()

   # Light sensor
    if lightSensorEnabled:
        tagDict["lightSensor/voltage"]=light.getVoltage()        

    # WeatherPi current IP address
    #hostname -I | awk '{print $1}'
    
    # Last updated timestamp
    tagDict["diagnostics/lastUpdate"]=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    tagDict["diagnostics/ipAddr"]=ipAddr
    client.publish(topic, json.dumps(tagDict))
    mqtt_led.on()

    # Reset the wind and rain objects, since they measure a quantity collected every 5 seconds
    windSpeed.resetRotationCount()
    bucket.resetBucketDrops()

    time.sleep(measure_interval_secs)