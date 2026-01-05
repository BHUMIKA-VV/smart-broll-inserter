import React from 'react';
import './TimelineViewer.css';

function TimelineViewer({ insertions, brollClips, arollDuration }) {
  if (!insertions || insertions.length === 0) {
    return (
      <div className="timeline-viewer">
        <h2>📊 Timeline Plan</h2>
        <p>No insertions planned.</p>
      </div>
    );
  }

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const getBrollInfo = (brollId) => {
    return brollClips.find((clip) => clip.broll_id === brollId) || null;
  };

  const getPositionPercent = (time) => {
    return (time / arollDuration) * 100;
  };

  return (
    <div className="timeline-viewer">
      <h2>📊 Timeline Plan</h2>
      <p className="summary">
        <strong>{insertions.length}</strong> B-roll insertion{insertions.length !== 1 ? 's' : ''} planned
      </p>

      <div className="timeline-visual">
        <div className="timeline-bar">
          <div className="timeline-start">0:00</div>
          <div className="timeline-end">{formatTime(arollDuration)}</div>
          {insertions.map((insertion, idx) => (
            <div
              key={idx}
              className="insertion-marker"
              style={{
                left: `${getPositionPercent(insertion.start_sec)}%`,
                width: `${getPositionPercent(insertion.duration_sec)}%`,
              }}
              title={`${formatTime(insertion.start_sec)} - ${formatTime(insertion.start_sec + insertion.duration_sec)}`}
            />
          ))}
        </div>
      </div>

      <div className="insertions-list">
        {insertions.map((insertion, idx) => {
          const brollInfo = getBrollInfo(insertion.broll_id);
          return (
            <div key={idx} className="insertion-item">
              <div className="insertion-header">
                <span className="insertion-number">#{idx + 1}</span>
                <span className="insertion-time">
                  {formatTime(insertion.start_sec)} - {formatTime(insertion.start_sec + insertion.duration_sec)}
                </span>
                <span className="insertion-duration">
                  ({insertion.duration_sec}s)
                </span>
                <span className="insertion-confidence">
                  Confidence: {(insertion.confidence * 100).toFixed(0)}%
                </span>
              </div>
              
              <div className="insertion-details">
                <div className="broll-info">
                  <strong>B-roll Clip:</strong> {insertion.broll_id}
                  {brollInfo && (
                    <div className="broll-description">
                      {brollInfo.description}
                    </div>
                  )}
                </div>
                
                <div className="insertion-reason">
                  <strong>Reason:</strong> {insertion.reason}
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

export default TimelineViewer;
