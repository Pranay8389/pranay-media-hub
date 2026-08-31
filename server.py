import os
import requests
from flask import Flask, request, jsonify, send_from_directory

app = Flask(__name__)

# GitHub Config
GITHUB_USER = "Pranay8389"
GITHUB_REPO = "pranay-media-hub"
GITHUB_BRANCH = "main"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Folder paths
DIRS = {
    'images': os.path.join(BASE_DIR, 'images'),
    'videos': os.path.join(BASE_DIR, 'videos'),
    'music': os.path.join(BASE_DIR, 'mp3'),
    'documents': os.path.join(BASE_DIR, 'documents')
}

for path in DIRS.values():
    os.makedirs(path, exist_ok=True)

def fetch_github_files(folder_name, valid_extensions):
    url = f"https://api.github.com/repos/{GITHUB_USER}/{GITHUB_REPO}/contents/{folder_name}?ref={GITHUB_BRANCH}"
    file_list = []
    try:
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        if response.status_code == 200:
            items = response.json()
            for item in items:
                if item.get('type') == 'file':
                    download_url = item.get('download_url')
                    if download_url and any(download_url.lower().endswith(ext) for ext in valid_extensions):
                        file_list.append(download_url)
    except Exception as e:
        print(f"Error fetching from GitHub: {e}")
    return file_list

@app.route('/')
def home():
    return jsonify({"status": "Server Active"}), 200

# Flexible Upload Route: Accepts file_type or auto-detects folder
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No filename"}), 400
    
    file_type = request.form.get('file_type', 'images')
    save_dir = DIRS.get(file_type, DIRS['images'])

    filepath = os.path.join(save_dir, file.filename)
    file.save(filepath)
    return jsonify({"message": f"Uploaded successfully to {file_type}"}), 200

@app.route('/images', methods=['GET'])
def get_images():
    exts = ('.png', '.jpg', '.jpeg', '.webp', '.gif')
    files = fetch_github_files('images', exts)
    if os.path.exists(DIRS['images']):
        for f in os.listdir(DIRS['images']):
            if f.lower().endswith(exts):
                url = f"/static_img/{f}"
                if url not in files: files.append(url)
    return jsonify(files)

@app.route('/videos', methods=['GET'])
def get_videos():
    exts = ('.mp4', '.mkv', '.avi', '.mov', '.3gp', '.webm')
    files = fetch_github_files('videos', exts)
    if os.path.exists(DIRS['videos']):
        for f in os.listdir(DIRS['videos']):
            if f.lower().endswith(exts):
                url = f"/static_vid/{f}"
                if url not in files: files.append(url)
    return jsonify(files)

@app.route('/music', methods=['GET'])
def get_music():
    exts = ('.mp3', '.wav', '.aac', '.m4a', '.flac')
    files = fetch_github_files('mp3', exts)
    if os.path.exists(DIRS['music']):
        for f in os.listdir(DIRS['music']):
            if f.lower().endswith(exts):
                url = f"/static_aud/{f}"
                if url not in files: files.append(url)
    return jsonify(files)

@app.route('/documents', methods=['GET'])
def get_documents():
    exts = ('.pdf', '.doc', '.docx', '.txt', '.zip', '.xlsx')
    files = fetch_github_files('documents', exts)
    if os.path.exists(DIRS['documents']):
        for f in os.listdir(DIRS['documents']):
            if f.lower().endswith(exts):
                url = f"/static_doc/{f}"
                if url not in files: files.append(url)
    return jsonify(files)

# Serving Static Files
@app.route('/static_img/<filename>')
def serve_image(filename): return send_from_directory(DIRS['images'], filename)

@app.route('/static_vid/<filename>')
def serve_video(filename): return send_from_directory(DIRS['videos'], filename)

@app.route('/static_aud/<filename>')
def serve_audio(filename): return send_from_directory(DIRS['music'], filename)

@app.route('/static_doc/<filename>')
def serve_doc(filename): return send_from_directory(DIRS['documents'], filename)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
