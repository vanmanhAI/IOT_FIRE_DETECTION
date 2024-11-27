# mqtt.py
import paho.mqtt.client as mqtt
import json

# MQTT topics
PUMP_TOPIC = "dieukhienbom"         
GENERAL_TOPIC = "cambien/duLieu"  

def init_mqtt_client():
    """Initialize MQTT client and configure events."""
    client = mqtt.Client()
    client.username_pw_set("Quan532003", "Quan532003@")
    client.tls_set()

    def on_connect(client, userdata, flags, rc):
        """Handle connection to the MQTT broker."""
        if rc == 0:
            print("Connected to MQTT Broker!")
            client.subscribe(GENERAL_TOPIC)  # Subscribe to topic
        else:
            print(f"Failed to connect, return code {rc}")


    client.on_connect = on_connect

    return client