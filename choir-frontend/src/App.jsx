import React, { useState } from 'react';

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
    <div style={{ padding: '2rem', fontFamily: 'Arial' }}>
      <h1>🎵 Choir Mixer</h1>
      <p>Enter the original song and cover song YouTube URLs</p>

      <div>
        <input
          type="text"
          placeholder="Original YouTube URL"
          value={originalUrl}
          onChange={(e) => setOriginalUrl(e.target.value)}
          style={{ width: '100%', marginBottom: '1rem', padding: '0.5rem' }}
        />
        <textarea
          placeholder="Cover YouTube URLs (comma-separated)"
          value={coverUrls}
          onChange={(e) => setCoverUrls(e.target.value)}
          style={{ width: '100%', height: '100px', padding: '0.5rem' }}
        />
      </div>

      <button
        onClick={handleGenerate}
        style={{ marginTop: '1rem', padding: '0.75rem 1.5rem' }}
      >
        {loading ? 'Mixing...' : 'Generate Choir Mix'}
      </button>

      {resultPath && (
        <div style={{ marginTop: '2rem' }}>
          <h3>Result:</h3>
          <audio controls src={resultPath}></audio>
          <p>📁 Path: {resultPath}</p>
        </div>
      )}
    </div>
  );
}

export default App;
