import paho.mqtt.client as mqtt
import json
import asyncio
from app.utils import websocket_broadcast

PUMP_TOPIC = "dieukhienbom"
GENERAL_TOPIC = "cambien/duLieu"


def init_mqtt_client():
  client = mqtt.Client()
  client.username_pw_set("Quan532003", "Quan532003@")
  client.tls_set()

  def on_connect(client, userdata, flags, rc):
    if rc == 0:
      print("Connected to MQTT Broker!")
      client.subscribe(GENERAL_TOPIC)
    else:
      print(f"Failed to connect, return code {rc}")

  def on_message(client, userdata, msg):
    try:
      data = json.loads(msg.payload.decode('utf-8'))

      print("--------------------------------------------------------------------\n\n")
      print(f"Received: {data['lua1']} {data['lua2']} {data['lua3']} {data['khoi']}\n\n")
      print("--------------------------------------------------------------------")


            
      # Gửi dữ liệu đến WebSocket
      # asyncio.run(websocket_broadcast(data))
      asyncio.create_task(websocket_broadcast(data))
    except Exception as e:
      print(f"MQTT message processing error: {e}")

  client.on_connect = on_connect
  client.on_message = on_message
  return client
