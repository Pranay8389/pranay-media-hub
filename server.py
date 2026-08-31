import os
from flask import Flask, request, jsonify, send_from_directory

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Folder setup matching Git directories
FOLDERS = {
    'images': os.path.join(BASE_DIR, 'images'),
    'videos': os.path.join(BASE_DIR, 'videos'),
    'music': os.path.join(BASE_DIR, 'music'),
    'documents': os.path.join(BASE_DIR, 'documents')
}

for folder in FOLDERS.values():
    os.makedirs(folder, exist_ok=True)

@app.route('/')
def home():
    return jsonify({"status": "Server Running"}), 200

# File Upload Route
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No filename"}), 400
    
    # Save image directly to images folder
    filepath = os.path.join(FOLDERS['images'], file.filename)
    file.save(filepath)
    return jsonify({"message": "Uploaded successfully"}), 200

# Fetch Media Lists
def get_file_list(folder_key, extensions):
    path = FOLDERS[folder_key]
    if not os.path.exists(path):
        return []
    files = os.listdir(path)
    return [f"/static_files/{folder_key}/{f}" for f in files if f.lower().endswith(extensions)]

@app.route('/images', methods=['GET'])
def get_images():
    return jsonify(get_file_list('images', ('png', 'jpg', 'jpeg', 'webp')))

@app.route('/videos', methods=['GET'])
def get_videos():
    return jsonify(get_file_list('videos', ('mp4', 'mkv', 'avi', 'mov')))

@app.route('/music', methods=['GET'])
def get_music():
    return jsonify(get_file_list('music', ('mp3', 'wav', 'aac', 'm4a')))

@app.route('/documents', methods=['GET'])
def get_documents():
    return jsonify(get_file_list('documents', ('pdf', 'doc', 'docx', 'txt')))

# Serve static files dynamically
@app.route('/static_files/<category>/<filename>', methods=['GET'])
def serve_file(category, filename):
    if category in FOLDERS:
        return send_from_directory(FOLDERS[category], filename)
    return jsonify({"error": "Not Found"}), 404

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
