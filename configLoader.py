import ConfigParser
import logging
import logging.handlers

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
        num =  self.config.getint("Logging", "NumFiles")

        print "Configuring logger: file = " + file + " size = " + str(size) + " num = " + str(num)
        logger = logger.setLevel(logging.DEBUG)
        fh = logging.handlers.RotatingFileHandler(file, mode='a', maxBytes=size, backupCount=num)
        fh.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        logger.addHandler(fh)
        logger.info("---------------Started")
        return logger

    def config_mqtt(self, mqtt_config):
        """Configure the MQTT connection"""

        self.logger.info("Configuring the MQTT Broker " + mqtt_config.get("MQTT", "Host"))
        mqttConn.config(logger, mqtt_config.get("MQTT", "User"),
                        mqtt_config.get("MQTT", "Password"), mqtt_config.get("MQTT", "Host"),
                        mqtt_config.getint("MQTT", "Port"),
                        mqtt_config.getfloat("MQTT", "Keepalive"),
                        mqtt_config.get("MQTT", "LWT-Topic"), mqtt_config.get("MQTT", "LWT-Msg"),
                        mqtt_config.get("MQTT", "Topic"), on_message,
                        mqtt_config.get("MQTT", "TLS"))

    def config_rest(self, url):
        """Configure the REST connection"""
        restConn.config(logger, url)
        self.logger.info("REST URL set to: " + url)

    def load_config(self, rest_support, mqtt_support, wifi_support, bluetooth_support):
        """Read in the config file, set up the logger, and populate the sensors"""

        if rest_support and config.has_section("REST"):
            self.config_rest(config.get("REST", "URL"))
        if mqtt_support:
            self.config_mqtt(config)

        self.logger.info("Populating the sensor's list...")
        for section in config.sections():
            if section.startswith("Sensor"):
                sensor_type = config.get(section, "Type")
                report_type = config.get(section, "ReportType")
                if report_type == "REST" and rest_support:
                    type_connection = restConn
                elif report_type == "MQTT" and mqtt_support:
                    type_connection = mqttConn

                if sensor_type == "Bluetooth" and bluetooth_support:
                    sensors.append(BtSensor(config.get(section, "Address"),
                                            config.get(section, "Destination"),
                                            type_connection.publish, logger,
                                            config.getfloat(section, "Poll")))
                elif sensor_type == "Wifi" and wifi_support:
                    sensors.append(WifiSensor(config.get(section, "Address"),
                                              config.get(section, "Destination"),
                                              type_connection.publish, logger,
                                              config.getfloat(section, "Poll")))
                else:
                    msg = "Either '%s' is an unknown sensor type, not supported in this script, or '%s' is not supported in this script.  Please see preceding error messages to be sure." % (
                    sensor_type, report_type)
                    print msg
                    self.logger.error(msg)

            elif section.startswith("Actuator"):
                actuator_type = config.get(section, "Type")
                subscribe_type = config.get(section, "SubscribeType")
                if subscribe_type == "REST" and rest_support:
                    msg = "REST based actuators are not yet supported"
                    print msg
                    self.logger.error(msg)
                elif subscribe_type == "MQTT" and mqtt_support:
                    type_connection = mqttConn
                else:
                    msg = "Skipping actuator '%s' due to lack of support in the script for '%s'. Please see preceding error messages." % (
                    config.get(section, "Destination"), subscribe_type)
                    print msg
                    self.logger.warn(msg)
                    continue
        return sensors
