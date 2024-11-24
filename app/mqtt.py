import paho.mqtt.client as mqtt
import json
import requests

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
    if msg.topic == FIRE_TOPIC:
      fire_value = msg.payload.decode('utf-8')
      url = "http://localhost:5000/fire-alert"
      headers = {"Content-Type": "application/json"}
      if fire_value == "0":
        print("Fire detected! Sending alert...")
        # Gửi request đến Flask server
        data = {"fire_detected": True}
        try:
          response = requests.post(url, json=data, headers=headers)
          print(f"Response: { response.status_code }, { response.text }")
        except Exception as e:
          print(f"Error while sending request: {e}")
      else:
        response = requests.post(url, json={"fire_detected": False}, headers=headers)


  client.on_connect = on_connect
  client.on_message = on_message
  return client
