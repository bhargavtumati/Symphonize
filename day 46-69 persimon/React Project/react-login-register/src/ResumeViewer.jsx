import React from "react";

const ResumeViewer = () => {
  const pdfUrl = "paste-your-url";



  
    const viewerUrl = `https://docs.google.com/viewer?url=${encodeURIComponent(pdfUrl)}&embedded=true`;
    
    
      return (
        <div style={styles.container}>
          <iframe
            src={viewerUrl}
            width="600px"
            height="600px"
            style={styles.iframe}
            title="Resume Viewer"
          ></iframe>
        </div>
      );
    };
    
    const styles = {
      container: {
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        height: "100vh", // Full viewport height
        backgroundColor: "#f5f5f5", // Optional background color
      },
      iframe: {
        border: "1px solid #ccc", // Optional border
        borderRadius: "8px", // Optional rounded corners
      },
    };
    
    export default ResumeViewer;
    
  
  
  
