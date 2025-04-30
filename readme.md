python -m venv venv
source venv/bin/activate

pip install fastapi uvicorn yt-dlp librosa pydub numpy soundfile

brew install ffmpeg

uvicorn main:app --reload

access http://127.0.0.1:8000/docs



Links to test:

original:
https://www.youtube.com/watch?v=bo_efYhYU2A

covers:

https://www.youtube.com/watch?v=w4HK6faLpck,
https://www.youtube.com/watch?v=rEIRHVcjE6o,
https://www.youtube.com/watch?v=s3TwtZxpxwo