from flask import Flask
import asyncio
from threading import Thread
from app.websocket import websocket_server

def create_app():
  app = Flask(__name__)

  # Load configuration (có thể tạo file config riêng)
  app.config['DEBUG'] = True

  # Đăng ký blueprint
  from app.routes import main_bp
  app.register_blueprint(main_bp)

  # Chạy WebSocket server trong một thread riêng
  def run_websocket():
    asyncio.run(websocket_server())

  websocket_thread = Thread(target=run_websocket, daemon=True)
  websocket_thread.start()
    
  return app
