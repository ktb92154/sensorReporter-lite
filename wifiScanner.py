"""
 Script: wifiScanner.py
 Author: Sascha Sambale
 Date:   June 7th, 2016
 Purpose: Scans for a Wifi device with a given address and publishes whether or not the device is present in the network.

  Based on code provided by Benedikt Waldvogel's Layer 2 network neighbourhood discovery tool.
"""

from __future__ import absolute_import, division, print_function

import math
import scapy.config
import scapy.layers.l2
import scapy.route
import socket

debug = 0

class WifiSensor:
    """Represents a Bluetooth device"""

    def __init__(self, section, config, publish, logger):
        """Finds whether the BT device is close and publishes its current state"""

        self.logger = logger
        self.name = config.get(section, "Name")
        self.address = config.get(section, "Address")
        self.destination = config.get(section, "Destination")
        self.publish = publish
        self.poll = config.getfloat(section, "Poll")
        self.tries_until_offline = config.getfloat(section, "OfflineTrigger")

        self.logger.info(
                "----------Configuring WifiSensor: Name = %s Address = %s Destination = %s", self.name,
                self.address, self.destination)

        self.state = "OFF"

        # We'll try at least 5 times until we report an "OFF" state (to overcome smartphone sleep policies).
        self.off_count = 0

        self.publish_state()

    @staticmethod
    def long2net(arg):
        if arg <= 0 or arg >= 0xFFFFFFFF:
            raise ValueError("Illegal netmask value", hex(arg))
        return 32 - int(round(math.log(0xFFFFFFFF - arg, 2)))

    def to_cidr_notation(self, bytes_network, bytes_netmask):
        network = scapy.utils.ltoa(bytes_network)
        netmask = self.long2net(bytes_netmask)
        net = "%s/%s" % (network, netmask)
        if netmask < 16:
            self.logger.warn("%s is too big. skipping" % net)
            return None
        return net

    def get_network_presence(self, net, interface, timeout=1):
        value = "OFF"
        self.logger.debug("Ready to check network presence!")
        try:
            ans, unans = scapy.layers.l2.arping(net, iface=interface, timeout=timeout, verbose=True)
            for s, r in ans.res:
                mac = r.sprintf("%Ether.src%")
                if mac.lower() == self.address.lower():
                    self.logger.info("%s (%s) has been found in the network!", self.name,
                                     self.address)
                    value = "ON"
                    self.off_count = 0
                    break
            if value is "OFF":
                self.logger.debug("%s (%s) has not been found in the network!", self.name,
                                  self.address)
                self.off_count += 1
                if self.off_count <= self.tries_until_offline:
                    value = "ON"
                    self.logger.debug("%s of %s tries. Will not report OFF yet.", self.off_count,
                                      self.tries_until_offline)

        except socket.error as e:
            if e.errno == errno.EPERM:  # Operation not permitted
                self.logger.error("%s. Did you run as root?", e.strerror)
            else:
                raise
        return value

    def check_network(self):
        value = self.state
        for network, netmask, _, interface, address in scapy.config.conf.route.routes:
            """ Skip loopback network and default gw """
            if network == 0 or interface == 'lo' or address == '127.0.0.1' or address == '0.0.0.0':
                continue

            if netmask <= 0 or netmask == 0xFFFFFFFF:
                continue

            net = self.to_cidr_notation(network, netmask)

            if interface != scapy.config.conf.iface:
                # see http://trac.secdev.org/scapy/ticket/537
                self.logger.warn(
                        "skipping %s because scapy currently doesn't support arping on non-primary network interfaces",
                        net)
                continue

            if net:
                value = self.get_network_presence(net, interface)
                if value != self.state:
                    self.state = value
                    self.publish_state()
                    break

    def get_presence(self):
        """Detects whether the device is in the network"""
        self.check_network()

    def check_state(self):
        """Detects and publishes any state change"""
        self.logger.debug("Checking Wifi state for %s/%s", self.address, self.destination)
        self.get_presence()

    def publish_state(self):
        """Publishes the current state"""
        self.publish(self.state, self.destination)
