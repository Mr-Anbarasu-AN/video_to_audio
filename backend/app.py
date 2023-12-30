# work
# app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
from moviepy.editor import VideoFileClip
from flask import send_from_directory
import os
import time

app = Flask(__name__)
CORS(app, origins="*", allow_headers=["Content-Type", "Authorization", "Access-Control-Allow-Credentials"], supports_credentials=True)

UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

conversion_progress = 0  # Global variable to store conversion progress

def convert_to_audio(video_path):
    global conversion_progress
    video = VideoFileClip(video_path)
    audio = video.audio
    base_path, _ = os.path.splitext(video_path)
    audio_path = os.path.join(app.config['UPLOAD_FOLDER'], 'output.mp3')

    duration = video.duration

    start_time = time.time()
    audio.write_audiofile(audio_path, codec='mp3', bitrate='192k', fps=44100)
    elapsed_time = time.time() - start_time

    conversion_progress = 100  # Set progress to 100% when conversion is complete
    return audio_path, elapsed_time

@app.route('/upload', methods=['POST'])
def upload_file():
    global conversion_progress
    conversion_progress = 0  # Reset progress when a new file is uploaded

    if 'video' not in request.files:
        return jsonify({'error': 'No video file provided'}), 400

    video_file = request.files['video']
    if video_file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    video_path = os.path.join(app.config['UPLOAD_FOLDER'], 'input.mp4')
    video_file.save(video_path)

    audio_path, elapsed_time = convert_to_audio(video_path)

    return jsonify({'message': 'Video converted to audio', 'audio_path': audio_path, 'elapsed_time': elapsed_time})

@app.route('/progress')
def progress():
    global conversion_progress
    return jsonify({'progress': conversion_progress})

@app.route('/download')
def download_file():
    audio_path = os.path.join(app.config['UPLOAD_FOLDER'], 'output.mp3')
    return send_from_directory(app.config['UPLOAD_FOLDER'], 'output.mp3', as_attachment=True)

def generate(file_path):
    with open(file_path, 'rb') as f:
        while True:
            chunk = f.read(1024)
            if not chunk:
                break
            yield chunk

if __name__ == '__main__':
    app.run(debug=True)
