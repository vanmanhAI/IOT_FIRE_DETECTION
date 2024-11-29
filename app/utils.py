from PIL import Image
from io import BytesIO
import json
from ultralytics import YOLO
import websockets
import time
import cv2 as cv
from app.websocket import broadcast

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
      imageRGB = cv.cvtColor(img, cv.COLOR_BGR2RGB)
      image = Image.fromarray(imageRGB)

      img_io = BytesIO()
      image.save(img_io, 'JPEG')
      img_io.seek(0)
      yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + img_io.read() + b'\r\n')
    except Exception as e:
      print("Error reading image:", e)
      yield b''

def get_image_stream(mqtt_client):
  fire_detected_start_time = None
  while True:
    try:
      with open("image.jpg", "rb") as f:
        image_bytes = f.read()
      image = Image.open(BytesIO(image_bytes))

      results = model.predict(image, show=False, imgsz=240)
      result = results[0]

      if result.boxes is None or len(result.boxes) == 0:
        print("No objects detected.")
        fire_detected_start_time = None
      else:
        # Phát hiện lửa
        if fire_detected_start_time is None:
          fire_detected_start_time = time.time()
          print("Fire detected, starting timer...")
        else:
          # Tính thời gian đã phát hiện lửa
          elapsed_time = time.time() - fire_detected_start_time
          print(f"Fire detected for {elapsed_time:.2f} seconds")
          if elapsed_time >= 5:
            xywh = result.boxes.xywh[0].tolist()
            x_center = xywh[0] / result.orig_shape[1]
            y_center = xywh[1] / result.orig_shape[0]

            print(f"Fire detected at ({x_center:.2f}, {y_center:.2f})")

            data = TinhToan(x_center, y_center)

            if mqtt_client.is_connected():
              print("Sending data to MQTT...")
              mqtt_client.publish("dieukhienbom", json.dumps(data))
              # Reset thời gian sau khi gửi
              fire_detected_start_time = None
            else:
              print("MQTT client not connected.")

    except Exception as e:
      print("Error reading image:", e)

async def websocket_broadcast(data):
    message = json.dumps(data)
    await broadcast(message)

def TinhToan(x: float, y: float):
  goc1 = 45 + x * 35.0
  tmp = 40 + y * 50.0
  goc2From = tmp - 20
  goc2To = tmp + 20
  return  {
    "goc1": int(goc1),
    "goc2From": int(goc2From),
    "goc2To": int(goc2To)
  }

  # gui len mqtt voi topic la dieukhienbom {"goc1": goc1, "goc2From": 90, "goc2To": 90}
