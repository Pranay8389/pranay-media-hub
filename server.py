import os
from flask import Flask, request, jsonify, send_from_directory

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Folder configurations mapped to GitHub paths
FOLDERS = {
    'images': os.path.join(BASE_DIR, 'images'),
    'videos': os.path.join(BASE_DIR, 'videos'),
    'documents': os.path.join(BASE_DIR, 'documents'),
    'music': os.path.join(BASE_DIR, 'music')
}

# Create folders if not present
for folder in FOLDERS.values():
    os.makedirs(folder, exist_ok=True)

@app.route('/')
def home():
    return jsonify({"message": "Server is Running!"}), 200

# File Upload Route
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
        
    filepath = os.path.join(FOLDERS['images'], file.filename)
    file.save(filepath)
    return jsonify({"message": "File uploaded successfully"}), 200

# List Images
@app.route('/images', methods=['GET'])
def get_images():
    if not os.path.exists(FOLDERS['images']):
        return jsonify([])
    files = os.listdir(FOLDERS['images'])
    host = request.host_url.rstrip('/')
    image_urls = [f"{host}/images/{f}" for f in files if f.lower().endswith(('png', 'jpg', 'jpeg', 'webp'))]
    return jsonify(image_urls)

# Serve specific image
@app.route('/images/<filename>', methods=['GET'])
def serve_image(filename):
    return send_from_directory(FOLDERS['images'], filename)

# Routes for videos, documents, music
@app.route('/videos', methods=['GET'])
def get_videos():
    files = os.listdir(FOLDERS['videos']) if os.path.exists(FOLDERS['videos']) else []
    return jsonify(files)

@app.route('/documents', methods=['GET'])
def get_documents():
    files = os.listdir(FOLDERS['documents']) if os.path.exists(FOLDERS['documents']) else []
    return jsonify(files)

@app.route('/music', methods=['GET'])
def get_music():
    files = os.listdir(FOLDERS['music']) if os.path.exists(FOLDERS['music']) else []
    return jsonify(files)

@app.route('/location', methods=['POST'])
def receive_location():
    data = request.json
    print(f"Location: {data}")
    return jsonify({"message": "Location received"}), 200

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
