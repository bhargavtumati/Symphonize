import React, { useState } from "react";
import axios from "axios";

const CLIENT_ID = "793571778940-361uq4isbu25oh0on9rci3fpieb6ektn.apps.googleusercontent.com";
//const REDIRECT_URI = "http://localhost:3000/oauth-callback";
const REDIRECT_URI = "http://localhost:3000/integrations/google-meet"
const SCOPES = "https://www.googleapis.com/auth/calendar";



const App = () => {
  const [token, setToken] = useState(null);
  const [meetingLink, setMeetingLink] = useState("");

  const loginWithGoogle = () => {
    const authUrl = `https://accounts.google.com/o/oauth2/auth?client_id=${CLIENT_ID}&redirect_uri=${REDIRECT_URI}&response_type=code&scope=${SCOPES}&access_type=offline&prompt=consent`;
    window.location.href = authUrl;
  };

  const createMeeting = async () => {
    if (!token) {
      alert("Please authenticate first!");
      return;
    }

    const attendees = ["user1@example.com", "user2@example.com"]; // Example participants

    try {
      const response = await axios.post("http://localhost:8000/create_meeting", {
        token,
        attendees
      });

      setMeetingLink(response.data.meeting_link);
      alert("Meeting created! Check your Google Calendar.");
    } catch (error) {
      console.error("Error creating meeting:", error);
    }
  };

  return (
    <div style={{ textAlign: "center", marginTop: "50px" }}>
      <h1>Google Meet Scheduler</h1>
      <button onClick={loginWithGoogle}>Sign in with Google</button>
      <button onClick={createMeeting} disabled={!token}>Create Google Meet</button>

      {meetingLink && (
        <p>
          Meeting Link: <a href={meetingLink} target="_blank" rel="noopener noreferrer">{meetingLink}</a>
        </p>
      )}
    </div>
  );
};

export default App;