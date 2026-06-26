import { useState } from "react";
import axios from "axios";
import { Layout, User, Mail, Lock, ChevronRight } from "lucide-react";

export default function Signup({ onSwitchView }) {
  const [authForm, setAuthForm] = useState({
    name: "",
    email: "",
    password: "",
  });

  const handleAuthChange = (e) => {
    setAuthForm({ ...authForm, [e.target.name]: e.target.value });
  };

  const handleSignup = async (e) => {
    e.preventDefault();
    try {
      await axios.post("http://localhost:5000/api/signup", authForm);
      alert("Signup successful! Please login.");
      onSwitchView("login");
    } catch (err) {
      alert(err.response?.data?.error || "Signup failed");
    }
  };

  return (
    // UI starts here
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
            <span onClick={() => onSwitchView("login")}>Log in</span>
          </p>
        </form>
      </div>
    </div>
  );
}
