# Overview
This project has two major components: a Raspberry Pi 4 running an [Ignition gateway server](https://inductiveautomation.com), and a Raspberry Pi Zero that measures weather sensors. The Pi Zero transmits the sensor data to the Ignition gateway via the [MQTT protocol](https://docs.chariot.io). The Ignition gateway captures and displays the raw data from the sensors, and stores historical data in a MariaDB database running on the Pi 4. Inspiration for this project was heavily influenced by [electromaker.io](https://www.electromaker.io/project/view/build-your-own-weather-station)

# Pi 4 Server
The server runs a non-commercial version of the Ignition SCADA software platform known as the [Maker edition](https://docs.inductiveautomation.com/display/DOC81/Ignition+Maker+Edition). This version is free to use for personal projects only, and requires a stable Internet connection to occasionally contact the Inductive Automation licensing servers. 

The gateway runs a MQTT server using the [Cirrus Link](https://cirrus-link.com/mqtt-software-for-iiot-scada) MQTT Distributor module and the MQTT Engine module. The module need to be installed in the Ignition gateway for this project. They can be downloaded from from the [Inductive Automation website](https://inductiveautomation.com/downloads/third-party-modules) and installed in the Ignition gateway. The `ignition-gateway/weatherpi.gwbk` gateway backup file contains MQTT settings that utilize these modules. After the .gwbk file is used to restore the gateway, an MQTT server will be set up that is ready to accept data from a MQTT client running on a Raspberry Pi Zero.  

The gateway runs a visualization system known as Perspective to display the weather sensor data in a browser window. Sensor data is held in data structures called "tags". Each tag holds a specific sensor value. Tag values can be written to a MariaDB database using the Ignition historian module. This allows past values of each sensor to be retrieved later and displayed on a trend chart.
Ignition designer with sensor tags:
![Ignition designer screenshot](/ignition-gateway/perspective-screenshots/designer.png)

# Pi Zero
The Pi Zero runs a Python script that regularly retrieves weather sensor data from the GPIO pins. The `all-sensors-to-mqtt` script uses the `paho.mqtt.client` Python library to transmit the sensor data to the Ignition gateway running on the Pi 4.

## Sensors
The following sensors are currently connected to the Pi Zero to provide weather data.

### BME280 Atmospheric sensors
The BME280 package provides ambient temperature, humidity, pressure, and air quality sensors. The BME280 communicates over the Pi Zero's I2C bus.

The air quality sensor measures the gas in the ambient air and provides a resistance reading. The lower the reading, the worse air quality is. However, the measured resistance is not in relation to any other known air quality values, so its readings can only be compared to its past readings to give a relative idea of current air quality.

The ambient temperature sensor is not used in this project, as it was found that a temperature probe positioned under an awning gave more accurate temperature readings. The BME280 sensor was placed in an enclosure next to the Raspberry Pi 0's enclosure, and tended to heat up much more than the ambient air on hot days.

### Temperature probe
This is a waterproof probe model DS18B20 connected to the Pi Zero via the GPIO pins. It can be used to measure ground temperature (to monitor for freezing ground temperature for example), or it can be used to measure ambient air temperature. Ambient air temperature measurements are only accurate as long as the probe is maintained in the shade, away from any structures or equipment that might retain heat.

### Wind sensors
There are two devices in use to measure wind: an anemometer to measure wind velocity, and a wind vane to measure the direction that the wind is coming from. I found that the wind vane will sometimes wildly change direction when a wind gust comes along, so measuring the direction of the vane at any instant can give some strange reading. To get around this, the Ignition software records the instant direction once every 5 seconds, then averages the values of the last minute to determine the overall wind direction. This works well to smooth out the direction signal.

The anemometer connects to the Pi Zero via the SPI bus. The wind vane needs a MCP3008 analog to digital converter as the Pi cannot handle analog inputs directly.

### Rain sensor
This sensor uses small buckets to collect rain. Each time the bucket is filled and drops, this triggers a "button" press on the Pi Zero. The Pi can then record the bucket drop event and report it to the Ignition gateway. The rain sensor connects to the Pi Zero via GPIO pins.

# Installation Instructions
Follow the step-by-step instructions in `installation.txt`. The instructions assume that you have both a Raspberry Pi 4 and a Raspberry Pi Zero, and one or more of the sensors detailed above.
