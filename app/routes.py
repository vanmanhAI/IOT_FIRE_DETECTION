from flask import Blueprint, jsonify, request, Response
from app.utils import get_image_stream

main_bp = Blueprint('main', __name__)

@main_bp.route('/hello', methods=['GET'])
def hello():
    return jsonify({"message": "Hello World!"}), 200

@main_bp.route('/stream')
def index():
    return Response(get_image_stream(), mimetype='multipart/x-mixed-replace; boundary=frame')




