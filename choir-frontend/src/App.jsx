import React, { useState } from 'react';
import './App.css';

function App() {
  const [originalUrl, setOriginalUrl] = useState('');
  const [coverUrls, setCoverUrls] = useState('');
  const [originalFile, setOriginalFile] = useState(null);
  const [coverFiles, setCoverFiles] = useState([]);
  const [resultPath, setResultPath] = useState('');
  const [loading, setLoading] = useState(false);
  const [showUpload, setShowUpload] = useState(false);
  const [musicStarted, setMusicStarted] = useState(false);

  const handleGenerate = async () => {
    setLoading(true);
    setResultPath('');
    try {
      const formData = new FormData();
      if (originalUrl) formData.append('original_url', originalUrl);
      if (coverUrls) formData.append('cover_urls', coverUrls);
      if (originalFile) formData.append('original_file', originalFile);
      for (let i = 0; i < coverFiles.length; i++) {
        formData.append('cover_files', coverFiles[i]);
      }

      const response = await fetch('http://localhost:8000/generate_choir/', {
        method: 'POST',
        body: formData
      });

      const data = await response.json();
      if (data.result_path) {
        setResultPath(data.result_path);
      } else {
        alert('Failed to generate choir mix.');
      }
    } catch (err) {
      console.error(err);
      alert('Error during request.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="App">
      <div className="container">
        <h1>🎵 Choir Mixer</h1>
        <p>Enter YouTube URLs or upload songs manually</p>

        <input
          type="text"
          placeholder="Original YouTube URL"
          value={originalUrl}
          onChange={(e) => setOriginalUrl(e.target.value)}
        />
        <textarea
          placeholder="Cover YouTube URLs (comma-separated)"
          value={coverUrls}
          onChange={(e) => setCoverUrls(e.target.value)}
        />

        {showUpload && (
          <div className="upload-section" style={{ marginBottom: '1rem' }}>
            <div>
              <label style={{ display: 'block', marginBottom: '0.25rem' }}>Upload Original Song:</label>
              <input
                type="file"
                accept="audio/*"
                onChange={(e) => setOriginalFile(e.target.files[0])}
              />
            </div>

            <div style={{ marginTop: '1rem' }}>
              <label style={{ display: 'block', marginBottom: '0.25rem' }}>Upload Cover Songs:</label>
              <input
                type="file"
                accept="audio/*"
                multiple
                onChange={(e) => setCoverFiles(Array.from(e.target.files))}
              />
            </div>
          </div>
        )}

        <div className="button-group">
          <button
            className="upload-btn"
            onClick={() => setShowUpload(!showUpload)}
          >
            {showUpload ? 'Hide Manual Uploads' : 'Upload Songs Manually'}
          </button>

          <button
            className="mix-btn"
            onClick={handleGenerate}
            disabled={loading}
          >
            {loading ? 'Mixing...' : 'Generate Choir Mix'}
          </button>
        </div>

        {resultPath && (
          <div className={`result ${musicStarted ? 'futuristic-mode' : ''}`}>
            <audio
              controls
              src={`http://localhost:8000/get_audio/?path=${encodeURIComponent(resultPath)}`}
              onPlay={() => setMusicStarted(true)}
              onPause={() => setMusicStarted(false)}
            ></audio>
            <p className="path">📁 Path: {resultPath}</p>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
