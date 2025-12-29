import { useState } from 'react';
import { useReactMediaRecorder } from 'react-media-recorder';
import axios from 'axios';
import { Mic, Square, Loader2, Layout } from 'lucide-react';
import './App.css';

function App() {
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState(null);
  
  const { status, startRecording, stopRecording, mediaBlobUrl } = useReactMediaRecorder({ 
    audio: true,
    blobPropertyBag: { type: "audio/wav" } 
  });

  const handleAnalyze = async () => {
    if (!mediaBlobUrl) return alert("Please record something first!");
    setLoading(true);

    try {
      const audioBlob = await fetch(mediaBlobUrl).then(r => r.blob());
      const formData = new FormData();
      formData.append("file", audioBlob, "meeting.wav");

      // Send to Flask Backend (Port 5000)
      const response = await axios.post("http://localhost:5000/api/process-meeting", formData);
      setData(response.data);
      
    } catch (error) {
      console.error(error);
      alert("Error connecting to backend. Is Python running?");
    }
    setLoading(false);
  };

  return (
    <div className="app-container">
      <header>
        <h1><Layout className="icon" /> ActionPoint</h1>
        <p>AI Meeting Assistant</p>
      </header>

      <main>
        {/* Recorder Section */}
        <div className="recorder-card">
          <div className={`status-badge ${status}`}>
            Status: {status.toUpperCase()}
          </div>
          
          <div className="controls">
            {status !== 'recording' ? (
              <button className="btn start" onClick={startRecording}>
                <Mic size={20} /> Start Recording
              </button>
            ) : (
              <button className="btn stop" onClick={stopRecording}>
                <Square size={20} /> Stop Recording
              </button>
            )}
          </div>

          {mediaBlobUrl && status === 'stopped' && (
            <div className="analyze-section">
              <audio src={mediaBlobUrl} controls />
              <button className="btn analyze" onClick={handleAnalyze} disabled={loading}>
                {loading ? <><Loader2 className="spin" /> Analyzing...</> : "✨ Analyze Meeting"}
              </button>
            </div>
          )}
        </div>

        {/* Results Section */}
        {data && (
          <div className="results-container">
            <div className="result-card">
              <h2>📝 Transcript</h2>
              <p className="transcript-text">{data.transcript}</p>
            </div>

            <div className="result-card">
              <h2>🤖 AI Summary</h2>
              <p>{data.analysis.summary}</p>
            </div>

            <div className="result-card">
              <h2>✅ Identified Tasks</h2>
              <div className="task-list">
                {data.analysis.tasks.map((task, index) => (
                  <div key={index} className="task-item">
                    <div className="task-header">
                      <span className="task-title">{task.title}</span>
                      <span className={`badge ${task.priority.toLowerCase()}`}>{task.priority}</span>
                    </div>
                    <p className="task-desc">{task.description}</p>
                    <div className="task-footer">
                      <span>👤 {task.assignee}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;