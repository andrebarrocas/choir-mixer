from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import subprocess
import os
import librosa
import numpy as np
import soundfile as sf
from tempfile import mkdtemp
import shutil
import uuid
import whisper

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load Whisper model once
whisper_model = whisper.load_model("base")  # Change to "medium" or "large" for better accuracy

def download_audio(url, output_dir):
    out_path = os.path.join(output_dir, f"{uuid.uuid4()}.%(ext)s")
    command = [
        'yt-dlp', url, '-x',
        '--audio-format', 'wav',
        '-o', out_path
    ]
    print(f"[INFO] Downloading audio: {url}")
    try:
        result = subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(result.stdout.decode())
        expected_file = out_path.replace('%(ext)s', 'wav')
        if os.path.exists(expected_file):
            print(f"[INFO] Audio downloaded: {expected_file}")
            return expected_file
        else:
            print(f"[ERROR] Audio not created for URL: {url}")
            return None
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Failed to download {url}")
        print(e.stderr.decode())
        return None

def trim_to_first_onset(y, sr):
    onset_frames = librosa.onset.onset_detect(y=y, sr=sr, backtrack=True)
    if len(onset_frames) == 0:
        return y
    onset_sample = librosa.frames_to_samples(onset_frames[0])
    return y[onset_sample:]

def align_and_mix(original_path, cover_paths):
    print("[INFO] Loading original audio...")
    y_orig, sr = librosa.load(original_path, sr=None)
    y_orig = librosa.to_mono(y_orig)
    y_orig = trim_to_first_onset(y_orig, sr)

    env_orig = librosa.onset.onset_strength(y=y_orig, sr=sr)
    mix = np.copy(y_orig)

    for cover_path in cover_paths:
        print(f"[INFO] Processing cover: {cover_path}")
        y_cover, _ = librosa.load(cover_path, sr=sr)
        y_cover = librosa.to_mono(y_cover)
        y_cover = trim_to_first_onset(y_cover, sr)

        env_cover = librosa.onset.onset_strength(y=y_cover, sr=sr)
        correlation = np.correlate(env_orig, env_cover, mode='full')
        lag = np.argmax(correlation) - len(env_cover)

        sample_shift = lag * 512  # 512 is default hop_length for onset_strength
        print(f"[INFO] Aligning with lag: {lag}, sample shift: {sample_shift}")

        if sample_shift > 0:
            y_cover = np.pad(y_cover, (sample_shift, 0))
        elif sample_shift < 0:
            y_cover = y_cover[-sample_shift:]

        if np.max(np.abs(y_cover)) > 0:
            y_cover = y_cover / np.max(np.abs(y_cover))

        if len(y_cover) > len(mix):
            y_cover = y_cover[:len(mix)]
        elif len(y_cover) < len(mix):
            y_cover = np.pad(y_cover, (0, len(mix) - len(y_cover)))

        mix += y_cover

    mix = mix / np.max(np.abs(mix))
    out_path = os.path.join(mkdtemp(), "choir_mix.wav")
    print(f"[INFO] Saving mixed audio to: {out_path}")
    sf.write(out_path, mix, sr)
    return out_path

@app.post("/generate_choir/")
async def generate_choir(request: Request):
    print("[INFO] Received request to generate choir")
    tmp_dir = mkdtemp()
    print(f"[INFO] Created temp directory: {tmp_dir}")
    try:
        form = await request.form()
        original_url = form.get("original_url")
        cover_urls = form.get("cover_urls")
        original_file = form.get("original_file")
        cover_files = form.getlist("cover_files")

        # Handle original
        if original_url:
            original_path = download_audio(original_url, tmp_dir)
            if not original_path:
                raise HTTPException(status_code=400, detail="Failed to download original song.")
        elif original_file:
            original_path = os.path.join(tmp_dir, f"original_{uuid.uuid4()}.wav")
            with open(original_path, "wb") as f:
                f.write(await original_file.read())
        else:
            raise HTTPException(status_code=400, detail="Original song not provided.")

        # Handle covers
        cover_paths = []
        if cover_urls:
            for url in cover_urls.split(','):
                url = url.strip()
                if url:
                    path = download_audio(url, tmp_dir)
                    if path:
                        cover_paths.append(path)

        for file in cover_files:
            path = os.path.join(tmp_dir, f"cover_{uuid.uuid4()}.wav")
            with open(path, "wb") as f:
                f.write(await file.read())
            cover_paths.append(path)

        if not cover_paths:
            raise HTTPException(status_code=400, detail="No valid cover songs provided.")

        output_path = align_and_mix(original_path, cover_paths)
        print(f"[INFO] Choir mix completed: {output_path}")
        return {"result_path": output_path}

    finally:
        print(f"[INFO] Cleaning up temporary files at: {tmp_dir}")
        shutil.rmtree(tmp_dir, ignore_errors=True)

@app.get("/get_audio/")
def get_audio(path: str):
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="File not found.")
    return FileResponse(path, media_type="audio/wav", filename="choir_mix.wav")

def extract_lyrics(file_path):
    print(f"[INFO] Transcribing {file_path} using Whisper")
    result = whisper_model.transcribe(file_path)
    segments = result.get("segments", [])
    lyrics = []
    for seg in segments:
        lyrics.append({
            "start": round(seg["start"], 2),
            "end": round(seg["end"], 2),
            "text": seg["text"].strip()
        })
    return lyrics

@app.post("/extract_lyrics/")
async def extract_lyrics_endpoint(request: Request):
    print("[INFO] Received request to extract lyrics from audio")
    form = await request.form()
    file = form.get("audio_file")

    if not file:
        raise HTTPException(status_code=400, detail="No audio file provided")

    tmp_dir = mkdtemp()
    try:
        path = os.path.join(tmp_dir, f"{uuid.uuid4()}.wav")
        with open(path, "wb") as f:
            f.write(await file.read())

        lyrics_data = extract_lyrics(path)
        return {"lyrics": lyrics_data}

    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
