# Overview
This project has two major components: a Raspberry Pi 4 running an [Ignition gateway server](https://inductiveautomation.com), and a Raspberry Pi Zero that measures weather sensors. The Pi Zero transmits the sensor data to the Ignition gateway via the [MQTT protocol](https://docs.chariot.io). The Ignition gateway captures and displays the raw data from the sensors, and stores historical data in a MariaDB database running on the Pi 4.

# Pi 4 Server
The server runs a non-commercial version of the Ignition SCADA software platform known as the [Maker edition](https://docs.inductiveautomation.com/display/DOC81/Ignition+Maker+Edition). This version is free to use for personal projects only, and requires a stable Internet connection to occasionally contact the Inductive Automation licensing servers. The gateway runs a visualization system known as Perspective to display the weather sensor data in a browser window. Sensor data is held in data structures called "tags". Each tag holds a specific sensor value. Tag values can be written to a MariaDB database using the Ignition historian module. This allows past values of each sensor to be retrieved later and displayed on a trend chart.
Ignition designer with sensor tags:
![Ignition designer screenshot](/ignition-gateway/perspective-screenshots/designer.png)

# Pi Zero
The Pi Zero runs a Python script that regularly retrieves weather sensor data from the GPIO pins. The `all-sensors-to-mqtt` script uses the `paho.mqtt.client` Python library to transmit the sensor data to the Ignition gateway running on the Pi 4.

## Sensors
The following sensors are currently connected to the Pi Zero to provide weather data.

### BME280 Atmospheric sensors
The BME280 package provides ambient temperature, humidity, pressure, and air quality sensors. 

The air quality sensor measures the gas in the ambient air and provides a resistance reading. The lower the reading, the worse air quality is. However, the measured resistance is not in relation to any other known air quality values, so its readings can only be compared to its past readings to give a relative idea of current air quality.

The ambient temperature sensor is not used in this project, as it was found that a temperature probe positioned under an awning gave more accurate temperature readings. The BME280 sensor was placed in an enclosure next to the Raspberry Pi 0's enclosure, and tended to heat up much more than the ambient air on hot days.

### Temperature probe
This is a waterproof probe connected to the Pi Zero. It can be used to measure ground temperature (to monitor for freezing ground temperature for example), or it can be used to measure ambient air temperature. Ambient air temperature measurements are only accurate as long as the probe is maintained in the shade, away from any structures or equipment that might retain heat.
