"""
 Script:  configLoader.py
 Author: Sascha Sambale
 Date:   June 7th, 2016
 Purpose: Loads all configurations (sensors, mqtt & rest connection, logger,...)
        from the given config file (which is being passed as argument)
"""

import ConfigParser
import logging
import logging.handlers

try:
    from restConn import RestConnection

    rest_support = True
except:
    rest_support = False
    print 'REST required files not found. REST not supported in this script.'

try:
    from mqttConn import MQTTConnection

    mqtt_support = True
except:
    mqtt_support = False
    print 'MQTT required files not found. MQTT not supported in this script.'

try:
    from bluetoothScanner import *

    bluetooth_support = True
except ImportError:
    bluetooth_support = False
    print 'Bluetooth is not supported on this machine'

try:
    from wifiScanner import *

    wifi_support = True
except ImportError as test:
    wifi_support = False
    print 'Wifi is not supported on this machine'
    print test

class ConfigLoader:
    def __init__(self, config_file):
        print "Loading " + config_file
        self.config = ConfigParser.ConfigParser(allow_no_value=True)
        self.config.read(config_file)
        pass

    def config_logger(self):
        """Configure a rotating log"""

        logger = logging.getLogger('sensorReporter')

        file = self.config.get("Logging", "File")
        size = self.config.getint("Logging", "MaxSize")
        num = self.config.getint("Logging", "NumFiles")

        print "Configuring logger: file = " + file + " size = " + str(size) + " num = " + str(num)
        logger.setLevel(logging.DEBUG)
        fh = logging.handlers.RotatingFileHandler(file, mode='a', maxBytes=size, backupCount=num)
        log_level = self.config.get("Logging", "LogLevel")
        print "LogLevel retrieved from options: " + log_level

        if log_level.lower().strip() == "debug":
            fh.setLevel(logging.DEBUG)
        else:
            log_level = "info"
            fh.setLevel(logging.INFO)

        print "LogLevel set to " + log_level
        formatter = logging.Formatter('%(asctime)s %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        logger.addHandler(fh)
        logger.info("---------------Started")

        self.logger = logger
        return logger

    def config_mqtt(self):
        """Configure the MQTT connection"""
        self.mqtt_conn = MQTTConnection()
        self.logger.info("Configuring the MQTT Broker " + self.config.get("MQTT", "Host"))
        self.mqtt_conn.config(self.logger, self.config.get("MQTT", "User"),
                              self.config.get("MQTT", "Password"), self.config.get("MQTT", "Host"),
                              self.config.getint("MQTT", "Port"),
                              self.config.getfloat("MQTT", "Keepalive"),
                              self.config.get("MQTT", "LWT-Topic"),
                              self.config.get("MQTT", "LWT-Msg"),
                              self.config.get("MQTT", "TLS"))

    def get_mqtt(self):
        return self.mqtt_conn

    def config_rest(self, url):
        """Configure the REST connection"""
        self.rest_conn = RestConnection()
        self.rest_conn.config(self.logger, url)
        self.logger.info("REST URL set to: " + url)

    def load_config(self, configured_logger):
        """Read in the config file, set up the logger, and populate the sensors"""

        if rest_support and self.config.has_section("REST"):
            self.config_rest(self.config.get("REST", "URL"))
        if mqtt_support:
            self.config_mqtt()

        sensors = []

        configured_logger.debug("Populating the sensor's list...")
        for section in self.config.sections():
            if section.startswith("Sensor"):
                sensor_type = self.config.get(section, "Type")
                report_type = self.config.get(section, "ReportType")
                if report_type == "REST" and rest_support:
                    type_connection = self.rest_conn
                elif report_type == "MQTT" and mqtt_support:
                    type_connection = self.mqtt_conn

                if sensor_type == "Bluetooth" and bluetooth_support:
                    sensors.append(BtSensor(section, self.config,type_connection.publish, configured_logger))
                elif sensor_type == "Wifi" and wifi_support:
                    sensors.append(WifiSensor(section, self.config,type_connection.publish, configured_logger))
                else:
                    msg = "Either '%s' is an unknown sensor type, not supported in this script, or '%s' is not supported in this script.  Please see preceding error messages to be sure." % (
                        sensor_type, report_type)
                    print msg
                    configured_logger.error(msg)
        return sensors

