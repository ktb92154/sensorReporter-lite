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

    def config(self, logger, user, password, host, prt, ka, lwt_topic, lwt_message, topic, message_proc, tls):
        """Creates and connects the client"""

        self.logger = logger
        self.msgProc = message_proc # function that gets called when a message is received
        self.topic = topic

        self.client = mqtt.Client()
        if tls == "YES":
            self.client.tls_set("./certs/ca.crt")
        self.client.on_connect = self.on_connect
        self.client.on_message = self.msgProc
        self.client.on_disconnect = self.on_disconnect
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

    def register(self, sub_topic, message_handler):
        """Registers an actuator to receive messages
        :param sub_topic:
        :param message_handler:
        """
        self.logger.info("Registering for messages on " + sub_topic)
        self.registered.append((sub_topic, message_handler))
        self.client.subscribe(sub_topic)
        self.client.message_callback_add(sub_topic, message_handler)

    def on_connect(self, client, userdata, flags, rc):
        """Called when the MQQT client successfully connects to the broker
        :param client:
        :param userdata:
        :param flags:
        :param rc:
        """

        self.logger.info("Connected with result code "+str(rc)+", subscribing to command topic " + self.topic)
        
        # Subscribing in on_connect() means that if we lose the connection and
        # reconnect then subscriptions will be renewed
        self.client.subscribe(self.topic)

        for r in self.registered:
            self.client.subscribe(r[0])
            # TODO, determine if the callback_add needs to be added here

        self.msgProc(None, None, None)

    def on_disconnect(self, client, userdata, rc):
        """Called when the MQTT client disconnects from the broker
        :param client:
        :param userdata:
        :param rc:
        """

        self.logger.info("Disconnected from the MQTT broker with code " + str(rc))

        if rc != 0:
            self.logger.info("Unexpected disconnect: code = " + str(rc) + " reconnecting")

