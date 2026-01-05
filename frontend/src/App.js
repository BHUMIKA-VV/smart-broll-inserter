import React, { useState } from 'react';
import './App.css';
import FileUpload from './components/FileUpload';
import TranscriptViewer from './components/TranscriptViewer';
import TimelineViewer from './components/TimelineViewer';

function App() {
  const [timelinePlan, setTimelinePlan] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handlePlanGenerated = (plan) => {
    setTimelinePlan(plan);
    setError(null);
  };

  const handleError = (err) => {
    setError(err);
    setTimelinePlan(null);
  };

  const handleLoading = (isLoading) => {
    setLoading(isLoading);
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>🎬 Smart B-roll Inserter</h1>
        <p>Automatically plan B-roll insertions for your UGC videos</p>
      </header>

      <main className="App-main">
        <FileUpload
          onPlanGenerated={handlePlanGenerated}
          onError={handleError}
          onLoading={handleLoading}
          loading={loading}
        />

        {error && (
          <div className="error-message">
            <h3>Error</h3>
            <p>{error}</p>
          </div>
        )}

        {loading && (
          <div className="loading-message">
            <div className="spinner"></div>
            <p>Processing your videos... This may take a few minutes.</p>
          </div>
        )}

        {timelinePlan && (
          <div className="results-container">
            <TranscriptViewer transcript={timelinePlan.timeline_plan.transcript} />
            <TimelineViewer
              insertions={timelinePlan.timeline_plan.insertions}
              brollClips={timelinePlan.timeline_plan.broll_clips}
              arollDuration={timelinePlan.timeline_plan.aroll_duration_sec}
            />
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
