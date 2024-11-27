from PIL import Image
from io import BytesIO
import json
import websockets

def get_image_stream():
  while True:
    try:
      with open("image.jpg", "rb") as f:
          image_bytes = f.read()
      image = Image.open(BytesIO(image_bytes))
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

