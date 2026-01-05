import React, { useState } from 'react';
import axios from 'axios';
import './FileUpload.css';

function FileUpload({ onPlanGenerated, onError, onLoading, loading }) {
  const [arollFile, setArollFile] = useState(null);
  const [brollFiles, setBrollFiles] = useState([]);
  const [numInsertions, setNumInsertions] = useState(4);
  const [renderVideo, setRenderVideo] = useState(false);

  const handleArollChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setArollFile(file);
    }
  };

  const handleBrollChange = (e) => {
    const files = Array.from(e.target.files);
    setBrollFiles(files);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!arollFile) {
      onError('Please select an A-roll video');
      return;
    }

    if (brollFiles.length === 0) {
      onError('Please select at least one B-roll clip');
      return;
    }

    onLoading(true);
    onError(null);

    const formData = new FormData();
    formData.append('aroll', arollFile);
    brollFiles.forEach((file) => {
      formData.append('brolls', file);
    });
    formData.append('num_insertions', numInsertions);
    formData.append('render_video', renderVideo);

    try {
      const response = await axios.post('/api/plan', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        timeout: 300000, // 5 minutes timeout
      });

      onPlanGenerated(response.data);
    } catch (error) {
      console.error('Error generating plan:', error);
      onError(
        error.response?.data?.error ||
        error.message ||
        'Failed to generate plan. Please try again.'
      );
    } finally {
      onLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="file-upload-form">
      <div className="upload-section">
        <h2>Upload Videos</h2>
        
        <div className="file-input-group">
          <label htmlFor="aroll">
            <strong>A-roll Video (Talking Head)</strong>
            <span className="file-info">Required</span>
          </label>
          <input
            type="file"
            id="aroll"
            accept="video/*"
            onChange={handleArollChange}
            disabled={loading}
          />
          {arollFile && (
            <div className="file-name">Selected: {arollFile.name}</div>
          )}
        </div>

        <div className="file-input-group">
          <label htmlFor="brolls">
            <strong>B-roll Clips</strong>
            <span className="file-info">Select multiple files</span>
          </label>
          <input
            type="file"
            id="brolls"
            accept="video/*"
            multiple
            onChange={handleBrollChange}
            disabled={loading}
          />
          {brollFiles.length > 0 && (
            <div className="file-list">
              <strong>Selected ({brollFiles.length}):</strong>
              <ul>
                {brollFiles.map((file, idx) => (
                  <li key={idx}>{file.name}</li>
                ))}
              </ul>
            </div>
          )}
        </div>

        <div className="options-group">
          <div className="option-item">
            <label htmlFor="num_insertions">
              Number of Insertions:
            </label>
            <input
              type="number"
              id="num_insertions"
              min="1"
              max="10"
              value={numInsertions}
              onChange={(e) => setNumInsertions(parseInt(e.target.value))}
              disabled={loading}
            />
          </div>

          <div className="option-item">
            <label htmlFor="render_video">
              <input
                type="checkbox"
                id="render_video"
                checked={renderVideo}
                onChange={(e) => setRenderVideo(e.target.checked)}
                disabled={loading}
              />
              Render Final Video (Optional)
            </label>
          </div>
        </div>

        <button
          type="submit"
          className="submit-button"
          disabled={loading || !arollFile || brollFiles.length === 0}
        >
          {loading ? 'Processing...' : 'Generate B-roll Plan'}
        </button>
      </div>
    </form>
  );
}

export default FileUpload;
