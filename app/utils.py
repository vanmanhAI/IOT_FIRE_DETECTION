from PIL import Image
from io import BytesIO
import json
from ultralytics import YOLO
import websockets
import math
# Load a model
model = YOLO("app/model/best.pt")

def get_image_stream_client():
  while True:
    try:
      with open("image.jpg", "rb") as f:
        image_bytes = f.read()
      image = Image.open(BytesIO(image_bytes))

      results = model.predict(image, show=False, imgsz=240)
      result = results[0]

      img = result.plot()
      image = Image.fromarray(img)

      img_io = BytesIO()
      image.save(img_io, 'JPEG')
      img_io.seek(0)
      yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + img_io.read() + b'\r\n')
    except Exception as e:
      print("Error reading image:", e)
      yield b''

def get_image_stream(mqtt_client):
  while True:
    try:
      with open("image.jpg", "rb") as f:
        image_bytes = f.read()
      image = Image.open(BytesIO(image_bytes))

      results = model.predict(image, show=False, imgsz=240)
      result = results[0]

      if result.boxes is None or len(result.boxes) == 0:
        print("No objects detected.")
      else:
        xywh = result.boxes.xywh[0].tolist()
        conf = result.boxes.conf[0].item()

        original_shape = result.orig_shape

        x_center = xywh[0] / original_shape[1]
        y_center = xywh[1] / original_shape[0]
        width = xywh[2] / original_shape[1]
        height = xywh[3] / original_shape[0]

        data = TinhToan(x_center, y_center)

        # Gửi lên MQTT, kiểm tra kết nối trước khi gửi
        if mqtt_client.is_connected():
          mqtt_client.publish("fire_detect", json.dumps(data))
        else:
          print("MQTT client not connected.")

      img = result.plot()
      image = Image.fromarray(img)

      img_io = BytesIO()
      image.save(img_io, 'JPEG')
      img_io.seek(0)
      yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + img_io.read() + b'\r\n')
    except Exception as e:
      print("Error reading image:", e)
      yield b''

async def websocket_broadcast(data):
  """Gửi dữ liệu tới WebSocket."""
  try:
    async with websockets.connect('ws://localhost:3001') as websocket:
      await websocket.send(json.dumps(data))
      print("Data broadcasted to WebSocket clients.")
  except Exception as e:
    print(f"Failed to broadcast WebSocket message: {e}")

def TinhToan(x: float, y: float):
  alpha_radian = math.atan(abs(0.5 - x) * 23 / 30)
  alpha_degree = math.degrees(alpha_radian)
  goc1 = 90 + (alpha_degree if x > 0.5 else -alpha_degree)
  goc2 = 90
  return  {
    "goc1": goc1,
    "goc2From": 90,
    "goc2To": 90
  }

  # gui len mqtt voi topic la dieukhienbom {"goc1": goc1, "goc2From": 90, "goc2To": 90}
