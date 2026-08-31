import os
from flask import Flask, request, jsonify, send_from_directory

app = Flask(__name__)

# Folders Setup
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'images')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
        
    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)
    return jsonify({"message": "File uploaded successfully"}), 200

@app.route('/images', methods=['GET'])
def get_images():
    files = os.listdir(UPLOAD_FOLDER)
    host = request.host_url.rstrip('/')
    image_urls = [f"{host}/static/images/{f}" for f in files if f.lower().endswith(('png', 'jpg', 'jpeg', 'webp'))]
    return jsonify(image_urls)

@app.route('/static/images/<filename>')
def serve_image(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

@app.route('/location', methods=['POST'])
def receive_location():
    data = request.json
    print(f"Received Location: Latitude = {data.get('latitude')}, Longitude = {data.get('longitude')}")
    return jsonify({"message": "Location received successfully"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
