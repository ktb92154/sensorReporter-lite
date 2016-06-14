"""
 Script:      bluetoothScanner.py
 Author:      Rich Koshak / Lenny Shirley <http://www.lennysh.com> / Sascha Sambale
 Date:        June 7th, 2016
 Purpose:     Scans for a Bluetooth device with a given address and publishes whether or not the device is present using RSSI figures, or lookup function.
Credit From:  https://github.com/blakeman399/Bluetooth-Proximity-Light/blob/master/https/github.com/blakeman399/Bluetooth-Proximity-Light.py
"""

import array
import bluetooth
import bluetooth._bluetooth as bt
import fcntl
import struct

debug = 0

"""Either use 'RSSI' mode, or 'LOOKUP' mode.  RSSI is more reliable."""
mode = "RSSI"
# mode = "LOOKUP"

class BtSensor:
    """Represents a Bluetooth device"""

    def __init__(self, config, publish, logger):
        """Finds whether the BT device is close and publishes its current state"""
        self.logger = logger
        self.name = config.get(section, "Name")
        self.address = config.get(section, "Address")
        self.destination = config.get(section, "Destination")
        self.publish = publish
        self.poll = config.getfloat(section, "Poll")

        self.logger.info(
                "----------Configuring BluetoothSensor: Name = %s Address = %s Destination = %s", self.name,
                self.address, self.destination)

        # assume phone is initially far away
        # self.far = True
        self.far_count = 0
        self.near_count = 0
        self.rssi = None

        self.publish_state()

    def get_presence(self):
        """Detects whether the device is near by or not using lookup_name"""
        result = bluetooth.lookup_name(self.address, timeout=25)
        if result is not None:
            return "ON"
        else:
            return "OFF"

    def get_rssi(self):
        """Detects whether the device is near by or not using RSSI"""
        addr = self.address

        # Open hci socket
        hci_sock = bt.hci_open_dev()
        hci_fd = hci_sock.fileno()

        # Connect to device (to whatever you like)
        bt_sock = bluetooth.BluetoothSocket(bluetooth.L2CAP)
        bt_sock.settimeout(10)
        bt_sock.connect_ex((addr, 1))  # PSM 1 - Service Discovery

        try:
            # Get ConnInfo
            reqstr = struct.pack("6sB17s", bt.str2ba(addr), bt.ACL_LINK, "\0" * 17)
            request = array.array("c", reqstr)
            fcntl.ioctl(hci_fd, bt.HCIGETCONNINFO, request, 1)
            handle = struct.unpack("8xH14x", request.tostring())[0]

            # Get RSSI
            cmd_pkt = struct.pack('H', handle)
            rssi = bt.hci_send_req(hci_sock, bt.OGF_STATUS_PARAM,
                                   bt.OCF_READ_RSSI, bt.EVT_CMD_COMPLETE, 4, cmd_pkt)
            rssi = struct.unpack('b', rssi[3])[0]

            # Close sockets
            bt_sock.close()
            hci_sock.close()

            return rssi

        except Exception, e:
            # self.logger.error("<Bluetooth> (getRSSI) %s" % (repr(e)))
            return None

    def check_state(self):
        """Detects and publishes any state change"""

        if mode == "RSSI":
            value = self.state
            self.rssi = self.get_rssi()
            if self.rssi is None:
                if self.far_count < 3:
                    self.logger.info("Signal lost - will wait just to be sure.")
                self.far_count += 1
                self.near_count -= 1
                if self.near_count < 0:
                    self.near_count = 0
                if self.far_count > 15:
                    self.far_count = 15
            elif self.rssi > 1:
                if self.near_count < 10:
                    self.logger.info(
                            "Got signal from " + self.name + ", waiting for stronger one: " + str(
                                    self.near_count * 10) + "%.")
                self.far_count -= 1
                self.near_count += 1
                if self.far_count < 0:
                    self.far_count = 0
                if self.near_count > 10:
                    self.near_count = 10
            if self.near_count > self.far_count and self.near_count >= 10:
                value = "ON"
            elif self.far_count > self.near_count and self.far_count > 3:
                value = "OFF"
            else:
                value = self.state
            self.logger.debug(
                    "Name "+self.name+" Destination " + self.destination + " far count = " + str(
                            self.far_count) + " near count = " + str(
                            self.near_count) + " RSSI = " + str(self.rssi))

        elif mode == "LOOKUP":
            value = self.get_presence()

        else:
            msg = "Invalid 'mode' specified in 'bluetoothScanner.py' !"
            print msg
            self.logger.error(msg)
            return

        if value != self.state:
            self.state = value
            self.publish_state()

    def publish_state(self):
        """Publishes the current state"""

        self.publish(self.state, self.destination)
