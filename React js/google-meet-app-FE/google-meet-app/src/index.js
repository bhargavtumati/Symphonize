import React from "react";
import ReactDOM from "react-dom/client";  // Import from 'react-dom/client'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import App from "./App";
import OAuthCallback from "./OAuthCallback";

const root = ReactDOM.createRoot(document.getElementById("root")); // Create the root using createRoot
root.render(
  <Router>
    <Routes>
      <Route path="/" element={<App />} />
      <Route path="/oauth-callback" element={<OAuthCallback />} />
    </Routes>
  </Router>
);
