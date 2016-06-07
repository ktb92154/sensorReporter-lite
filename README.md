# Introduction
If you need a script to detect whether someone is at home or not, this might be your solution.

# What does this script do?
This script detects whether certain Bluetooth or WIFI MAC addresses are either nearby (Bluetooth) or in your home network (Wifi) and then sends a message either to an MQTT queue or a REST interface.

# What can I use this script for?
I'm using this script to detect whether I or my wife are at home (we're always taking our smartphones with us). If we're both not at home, I will trigger certain events at home, since my [OpenHAB](http://www.openhab.org/) installation is attached to the same MQTT queue like this script (which runs on a Raspberry Pi 3).

# Dependencies
This script depends on the [paho library for MQTT](https://pypi.python.org/pypi/paho-mqtt/1.2) and [python-bluez](http://karulis.github.io/pybluez/) for Bluetooth support (and of course you system must be able to use Bluetooth). You'll also need a working scapy setup for the Wifi support.

# Installation
The install.sh in the config folder lists all the commands necessary  to install dependencies, link the current folder to /opt and set it up to start  as a service. It has the scripts and commands for both upstart and systemd.

# Support
I won't be able to give you premium support here. So you should be able to understand the code when something unexpected happens. I also won't take any responsibility if something messes up your system.

# Configuration
The configuration file (you should call it sensorReporter.ini) contains one or more Sensor sections which specify their Type, the MQTT/REST destination to report or subscribe to, reporting type (MQTT or REST), sensor and actuator specific info (e.g. Wifi MAC, BT address, etc.). You can see an example in the sensorReporter_demo.ini file.

Example:

```
[Sensor1]
Name: MyBluetoothDevice
Type: Bluetooth
Address: F6:F7:B8:39:4A:FB
Destination: presence/bluetooth1
ReportType: MQTT
; Needs to be greater than 1 if using the RSSI method, 25 if using the other method.
Poll: 2

[Sensor2]
Name: MyWifiDevice
Type: Wifi
Address: F7:F8:B9:3A:4B:FC
Destination: presence/wifi1
ReportType: MQTT
; Should be greater than 30, since we don't want to stress the network so much.
Poll: 60
```

The Logging section allows one to specify where the scripts log file is saved, its max size, and maximum number of old log files to save.

Example:
```
[Logging]
File: mqttReporter.log
MaxSize: 67108864
NumFiles: 10
```

The REST section is where one specifies the first portion of the URL for the REST API.

Example:
```
[REST]
URL = http://localhost:8080/rest/items/
```

The MQTT section is where one specifies the user, password, host, and port, for the MQTT Broker. The Topic item in this section is a topic the script listens to.
One also defines a Last Will and Testament topic and message so other servers can monitor whether this script is running. Finally there is an option for turning on TLS in the connection to the MQTT Broker. It will look for the certificates in ./certs/ca.cert.

Example:
```
[MQTT]
User = user
Password = password
Host = host
Port = 1883
TLS = no
Keepalive = 60
; The MQTT broker will publish the following message on the following topic 
; when the client disconnects (cleanly or crashes)
LWT-Topic = status/reporters
LWT-Msg = My SensorReporter is dead
```

A full example can be seen in the sensorReporter_demo.ini file of the project.

# Usage
This script must always be run as root - at least when using Wifi for presence detection.

To run the script manually:

`sudo python sensorReporter sensorReporter.ini`

If it has been installed, run:

`sudo systemctl start sensorReporter`

# Addition information
If you want to scan your network/are for certain devices or you want to see whether everything works as expected, you can use the helper scrips in the config directory.

## Manually scan your area for Bluetooth devices (devices must be in discovery mode)

Output:
```
your@raspberry:~/sensorReporter-lite/config $ sudo python inquiry_bt.py
performing inquiry...
found 2 devices
00:1E:3B:38:16:5D - MyBluetoothDeviceInDiscoveryMode
A0:2F:1C:11:67:7F - MyOtherBluetoothDeviceInDiscoveryMode
```

## Manually scan your network for Wifi devices

Output:
```
your@raspberry:~/sensorReporter-lite/config $ sudo python inquiry_wifi.py
Begin emission:
Finished to send 256 packets.

Received 9 packets, got 9 answers, remaining 247 packets
  06:11:35:aa:dc:34 192.168.1.110
  b7:27:e5:af:de:68 192.168.1.111
[...]
  06:11:35:aa:dc:34  192.168.1.110 myFirstMachineInTheNetwork
  b7:27:e5:af:de:68  192.168.1.111 mySecondMachineInTheNetwork
[...]
```

# Remarks

Originally this script has been forked from [rkoshak/sensorReporter](https://github.com/rkoshak/sensorReporter). 

## Changes to original fork:

* Added Wifi support (with help from code of Benedikt Waldvogel's Layer 2 network neighbourhood discovery tool)
* Added Name field to sensor config
* Added TLS field to MQTT config
* Removed GPIO support
* Removed MQTT listener
* Removed unnecessary files
* Moved config loader to separate module
* Code clean up

In short: This project has changed a lot. :)