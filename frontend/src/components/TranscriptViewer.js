import React from 'react';
import './TranscriptViewer.css';

function TranscriptViewer({ transcript }) {
  if (!transcript) {
    return null;
  }

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <div className="transcript-viewer">
      <h2>📝 Transcript</h2>
      <div className="transcript-full">
        <p><strong>Full Text:</strong></p>
        <p className="transcript-text">{transcript.full_text}</p>
      </div>
      
      <div className="transcript-segments">
        <h3>Segments with Timestamps</h3>
        <div className="segments-list">
          {transcript.segments.map((segment, idx) => (
            <div key={idx} className="segment-item">
              <div className="segment-time">
                {formatTime(segment.start_sec)} - {formatTime(segment.end_sec)}
              </div>
              <div className="segment-text">{segment.text}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default TranscriptViewer;
