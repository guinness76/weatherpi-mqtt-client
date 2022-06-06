# Overview
This project has two major components: a Raspberry Pi 4 running an [Ignition gateway server](https://inductiveautomation.com), and a Raspberry Pi Zero that measures weather sensors. The Pi Zero transmits the sensor data to the Ignition gateway via the [MQTT protocol](https://docs.chariot.io). The Ignition gateway captures and displays the raw data from the sensors, and stores historical data in a MariaDB database running on the Pi 4.

# Pi 4 Server
The server runs a non-commercial version of the Ignition SCADA software platform known as the [Maker edition](https://docs.inductiveautomation.com/display/DOC81/Ignition+Maker+Edition). This version is free to use for personal projects only, and requires a stable Internet connection to occasionally contact the Inductive Automation licensing servers. The gateway runs a visualization system known as Perspective to display the weather sensor data in a browser window. Sensor data is held in data structures called "tags". Each tag holds a specific sensor value. Tag values can be written to a MariaDB database using the Ignition historian module. This allows past values of each sensor to be retrieved later and displayed on a trend chart.
Ignition designer with sensor tags:
![Ignition designer screenshot](/ignition-gateway/perspective-screenshots/designer.png)

# Pi Zero
The Pi Zero runs a Python script that regularly retrieves weather sensor data from the GPIO pins. The script uses the `paho.mqtt.client` Python library to transmit the sensor data to the Ignition gateway running on the Pi 4.
