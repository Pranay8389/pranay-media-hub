from flask import Flask, jsonify, send_from_directory
import os

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

IMAGE_FOLDER = os.path.join(BASE_DIR, "images")
VIDEO_FOLDER = os.path.join(BASE_DIR, "videos")
MUSIC_FOLDER = os.path.join(BASE_DIR, "mp3")
DOCUMENT_FOLDER = os.path.join(BASE_DIR, "documents")


def get_files(folder, extensions):
    if not os.path.exists(folder):
        return []

    return sorted([
        filename
        for filename in os.listdir(folder)
        if filename.lower().endswith(extensions)
    ])


@app.route("/")
def home():
    return "Pranay Media Hub server is running"


# ---------- PHOTOS ----------

@app.route("/images")
def images():
    files = get_files(
        IMAGE_FOLDER,
        (".jpg", ".jpeg", ".png", ".webp", ".gif")
    )
    return jsonify(files)


@app.route("/images/<path:filename>")
def image(filename):
    return send_from_directory(IMAGE_FOLDER, filename)


# ---------- VIDEOS ----------

@app.route("/videos")
def videos():
    files = get_files(
        VIDEO_FOLDER,
        (".mp4", ".mkv", ".webm", ".mov", ".avi")
    )
    return jsonify(files)


@app.route("/videos/<path:filename>")
def video(filename):
    return send_from_directory(VIDEO_FOLDER, filename)


# ---------- MUSIC ----------

@app.route("/music")
def music():
    files = get_files(
        MUSIC_FOLDER,
        (".mp3", ".wav", ".m4a", ".ogg")
    )
    return jsonify(files)


@app.route("/music/<path:filename>")
def music_file(filename):
    return send_from_directory(MUSIC_FOLDER, filename)


# ---------- DOCUMENTS ----------

@app.route("/documents")
def documents():
    files = get_files(
        DOCUMENT_FOLDER,
        (".pdf", ".txt", ".doc", ".docx")
    )
    return jsonify(files)


@app.route("/documents/<path:filename>")
def document(filename):
    return send_from_directory(DOCUMENT_FOLDER, filename)


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000))
    
    )