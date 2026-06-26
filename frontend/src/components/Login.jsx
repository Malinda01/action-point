import { useState } from "react";
import axios from "axios";
import { Layout, Mail, Lock, ChevronRight } from "lucide-react";

export default function Login({ onSwitchView, onLoginSuccess }) {
  const [authForm, setAuthForm] = useState({ email: "", password: "" });

  const handleAuthChange = (e) => {
    setAuthForm({ ...authForm, [e.target.name]: e.target.value });
  };

  const handleLogin = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.post("http://localhost:5000/api/login", {
        email: authForm.email,
        password: authForm.password,
      });
      onLoginSuccess(response.data.user);
    } catch (err) {
      alert(err.response?.data?.error || "Login failed");
    }
  };

  return (
    // UI starts here
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
            <span onClick={() => onSwitchView("signup")}>Create Account</span>
          </p>
        </form>
      </div>
    </div>
  );
}
