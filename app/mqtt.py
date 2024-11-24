import asyncio
import paho.mqtt.client as mqtt
from websocket import send_message

# Kênh MQTT
PUMP_TOPIC = "dieukhienbom"         # Điều khiển bơm
LIGHT_TOPIC = "cambien/anhsang"     # Dữ liệu cảm biến ánh sáng
FIRE_TOPIC = "cambien/lua"          # Dữ liệu cảm biến lửa
SMOKE_TOPIC = "cambien/khoi"        # Dữ liệu cảm biến khói

def init_mqtt_client():
  client = mqtt.Client()
  client.username_pw_set("Quan532003", "Quan532003@")
  client.tls_set()

  def on_connect(client, userdata, flags, rc):
    if rc == 0:
      print("Connected to MQTT Broker!")
      client.subscribe(LIGHT_TOPIC)
      client.subscribe(FIRE_TOPIC)
      client.subscribe(SMOKE_TOPIC)
    else:
      print(f"Failed to connect, return code {rc}")

  def on_message(client, userdata, msg):
    print(f"Message from { msg.topic }: { msg.payload.decode('utf-8') }")
    asyncio.run_coroutine_threadsafe(send_message(message), loop)

  client.on_connect = on_connect
  client.on_message = on_message
  return client
