import { useState } from "react";
import { useReactMediaRecorder } from "react-media-recorder";
import axios from "axios";
import {
  Mic,
  Square,
  Loader2,
  Layout,
  Send,
  User,
  Lock,
  Mail,
  ChevronRight,
  Settings,
  History,
  Plus,
} from "lucide-react";
import "./App.css";

function App() {
  // --- STATE ---
  const [currentView, setCurrentView] = useState("login"); // 'login', 'signup', 'dashboard'
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState(null);

  // Auth Forms State
  const [authForm, setAuthForm] = useState({
    name: "",
    email: "",
    password: "",
  });

  // Recording Hook
  const { status, startRecording, stopRecording, mediaBlobUrl } =
    useReactMediaRecorder({
      audio: true,
      blobPropertyBag: { type: "audio/wav" },
    });

  // --- AUTHENTICATION HANDLERS ---
  const handleAuthChange = (e) => {
    setAuthForm({ ...authForm, [e.target.name]: e.target.value });
  };

  const handleSignup = async (e) => {
    e.preventDefault();
    try {
      await axios.post("http://localhost:5000/api/signup", authForm);
      alert("Signup successful! Please login.");
      setCurrentView("login");
    } catch (err) {
      alert(err.response?.data?.error || "Signup failed");
    }
  };

  const handleLogin = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.post("http://localhost:5000/api/login", {
        email: authForm.email,
        password: authForm.password,
      });
      setUser(response.data.user);
      setCurrentView("dashboard");
    } catch (err) {
      alert(err.response?.data?.error || "Login failed");
    }
  };

  const handleLogout = () => {
    setUser(null);
    setData(null);
    setCurrentView("login");
  };

  // --- API HANDLERS ---
  const handleAnalyze = async () => {
    if (!mediaBlobUrl) return alert("Please record something first!");
    setLoading(true);
    try {
      const audioBlob = await fetch(mediaBlobUrl).then((r) => r.blob());
      const formData = new FormData();
      formData.append("file", audioBlob, "meeting.wav");

      const response = await axios.post(
        "http://localhost:5000/api/process-meeting",
        formData,
      );
      setData(response.data);
    } catch (error) {
      console.error(error);
      alert("Error connecting to backend.");
    }
    setLoading(false);
  };

  const handleSyncTrello = async () => {
    if (!data || !data.analysis.tasks) return;
    try {
      const response = await axios.post(
        "http://localhost:5000/api/create-trello-cards",
        {
          tasks: data.analysis.tasks,
        },
      );
      if (response.data.status === "success") {
        alert(
          `✅ Success! Created ${response.data.created.length} cards in Trello.`,
        );
      }
    } catch (err) {
      alert("Failed to sync with Trello.");
    }
  };

  // --- VIEWS ---
  if (currentView === "signup") {
    return (
      <div className="auth-container">
        <div className="auth-card signup-card">
          <div className="auth-brand">
            <Layout className="brand-icon" size={32} />
            <h2>Echo AI</h2>
            <p>The Quiet Observer.</p>
          </div>
          <form className="auth-form" onSubmit={handleSignup}>
            <h3>Create an account</h3>
            <div className="input-group">
              <label>Full Name</label>
              <div className="input-wrapper">
                <User size={18} />
                <input
                  type="text"
                  name="name"
                  placeholder="John Doe"
                  onChange={handleAuthChange}
                  required
                />
              </div>
            </div>
            <div className="input-group">
              <label>Email Address</label>
              <div className="input-wrapper">
                <Mail size={18} />
                <input
                  type="email"
                  name="email"
                  placeholder="john@company.com"
                  onChange={handleAuthChange}
                  required
                />
              </div>
            </div>
            <div className="input-group">
              <label>Password</label>
              <div className="input-wrapper">
                <Lock size={18} />
                <input
                  type="password"
                  name="password"
                  placeholder="••••••••"
                  onChange={handleAuthChange}
                  required
                />
              </div>
            </div>
            <button type="submit" className="btn primary-btn full-width">
              Create Account <ChevronRight size={16} />
            </button>
            <p className="auth-switch">
              Already have an account?{" "}
              <span onClick={() => setCurrentView("login")}>Log in</span>
            </p>
          </form>
        </div>
      </div>
    );
  }

  if (currentView === "login") {
    return (
      <div className="auth-container">
        <div className="auth-card login-card">
          <div className="auth-brand text-center">
            <Layout className="brand-icon" size={32} />
            <h2>Echo AI</h2>
            <p>The Quiet Observer.</p>
          </div>
          <form className="auth-form" onSubmit={handleLogin}>
            <div className="input-group">
              <label>Email Address</label>
              <div className="input-wrapper">
                <Mail size={18} />
                <input
                  type="email"
                  name="email"
                  placeholder="john@company.com"
                  onChange={handleAuthChange}
                  required
                />
              </div>
            </div>
            <div className="input-group">
              <label>Password</label>
              <div className="input-wrapper">
                <Lock size={18} />
                <input
                  type="password"
                  name="password"
                  placeholder="••••••••"
                  onChange={handleAuthChange}
                  required
                />
              </div>
            </div>
            <button type="submit" className="btn primary-btn full-width">
              Sign In <ChevronRight size={16} />
            </button>
            <p className="auth-switch text-center">
              New to Echo AI?{" "}
              <span onClick={() => setCurrentView("signup")}>
                Create Account
              </span>
            </p>
          </form>
        </div>
      </div>
    );
  }

  // Dashboard View
  return (
    <div className="dashboard-layout">
      {/* Sidebar */}
      <aside className="sidebar">
        <div className="sidebar-brand">
          <Layout size={24} className="text-blue" />
          <div>
            <h3>Echo AI</h3>
            <span>The Quiet Observer</span>
          </div>
        </div>

        <button className="btn new-meeting-btn">
          <Plus size={16} /> New Meeting
        </button>

        <nav className="sidebar-nav">
          <a href="#" className="active">
            <Mic size={18} /> Recorder
          </a>
          <a href="#">
            <History size={18} /> History
          </a>
          <a href="#">
            <Settings size={18} /> Integrations
          </a>
        </nav>

        <div className="sidebar-user">
          <div className="avatar">{user?.name?.charAt(0)}</div>
          <div className="user-info">
            <span className="name">{user?.name}</span>
            <span className="email">{user?.email}</span>
          </div>
          <button onClick={handleLogout} className="logout-btn">
            Log out
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <main className="main-content">
        <header className="main-header">
          <div className="status-indicator">
            <span className={`dot ${status}`}></span>
            {status === "recording"
              ? "Recording in progress..."
              : "Ready to record"}
          </div>
        </header>

        <div className="content-grid">
          {/* Recorder Section */}
          <div className="panel recorder-panel">
            <h3>Audio Feed</h3>
            <div className="visualizer-placeholder">
              {/* Decorative waveform bars based on your design */}
              {Array.from({ length: 40 }).map((_, i) => (
                <div
                  key={i}
                  className="bar"
                  style={{ height: `${Math.random() * 80 + 10}%` }}
                ></div>
              ))}
            </div>

            <div className="recorder-controls">
              {status !== "recording" ? (
                <button
                  className="btn control-btn play"
                  onClick={startRecording}
                >
                  <Mic size={24} />
                </button>
              ) : (
                <button
                  className="btn control-btn stop"
                  onClick={stopRecording}
                >
                  <Square size={24} />
                </button>
              )}
            </div>

            {mediaBlobUrl && status === "stopped" && (
              <div className="analyze-action">
                <audio src={mediaBlobUrl} controls className="audio-player" />
                <button
                  className="btn primary-btn full-width mt-4"
                  onClick={handleAnalyze}
                  disabled={loading}
                >
                  {loading ? (
                    <>
                      <Loader2 className="spin" /> Processing...
                    </>
                  ) : (
                    "Analyze Audio"
                  )}
                </button>
              </div>
            )}
          </div>

          {/* Results Section */}
          <div className="panel results-panel">
            {data ? (
              <div className="analysis-results">
                <div className="result-section">
                  <h3>🎯 Summary</h3>
                  <div className="card summary-card">
                    <p>{data.analysis.summary}</p>
                  </div>
                </div>

                <div className="result-section split">
                  <div className="transcript-area">
                    <h3>📝 Transcript</h3>
                    <div className="card scrollable">
                      <p>{data.transcript}</p>
                    </div>
                  </div>

                  <div className="tasks-area">
                    <div className="flex-between">
                      <h3>✅ Action Items</h3>
                      <button
                        className="btn trello-btn"
                        onClick={handleSyncTrello}
                      >
                        <Send size={14} /> Sync to Trello
                      </button>
                    </div>
                    <div className="task-list">
                      {data.analysis.tasks.map((task, index) => (
                        <div key={index} className="task-card">
                          <div className="task-head">
                            <strong>{task.title}</strong>
                            <span
                              className={`priority-dot ${task.priority.toLowerCase()}`}
                            ></span>
                          </div>
                          <p className="task-desc">{task.description}</p>
                          <span className="task-assignee">
                            👤 {task.assignee}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            ) : (
              <div className="empty-state">
                <Layout size={48} className="text-muted" />
                <p>
                  Record a meeting to see the live transcript and AI analysis
                  here.
                </p>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}

export default App;
