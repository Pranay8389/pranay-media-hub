import os
from flask import Flask, request, jsonify, send_from_directory

app = Flask(__name__)

# Upload folders configuration
UPLOAD_FOLDER = 'uploads'
os.makedirs(os.path.join(UPLOAD_FOLDER, 'images'), exist_ok=True)
os.makedirs(os.path.join(UPLOAD_FOLDER, 'videos'), exist_ok=True)
os.makedirs(os.path.join(UPLOAD_FOLDER, 'music'), exist_ok=True)
os.makedirs(os.path.join(UPLOAD_FOLDER, 'documents'), exist_ok=True)

@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file uploaded"}), 400
            
        file = request.files['file']
        file_type = request.form.get('file_type', 'documents')

        if file.filename == '':
            return jsonify({"error": "No filename provided"}), 400

        # Validate directory
        valid_folders = ['images', 'videos', 'music', 'documents']
        if file_type not in valid_folders:
            file_type = 'documents'

        # Save file directly without using 'with' statement
        save_dir = os.path.join(UPLOAD_FOLDER, file_type)
        save_path = os.path.join(save_dir, file.filename)
        
        # 🟢 Correct way to save file in Flask:
        file.save(save_path)

        return jsonify({"message": "File uploaded successfully", "path": f"/uploads/{file_type}/{file.filename}"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/images', methods=['GET'])
def get_images():
    files = os.listdir(os.path.join(UPLOAD_FOLDER, 'images'))
    return jsonify([f"/uploads/images/{f}" for f in files])

@app.route('/videos', methods=['GET'])
def get_videos():
    files = os.listdir(os.path.join(UPLOAD_FOLDER, 'videos'))
    return jsonify([f"/uploads/videos/{f}" for f in files])

@app.route('/music', methods=['GET'])
def get_music():
    files = os.listdir(os.path.join(UPLOAD_FOLDER, 'music'))
    return jsonify([f"/uploads/music/{f}" for f in files])

@app.route('/documents', methods=['GET'])
def get_documents():
    files = os.listdir(os.path.join(UPLOAD_FOLDER, 'documents'))
    return jsonify([f"/uploads/documents/{f}" for f in files])

@app.route('/uploads/<folder>/<filename>', methods=['GET'])
def serve_file(folder, filename):
    return send_from_directory(os.path.join(UPLOAD_FOLDER, folder), filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
