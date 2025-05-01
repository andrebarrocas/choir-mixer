# 🎶 Choir Mixer

This application application downloads an original song and multiple cover versions from YouTube, aligns them, and mixes them into a single choir-like audio output.
Optionally you can also upload the music files manually.

## Features

- Download audio from YouTube using `yt-dlp`.
- Align and mix multiple cover versions with the original song using `librosa`.
- Serve the mixed audio through a FastAPI backend.
- Interactive API documentation available via Swagger UI.

## Installation

### 1. Clone the Repository


```bash
git clone https://github.com/andrebarrocas/choir-mixer.git
cd choir-mixer
```


### 2. Set Up a Virtual Environment


```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```


### 3. Install Dependencies


```bash
pip install -r requirements.txt
```


*Note: Ensure `ffmpeg` is installed on your system.*

- **macOS**: `brew install ffmpeg`
- **Ubuntu**: `sudo apt-get install ffmpeg`
- **Windows**: Download from [FFmpeg official website](https://ffmpeg.org/download.html) and add to PATH.

### Running the Application

1. **Run the backend**:
```bash
uvicorn main:app --reload
```

2. **Run the React frontend**:
```bash
cd choir-frontend
npm install
npm start
```

### Testing the Application
1. **Access the Application:**

   Open your browser and navigate to [http://localhost:5173](http://localhost:5173).

2. **Input the Original Song URL:**

   In the "Original YouTube URL" field, enter:

   ```
   https://www.youtube.com/watch?v=bo_efYhYU2A
   ```

3. **Input Cover Song URLs:**

   In the "Cover YouTube URLs" field, enter the following URLs, separated by commas:

   ```
   https://www.youtube.com/watch?v=w4HK6faLpck, https://www.youtube.com/watch?v=rEIRHVcjE6o, https://www.youtube.com/watch?v=s3TwtZxpxwo
   ```

4. **Generate Choir Mix:**

   Click the "Generate Choir Mix" button. The application will process the inputs and, upon completion, provide an audio player to listen to the mixed result.

### Backend Integration

Ensure the backend server is running to handle requests from the frontend. 