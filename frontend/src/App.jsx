import { useState } from 'react';
import { useReactMediaRecorder } from 'react-media-recorder';
import axios from 'axios';
import { Mic, Square, Loader2, Layout, Send } from 'lucide-react'; // Added 'Send' icon
import './App.css';

function App() {
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState(null);
  
  // The Hook that handles the microphone
  const { status, startRecording, stopRecording, mediaBlobUrl } = useReactMediaRecorder({ 
    audio: true,
    blobPropertyBag: { type: "audio/wav" } 
  });

  // 1. ANALYZE: Send Audio to OpenAI
  const handleAnalyze = async () => {
    if (!mediaBlobUrl) return alert("Please record something first!");
    
    setLoading(true);

    try {
      const audioBlob = await fetch(mediaBlobUrl).then(r => r.blob());
      const formData = new FormData();
      formData.append("file", audioBlob, "meeting.wav");

      // Send to Flask (Port 5000)
      const response = await axios.post("http://localhost:5000/api/process-meeting", formData);
      setData(response.data);
      
    } catch (error) {
      console.error(error);
      alert("Error connecting to backend. Is Python running on port 5000?");
    }
    
    setLoading(false);
  };

  // 2. SYNC: Send Tasks to Trello
  const handleSyncTrello = async () => {
    if (!data || !data.analysis.tasks) return;
    
    try {
        const response = await axios.post("http://localhost:5000/api/create-trello-cards", {
            tasks: data.analysis.tasks
        });
        
        if (response.data.status === "success") {
            alert(`✅ Success! Created ${response.data.created.length} cards in Trello.`);
        }
    } catch (err) {
        console.error(err);
        alert("Failed to sync with Trello. Check your API Keys in .env");
    }
  };

  return (
    <div className="app-container">
      <header>
        <h1><Layout className="icon" /> ActionPoint</h1>
        <p>AI Meeting Assistant</p>
      </header>

      <main>
        {/* SECTION 1: The Recorder */}
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

          {/* Only show Analyze button if we have a recording and aren't loading */}
          {mediaBlobUrl && status === 'stopped' && (
            <div className="analyze-section">
              <audio src={mediaBlobUrl} controls />
              <button 
                className="btn analyze" 
                onClick={handleAnalyze} 
                disabled={loading}
              >
                {loading ? <><Loader2 className="spin" /> Analyzing...</> : "✨ Analyze Meeting"}
              </button>
            </div>
          )}
        </div>

        {/* SECTION 2: The Results */}
        {data && (
          <div className="results-container">
            {/* Transcript Section */}
            <div className="result-card">
              <h2>📝 Transcript</h2>
              <p className="transcript-text">{data.transcript}</p>
            </div>

            {/* AI Summary Section */}
            <div className="result-card">
              <h2>🤖 AI Summary</h2>
              <p>{data.analysis.summary}</p>
            </div>

            {/* Tasks Section */}
            <div className="result-card">
              <div className="task-header-row">
                <h2>✅ Identified Tasks</h2>
                <button className="btn sync" onClick={handleSyncTrello}>
                    <Send size={16} /> Sync to Trello
                </button>
              </div>

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