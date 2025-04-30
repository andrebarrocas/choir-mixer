from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import uvicorn
import subprocess
import os
import librosa
import numpy as np
import soundfile as sf
from tempfile import mkdtemp
import shutil
import uuid
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Use ["http://localhost:5173"] if you want to be strict
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SongRequest(BaseModel):
    original_url: str
    cover_urls: List[str]

def download_audio(url, output_dir):
    out_path = os.path.join(output_dir, f"{uuid.uuid4()}.wav")
    command = [
        'yt-dlp', url, '-x',
        '--audio-format', 'wav',
        '-o', out_path
    ]
    print(f"[INFO] Downloading audio: {url}")
    try:
        result = subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(result.stdout.decode())
        if os.path.exists(out_path):
            print(f"[INFO] Audio downloaded: {out_path}")
            return out_path
        else:
            print(f"[ERROR] Audio not created for URL: {url}")
            return None
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Failed to download {url}")
        print(e.stderr.decode())
        return None

def align_and_mix(original_path, cover_paths):
    print("[INFO] Loading original audio...")
    y_orig, sr = librosa.load(original_path, sr=None)
    y_orig = librosa.to_mono(y_orig)
    mix = np.copy(y_orig)

    for cover_path in cover_paths:
        print(f"[INFO] Processing cover: {cover_path}")
        y_cover, _ = librosa.load(cover_path, sr=sr)
        y_cover = librosa.to_mono(y_cover)

        # Normalize cover to prevent volume imbalance
        if np.max(np.abs(y_cover)) > 0:
            y_cover = y_cover / np.max(np.abs(y_cover))

        # Pad or trim cover to match original's length
        if len(y_cover) > len(y_orig):
            y_cover = y_cover[:len(y_orig)]
        elif len(y_cover) < len(y_orig):
            y_cover = np.pad(y_cover, (0, len(y_orig) - len(y_cover)))

        # Add to the mix
        mix += y_cover

    # Final normalization
    mix = mix / np.max(np.abs(mix))
    out_path = os.path.join(mkdtemp(), "choir_mix.wav")
    print(f"[INFO] Saving mixed audio to: {out_path}")
    sf.write(out_path, mix, sr)
    return out_path

@app.post("/generate_choir/")
def generate_choir(req: SongRequest):
    print("[INFO] Received request to generate choir")
    tmp_dir = mkdtemp()
    print(f"[INFO] Created temp directory: {tmp_dir}")
    try:
        original_path = download_audio(req.original_url, tmp_dir)
        if not original_path:
            raise HTTPException(status_code=400, detail="Failed to download original song.")

        cover_paths = []
        for url in req.cover_urls:
            path = download_audio(url, tmp_dir)
            if path:
                cover_paths.append(path)
            else:
                print(f"[WARNING] Skipped failed cover: {url}")

        if not cover_paths:
            raise HTTPException(status_code=400, detail="No valid cover songs were downloaded.")

        output_path = align_and_mix(original_path, cover_paths)
        print(f"[INFO] Choir mix completed: {output_path}")
        return {"result_path": output_path}

    finally:
        print(f"[INFO] Cleaning up temporary files at: {tmp_dir}")
        shutil.rmtree(tmp_dir, ignore_errors=True)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
