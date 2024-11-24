from flask import Flask

def create_app():
  app = Flask(__name__)

  # Load configuration (có thể tạo file config riêng)
  app.config['DEBUG'] = True

  # Đăng ký blueprint
  from app.routes import main_bp
  app.register_blueprint(main_bp)

  return app
