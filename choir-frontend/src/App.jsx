import React, { useState } from 'react';
import './App.css';

function App() {
  const [originalUrl, setOriginalUrl] = useState('');
  const [coverUrls, setCoverUrls] = useState('');
  const [resultPath, setResultPath] = useState('');
  const [loading, setLoading] = useState(false);

  const handleGenerate = async () => {
    setLoading(true);
    setResultPath('');
    try {
      const response = await fetch('http://localhost:8000/generate_choir/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          original_url: originalUrl,
          cover_urls: coverUrls.split(',').map(url => url.trim())
        })
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
        <p>Enter the original song and cover song YouTube URLs</p>

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

        <button onClick={handleGenerate} disabled={loading}>
          {loading ? 'Mixing...' : 'Generate Choir Mix'}
        </button>

        {resultPath && (
          <div className="result">
            <h3>Result:</h3>
            <audio
              controls
              src={`http://localhost:8000/get_audio/?path=${encodeURIComponent(resultPath)}`}
            ></audio>
            <p className="path">📁 Path: {resultPath}</p>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
