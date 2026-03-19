import os
import subprocess
from openai import OpenAI
from dotenv import load_dotenv
from flask import Flask, request, jsonify, render_template

load_dotenv()
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

def format_timestamp(seconds: float):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = seconds % 60
    milliseconds = int((secs - int(secs)) * 1000)
    return f"{hours:02}:{minutes:02}:{int(secs):02},{milliseconds:03}"

def generate_srt(segments):
    srt_content = ""
    for i, segment in enumerate(segments, start=1):
        if hasattr(segment, 'model_dump'):
            segment = segment.model_dump()
        elif hasattr(segment, 'start'):
            segment = {'start': segment.start, 'end': segment.end, 'text': segment.text}
             
        start = format_timestamp(segment['start'])
        end = format_timestamp(segment['end'])
        text = segment['text'].strip()
        srt_content += f"{i}\n{start} --> {end}\n{text}\n\n"
    return srt_content

@app.route('/transcribe', methods=['POST'])
def transcribe():
    if 'video' not in request.files:
        return jsonify({'error': 'No video file provided'}), 400
    
    file = request.files['video']
    language = request.form.get('language', 'auto')
    task_type = request.form.get('task', 'transcribe')
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
        
    if file and file.filename.endswith('.mp4'):
        video_path = os.path.join(UPLOAD_FOLDER, 'input.mp4')
        audio_path = os.path.join(UPLOAD_FOLDER, 'output.mp3')
        
        file.save(video_path)
        
        try:
            subprocess.run(['ffmpeg', '-y', '-i', video_path, '-vn', '-acodec', 'libmp3lame', '-q:a', '2', audio_path], check=True, capture_output=True)
        except subprocess.CalledProcessError as e:
            print("FFmpeg Error:", e.stderr.decode('utf-8'))
            return jsonify({'error': 'Failed to extract audio using FFmpeg.'}), 500
            
        if not os.path.exists(audio_path):
             return jsonify({'error': 'Audio file was not created'}), 500
             
        try:
            with open(audio_path, "rb") as audio_file:
                transcribe_kwargs = {
                    "model": "whisper-1",
                    "file": audio_file,
                    "response_format": "verbose_json"
                }
                if language and language != 'auto':
                    transcribe_kwargs['language'] = language
                    
                print(f"Transcribing using OpenAI API...")
                result = client.audio.transcriptions.create(**transcribe_kwargs)
                
                if hasattr(result, 'model_dump'):
                    result_dict = result.model_dump()
                else:
                    try:
                        import json
                        result_dict = json.loads(result.json())
                    except:
                        if isinstance(result, dict):
                            result_dict = result
                        else:
                            result_dict = {"text": result.text, "segments": getattr(result, 'segments', [])}
                
                srt_content = generate_srt(result_dict.get('segments', []))
                
                response_data = dict(result_dict)
                response_data['srt_content'] = srt_content
                
                return jsonify(response_data)
        except Exception as e:
            print("OpenAI API Error:", e)
            return jsonify({'error': str(e)}), 500

    return jsonify({'error': 'Invalid file format.'}), 400

if __name__ == '__main__':
    app.run(debug=True, port=5001)
