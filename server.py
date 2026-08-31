import os
from flask import Flask, request, jsonify, send_from_directory

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGES_FOLDER = os.path.join(BASE_DIR, 'images')
os.makedirs(IMAGES_FOLDER, exist_ok=True)

@app.route('/')
def home():
    return jsonify({"message": "Server active"}), 200

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "Empty filename"}), 400
    filepath = os.path.join(IMAGES_FOLDER, file.filename)
    file.save(filepath)
    return jsonify({"message": "Uploaded successfully"}), 200

@app.route('/images', methods=['GET'])
def get_images():
    files = os.listdir(IMAGES_FOLDER) if os.path.exists(IMAGES_FOLDER) else []
    # Direct image serving path matching Flask route
    image_urls = [f"/static_img/{f}" for f in files if f.lower().endswith(('png', 'jpg', 'jpeg', 'webp'))]
    return jsonify(image_urls)

@app.route('/static_img/<filename>')
def serve_image(filename):
    return send_from_directory(IMAGES_FOLDER, filename)

@app.route('/location', methods=['POST'])
def location():
    return jsonify({"message": "Location received"}), 200

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
