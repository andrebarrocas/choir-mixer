python -m venv venv
source venv/bin/activate

pip install fastapi uvicorn yt-dlp librosa pydub numpy soundfile

brew install ffmpeg

uvicorn main:app --reload

access http://127.0.0.1:8000/docs


