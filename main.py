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

app = FastAPI()

# Enable CORS for local frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

        # Resolve actual output file
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

def align_and_mix(original_path, cover_paths):
    print("[INFO] Loading original audio...")
    y_orig, sr = librosa.load(original_path, sr=None)
    y_orig = librosa.to_mono(y_orig)
    mix = np.copy(y_orig)

    for cover_path in cover_paths:
        print(f"[INFO] Processing cover: {cover_path}")
        y_cover, _ = librosa.load(cover_path, sr=sr)
        y_cover = librosa.to_mono(y_cover)

        if np.max(np.abs(y_cover)) > 0:
            y_cover = y_cover / np.max(np.abs(y_cover))

        if len(y_cover) > len(y_orig):
            y_cover = y_cover[:len(y_orig)]
        elif len(y_cover) < len(y_orig):
            y_cover = np.pad(y_cover, (0, len(y_orig) - len(y_cover)))

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

        # Extract text fields
        original_url = form.get("original_url")
        cover_urls = form.get("cover_urls")

        # Extract file fields
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
