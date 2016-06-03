# Introduction
This script has been forked from [rkoshak/sensorReporter](https://github.com/rkoshak/sensorReporter). I've removed everything but the Bluetooth, MQTT and REST support.

# What can I use this script for?
I'm using this script to detect whether someone is at home (based on the persons Bluetooth device). Since this script reports to MQTT, I can use my OpenHAB installation to get the information and run some rules.
# SensorReporter
A python script that polls a sensor and publishes changes in its state to MQTT and/or REST as well as reacting to commands sent to it. This lite version only supports Bluetooth device scanning. If you need Dash or GPIO, please see the original repo!

# Dependencies
This script depends on the paho library for MQTT and python-bluez for Bluetooth support. The install.sh in the config folder lists all the commands necessary  to install dependencies, link the current folder to /opt and set it up to start  as a service. It has the scripts and commands for both upstart and systemd.

# Organization
The config folder contains an install.sh as described above, sensorReporter start 
script for upstart systems (e.g raspbian wheezy), and a service file for systemd 
type systems (e.g raspbian jessie, Ubuntu 15+). The install script will install 
dependencies using using apt-get and pip and copy and enable the start script to 
init.d or /systemd/system and enalbe it so sensorReporter will start as a service 
during boot. You must edit the script to match your system.

The main folder has a default.ini with configuration parametersi examples  and the 
Python script itself.

The install.sh expects there to be a .ini file that matches your hostname. It 
will create a symbolic link to sensorReporter.ini which the service start 
scripts expect.

If you place or link the script somewhere other than /opt/sensorReporter you need 
to update the sensorReporter start script or sensorReporter.service with the correct 
path.

# Configuration
The configuration file contains one or more Sensor sections which specify thier 
Type, the MQTT/REST destination to report or subscribe to, reporting type (MQTT 
or REST), sensor and actuator specific info (e.g. pin, BT address, etc.).

The Logging section allows one to specify where the scripts log file is saved, 
its max size, and maximum number of old log files to save.

The REST section is where one specifies the biggining portion of the URL for the
REST API.

The MQTT section is where one specifies the user, password, host, and port, for 
the MQTT Broker. The Topic item in this section is a topic the script listens to 
report the state of the pins on command. One also defines a Last Will and 
Testament topic and message so other servers can monitor whether this script is 
running. Finally there is an option for turning on TLS in the connection to the
MQTT Broker. It will look for the certificates in ./certs/ca.cert.

# Usage
To run the script manually:

sudo python sensorReporter sensorReporter.ini

If it has been installed, run:

sudo service sensorReporter start

or

sudo systemctl start sensorReporter

# Behavior
Certain sensors require polling. The Bluetooth sensor will
poll for the current state one per configured poll period. If the state of the 
sensor has changed the new state is published to the configured MQTT/REST 
destination.

Upon receipt of any message on the incoming destination configured in the MQTT 
section, the script will publish the current state of all configured polling 
sensors (sensors with a polling period &gt; 0) on their respective destinations 
immediately.

The script is configured to respond properly to term signals (e.g. &lt;ctrl&gt;-c) so 
it behaves nicely when run as a service (currently broken when using Dash).

# Bluetooth Specifics
To discover the address of your Bluetooth device (e.g. a phone), put it in 
pairing mode, run inquiry.py and record the address next to the name of your 
device. Use this address in the .ini file for your Bluetooth scanning sensors.

inquiry.py is part of the pybluez project and can be found at 
https://code.google.com/p/pybluez/source/browse/examples/simple/inquiry.py

When a configured device is detected it will report "ON" to the destination. 
"OFF" is reported when the device is no longer detected.

NOTE: Work is in progress to make the HIGH/LOW behavior more flexible to 
support a wider range of applications.