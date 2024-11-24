from flask import Blueprint, jsonify, request, Response
from app.utils import get_image_stream

main_bp = Blueprint('main', __name__)

@main_bp.route('/hello', methods=['GET'])
def hello():
    return jsonify({"message": "Hello World!"}), 200

@main_bp.route('/light', methods=['POST'])
def receive_light_data():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data received"}), 400

    light_state = data.get("light_value")
    if light_state is None:
        return jsonify({"error": "Invalid data format"}), 400

    print(f"Light state received: {light_state}")
    return jsonify({"message": "Data received successfully", "light_value": light_state}), 200

@main_bp.route('/')
def index():
    return Response(get_image_stream(), mimetype='multipart/x-mixed-replace; boundary=frame')
