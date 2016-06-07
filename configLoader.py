import ConfigParser


class ConfigLoader:
    def __init__(self):
        pass

    def config_logger(self, file, size, num):
        """Configure a rotating log"""
        print "Configuring logger: file = " + file + " size = " + str(size) + " num = " + str(num)
        self.logger.setLevel(logging.DEBUG)
        fh = logging.handlers.RotatingFileHandler(file, mode='a', maxBytes=size, backupCount=num)
        fh.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        logger.addHandler(fh)
        logger.info("---------------Started")

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

    def load_config(self, config_file):
        """Read in the config file, set up the logger, and populate the sensors"""
        print "Loading " + config_file

        config = ConfigParser.ConfigParser(allow_no_value=True)
        config.read(config_file)

        config_logger(config.get("Logging", "File"),
                      config.getint("Logging", "MaxSize"),
                      config.getint("Logging", "NumFiles"))

        if restSupport and config.has_section("REST"):
            config_rest(config.get("REST", "URL"))
        if mqttSupport:
            config_mqtt(config)

        self.logger.info("Populating the sensor's list...")
        for section in config.sections():
            if section.startswith("Sensor"):
                sensor_type = config.get(section, "Type")
                report_type = config.get(section, "ReportType")
                if report_type == "REST" and restSupport:
                    type_connection = restConn
                elif report_type == "MQTT" and mqttSupport:
                    type_connection = mqttConn

                if sensor_type == "Bluetooth" and bluetoothSupport:
                    sensors.append(BtSensor(config.get(section, "Address"),
                                            config.get(section, "Destination"),
                                            type_connection.publish, logger,
                                            config.getfloat(section, "Poll")))
                elif sensor_type == "Wifi" and wifiSupport:
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
                if subscribe_type == "REST" and restSupport:
                    msg = "REST based actuators are not yet supported"
                    print msg
                    self.logger.error(msg)
                elif subscribe_type == "MQTT" and mqttSupport:
                    type_connection = mqttConn
                else:
                    msg = "Skipping actuator '%s' due to lack of support in the script for '%s'. Please see preceding error messages." % (
                    config.get(section, "Destination"), subscribe_type)
                    print msg
                    self.logger.warn(msg)
                    continue
        return sensors
