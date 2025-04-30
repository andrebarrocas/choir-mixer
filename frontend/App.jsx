// frontend/App.jsx

import React, { useState } from 'react';

export default function App() {
  const [original, setOriginal] = useState('');
  const [covers, setCovers] = useState('');
  const [audioUrl, setAudioUrl] = useState('');

  const handleSubmit = async () => {
    const response = await fetch('http://localhost:8000/generate_choir/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        original_url: original,
        cover_urls: covers.split(',').map(s => s.trim())
      })
    });

    const data = await response.json();
    setAudioUrl(data.result_path);
  };

  return (
    <div className="p-4">
      <h1 className="text-xl mb-2">🎵 Choir Builder</h1>
      <input className="w-full mb-2 p-2" placeholder="Original Song URL" onChange={e => setOriginal(e.target.value)} />
      <textarea className="w-full mb-2 p-2" placeholder="Cover Song URLs, comma-separated" onChange={e => setCovers(e.target.value)} />
      <button onClick={handleSubmit} className="bg-blue-500 text-white px-4 py-2">Create Choir</button>

      {audioUrl && (
        <div className="mt-4">
          <h2 className="text-lg">Result:</h2>
          <audio controls src={audioUrl}></audio>
        </div>
      )}
    </div>
  );
}
