import os
from flask import Flask, request, jsonify, send_from_directory

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# GitHub Folder Mapping
FOLDERS = {
    'images': os.path.join(BASE_DIR, 'images'),
    'videos': os.path.join(BASE_DIR, 'videos'),
    'mp3': os.path.join(BASE_DIR, 'mp3'),
    'documents': os.path.join(BASE_DIR, 'documents')
}

# Ensure folders exist
for folder in FOLDERS.values():
    os.makedirs(folder, exist_ok=True)

def scan_files(folder_key, extensions):
    path = FOLDERS[folder_key]
    if not os.path.exists(path):
        return []
    files = os.listdir(path)
    return [f"/static_files/{folder_key}/{f}" for f in files if f.lower().endswith(extensions)]

@app.route('/')
def home():
    return jsonify({"status": "Server active"}), 200

# File Upload Route
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No filename"}), 400
    
    filepath = os.path.join(FOLDERS['images'], file.filename)
    file.save(filepath)
    return jsonify({"message": "Uploaded successfully"}), 200

# Endpoint API Routes
@app.route('/images', methods=['GET'])
def get_images():
    return jsonify(scan_files('images', ('.png', '.jpg', '.jpeg', '.webp', '.gif')))

@app.route('/videos', methods=['GET'])
def get_videos():
    return jsonify(scan_files('videos', ('.mp4', '.mkv', '.avi', '.mov', '.3gp')))

@app.route('/music', methods=['GET'])
def get_music():
    return jsonify(scan_files('mp3', ('.mp3', '.wav', '.aac', '.m4a', '.flac')))

@app.route('/documents', methods=['GET'])
def get_documents():
    return jsonify(scan_files('documents', ('.pdf', '.doc', '.docx', '.txt', '.zip', '.xlsx')))

# Static File Serve Path
@app.route('/static_files/<category>/<filename>', methods=['GET'])
def serve_file(category, filename):
    if category in FOLDERS and os.path.exists(FOLDERS[category]):
        return send_from_directory(FOLDERS[category], filename)
    return jsonify({"error": "File not found"}), 404

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
