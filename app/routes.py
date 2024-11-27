from flask import Blueprint, jsonify, request, Response
from app.utils import get_image_stream

main_bp = Blueprint('main', __name__)

@main_bp.route('/hello', methods=['GET'])
def hello():
    return jsonify({"message": "Hello World!"}), 200

@main_bp.route('/stream')
def index():
    return Response(get_image_stream(), mimetype='multipart/x-mixed-replace; boundary=frame')

@main_bp.route('/fire-alert', methods=['GET'])
def fire_alert():
    try:
        # Lấy dữ liệu từ MQTT gửi tới
        data = request.get_json()
        print(data['lua1'], data['lua2'], data['lua3'], data['khoi'])
        print("-------------------")
        return jsonify({
            "message": "Received data successfully",
            "lua1": data['lua1'],
            "lua2": data['lua2'],
            "lua3": data['lua3'],
            "khoi": data['khoi']
        }), 200
    except Exception as e:
        print(f"Error processing fire-alert: {e}")
        return jsonify({"error": "Internal server error"}), 500



