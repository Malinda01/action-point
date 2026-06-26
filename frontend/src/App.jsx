import { useState } from "react";
import Login from "./components/Login";
import Signup from "./components/Signup";
import Dashboard from "./components/Dashboard";
import "./App.css"; // Keep your existing App.css file

function App() {
  const [currentView, setCurrentView] = useState("login"); // 'login', 'signup', 'dashboard'
  const [user, setUser] = useState(null);

  const handleLoginSuccess = (userData) => {
    setUser(userData);
    setCurrentView("dashboard");
  };

  const handleLogout = () => {
    setUser(null);
    setCurrentView("login");
  };

  // Conditionally render the correct component based on state
  if (currentView === "signup") {
    return <Signup onSwitchView={setCurrentView} />;
  }

  if (currentView === "login") {
    return (
      <Login
        onSwitchView={setCurrentView}
        onLoginSuccess={handleLoginSuccess}
      />
    );
  }

  return <Dashboard user={user} onLogout={handleLogout} />;
}

export default App;
