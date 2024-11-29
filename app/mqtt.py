import paho.mqtt.client as mqtt
import json
import asyncio
from app.database import save_notification, save_status 

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
      lua1 = data.get('lua1', 0)
      lua2 = data.get('lua2', 0)
      lua3 = data.get('lua3', 0)
      khoi = data.get('khoi', 0)
      
      
      smoke = khoi  # Giả sử 'khoi' là giá trị khói
      fire = lua1 + lua2 + lua3
      light = 100  # Giá trị giả định, thay đổi theo nhu cầu

      # Xác định trạng thái và phần trăm
      status, percentage = determine_fire_status(lua1, lua2, lua3, smoke)

      # Lưu dữ liệu vào database
      save_notification(smoke, fire, light, "image.jpg")
      save_status(status, percentage)

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

def determine_fire_status(lua1, lua2, lua3, smoke):
    fire_count = sum([lua1, lua2, lua3])
    
    if fire_count == 0:
        if smoke < 400:
            return "an toàn", 0
        else:
            return "nguy cơ", 50
    elif fire_count == 1:
        return "nguy hiểm", 70
    elif fire_count >= 2:
        return "cực kỳ nguy hiểm", 100
    else:
        return "unknown", 0