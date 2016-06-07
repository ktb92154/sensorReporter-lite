# Introduction
If you need a script to detect whether someone is at home or not, this might be your solution.

# What does this script do?
This script detects wheter certain Bluetooth or WIFI MAC addresses are either nearby (Bluetooth) or in your home network (Wifi) and then sends a message either to an MQTT queue or a REST interface.

# What can I use this script for?
I'm using this script to detect whether I or my wife are at home (we're always taking our smartphones with us). If we're both not at home, I will trigger certain events at home, since my [OpenHAB](http://www.openhab.org/) installation is attached to the same MQTT queue like this script (which runs on a Raspberry Pi 3).

# Dependencies
This script depends on the [paho library for MQTT](https://pypi.python.org/pypi/paho-mqtt/1.2) and [python-bluez](http://karulis.github.io/pybluez/) for Bluetooth support (and of course you system must be able to use Bluetooth). You'll also need a working scapy setup for the Wifi support.

# Installation
The install.sh in the config folder lists all the commands necessary  to install dependencies, link the current folder to /opt and set it up to start  as a service. It has the scripts and commands for both upstart and systemd.

# Support
I won't be able to give you premium support here. So you should be able to understand the code when something unexpected happens. I also won't take any responsibility if something messes up your system.

# Configuration
The configuration file (you should call it sensorReporter.ini) contains one or more Sensor sections which specify their Type, the MQTT/REST destination to report or subscribe to, reporting type (MQTT or REST), sensor and actuator specific info (e.g. Wifi MAC, BT address, etc.). You can see an example in the default.ini file.

The Logging section allows one to specify where the scripts log file is saved, its max size, and maximum number of old log files to save.

The REST section is where one specifies the first portion of the URL for the REST API.

The MQTT section is where one specifies the user, password, host, and port, for the MQTT Broker. The Topic item in this section is a topic the script listens to.
One also defines a Last Will and Testament topic and message so other servers can monitor whether this script is running. Finally there is an option for turning on TLS in the connection to the MQTT Broker. It will look for the certificates in ./certs/ca.cert.

# Usage
This script must always be run as root - at least when using Wifi for presence detection.

To run the script manually:

`sudo python sensorReporter sensorReporter.ini`

If it has been installed, run:

`sudo systemctl start sensorReporter`

# Addition information
If you want to scan your network/are for certain devices or you want to see whether everything works as expected, you can use the helper scrips in the config directory.

## Scan your area for Bluetooth devices (devices must be in discovery mode)

Output:
```
your@raspberry:~/sensorReporter-lite/config $ sudo python inquiry_bt.py
performing inquiry...
found 1 devices
00:1E:3B:38:16:5D - Peter 25
```

## Scan your network for Wifi devices

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
  07:08:54 INFO  b7:27:e5:af:de:68  192.168.1.111 mySecondMachineInTheNetwork
[...]
```

# Remarks

Originally this script has been forked from [rkoshak/sensorReporter](https://github.com/rkoshak/sensorReporter), but I've removed everything but the Bluetooth, MQTT and REST support and added WIFI support (with help from code of Benedikt Waldvogel's Layer 2 network neighbourhood discovery tool).