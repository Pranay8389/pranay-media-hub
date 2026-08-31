import os
import requests
from flask import Flask, request, jsonify, send_from_directory

app = Flask(__name__)

# GitHub Config
GITHUB_USER = "Pranay8389"
GITHUB_REPO = "pranay-media-hub"
GITHUB_BRANCH = "main"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOCAL_IMAGES = os.path.join(BASE_DIR, 'images')
os.makedirs(LOCAL_IMAGES, exist_ok=True)

# Helper function to fetch files directly from GitHub API
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

# File Upload Route (Saves uploaded files locally and appends to response)
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No filename"}), 400
    
    filepath = os.path.join(LOCAL_IMAGES, file.filename)
    file.save(filepath)
    return jsonify({"message": "Uploaded successfully"}), 200

# API Endpoints linked directly to GitHub Data
@app.route('/images', methods=['GET'])
def get_images():
    exts = ('.png', '.jpg', '.jpeg', '.webp', '.gif')
    # Fetch from GitHub
    github_files = fetch_github_files('images', exts)
    
    # Also include newly app-uploaded local files
    if os.path.exists(LOCAL_IMAGES):
        for f in os.listdir(LOCAL_IMAGES):
            if f.lower().endswith(exts):
                local_url = f"/static_img/{f}"
                if local_url not in github_files:
                    github_files.append(local_url)
                    
    return jsonify(github_files)

@app.route('/videos', methods=['GET'])
def get_videos():
    exts = ('.mp4', '.mkv', '.avi', '.mov', '.3gp', '.webm')
    return jsonify(fetch_github_files('videos', exts))

@app.route('/music', methods=['GET'])
def get_music():
    exts = ('.mp3', '.wav', '.aac', '.m4a', '.flac')
    return jsonify(fetch_github_files('mp3', exts))

@app.route('/documents', methods=['GET'])
def get_documents():
    exts = ('.pdf', '.doc', '.docx', '.txt', '.zip', '.xlsx')
    return jsonify(fetch_github_files('documents', exts))

# Serve locally uploaded images
@app.route('/static_img/<filename>')
def serve_image(filename):
    return send_from_directory(LOCAL_IMAGES, filename)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
