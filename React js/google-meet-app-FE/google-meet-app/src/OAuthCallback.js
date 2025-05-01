import React, { useEffect } from "react";
import { useNavigate } from "react-router-dom";

const OAuthCallback = () => {
  const navigate = useNavigate();

  useEffect(() => {
    const hash = window.location.hash.substring(1);
    const params = new URLSearchParams(hash);
    console.log("Params:", params);
    const token = params.get("access_token");

    if (token) {
      localStorage.setItem("google_oauth_token", token);
      navigate("/");
    } else {
      console.error("No token found in URL");
    }
  }, [navigate]);

  return <p>Processing OAuth authentication...</p>;
};

export default OAuthCallback;