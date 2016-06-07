#!/bin/sh

# Assumptions
# This script is started from within the config directory
# The platfrom you're running it on supports systemd

echo "Creating soft link in /opt"
cd ..
sudo ln -s `pwd` /opt/sensorReporter
chmod a+x /opt/sensorReporter/sensorReporter.py

echo "Setting config"
ln -s $HOSTNAME.ini /opt/sensorReporter/sensorReporter.ini

echo "Installing start script"

# systemd
sudo cp ./config/sensorReporter.service /etc/systemd/system
sudo systemctl enable sensorReporter.service
