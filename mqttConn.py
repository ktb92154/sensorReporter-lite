"""
 Script: mqttConn.py
 Author: Rich Koshak
 Date:   October 22, 2015
 Purpose: Provides and maintains a connection to the MQTT broker
"""

# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

import sys
import paho.mqtt.client as mqtt

class MQTTConnection(object):
    """Centralizes the MQTT logic"""

    def config(self, logger, user, password, host, prt, ka, lwt_topic, lwt_message, tls):
        """Creates and connects the client"""

        self.logger = logger

        self.client = mqtt.Client()
        if tls == "YES":
            self.client.tls_set("./certs/ca.crt")
        self.client.username_pw_set(user, password)
        self.client.will_set(lwt_topic, lwt_message, 0, False)
        self.client.connect(host, port=prt, keepalive=ka)
        self.client.loop_start()

        self.registered = []

    def publish(self, message, pub_topic):
        """Called by others to publish a message to the publish topic
        :param message:
        :param pub_topic:
        """
        try:
            rval = self.client.publish(pub_topic, message)
            if rval[0] == mqtt.MQTT_ERR_NO_CONN:
                self.logger.error("Error publishing update: " + message +  " to " + pub_topic)
                self.comms.reconnect() # try to reconnect again
            else:
                self.logger.info("Published message " + message + " to " + pub_topic)
        except:
            print "Unexpected error publishing message:", sys.exc_info()[0]
