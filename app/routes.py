from flask import Blueprint, jsonify, request, Response
from app.utils import get_image_stream

main_bp = Blueprint('main', __name__)

@main_bp.route('/hello', methods=['GET'])
def hello():
    return jsonify({"message": "Hello World!"}), 200

@main_bp.route('/stream')
def index():
    return Response(get_image_stream(), mimetype='multipart/x-mixed-replace; boundary=frame')

@main_bp.route('/fire-alert', methods=['POST'])
def fire_alert():
    try:
        # Lấy dữ liệu JSON từ request
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        fire_detected = data.get("fire_detected")
        if fire_detected is None:
            return jsonify({"error": "Invalid data format"}), 400

        if fire_detected:
            print("Cảnh báo: Cháy được phát hiện!")
            # Xử lý logic khi phát hiện cháy (gửi thông báo, kích hoạt hệ thống, v.v.)
        else:
            print("Không phát hiện cháy.")
            # Xử lý logic khi không có cháy (cập nhật trạng thái, v.v.)

        return jsonify({"message": "Fire alert processed successfully", "fire_detected": fire_detected}), 200
    except Exception as e:
        print(f"Error in fire_alert: {e}")
        return jsonify({"error": "Internal server error"}), 500

