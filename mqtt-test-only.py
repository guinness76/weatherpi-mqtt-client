#!/usr/bin/python3
import os, sys, json
import time
from datetime import datetime
from gpiozero import LED

import paho.mqtt.client as mqtt

broker_address="192.168.1.184"
username="pi"
password="brewme18"
topic = "sensors"
mqtt_led = LED(12)

# Turn off the LED. It will be turned on again when we confirm the message goes through.
mqtt_led.off()

def on_connect(client, userdata, flags, rc):
    print("connected with connection status: "+str(rc))
    
    # First part of the path is the topic. This value needs to be defined in Subscriptions in the MQTT engine custom namespace.
    # client.publish()
    tagDict = {"dummyFloatTag": 42.42, "dummyDateTag": datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    client.publish(topic, json.dumps(tagDict))
    print("Message processing complete")
    client.disconnect()
    mqtt_led.on()   # Turn on the LED for a second to confirm the message went through.
    time.sleep(1)


client = mqtt.Client("mytest")
client.username_pw_set(username=username, password=password)
client.on_connect = on_connect
client.connect(broker_address, 1883)

# Needed to keep the process alive. Without this, the on_connect() never gets a chance to fire.
# For this example, we stop with client.disconnect() in the on_connect function.
client.loop_forever()