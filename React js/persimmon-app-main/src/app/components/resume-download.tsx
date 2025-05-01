"use client";

import { useState } from "react";

interface ResumeDownloadLinkProps {
  applicantId: string | undefined;
}

export function ResumeDownloadLink({ applicantId }: ResumeDownloadLinkProps) {
  const [isDownloading, setIsDownloading] = useState(false);

  const handleDownload = async (e: React.MouseEvent<HTMLAnchorElement>) => {
    e.preventDefault();
    setIsDownloading(true);

    try {
      const apiUrl = `${process.env.NEXT_PUBLIC_API}/api/v1/applicants/${applicantId}/resume?action=download`
      const idToken = localStorage.getItem("firebaseIdToken");
      const headers = {
        ...(idToken && { Authorization: `Bearer ${idToken}` }),
      };

      const response = await fetch(apiUrl,{
      method:"GET",
      headers
      })

      if (!response.ok) {
        throw new Error("Failed to download resume");
      }

      // Get the filename from the Content-Disposition header
      
      const contentDisposition = response.headers.get("Content-Disposition");
  
      const filenameMatch =
        contentDisposition && contentDisposition.match(/filename="?(.+)"?/);
    
      let filename;
      if (filenameMatch) {
        // Remove the trailing slash and quotation mark if present
        filename = filenameMatch[1].replace(/["\\/]+$/, "");
      }

      // Create a Blob from the response
      const blob = await response.blob();

      // Create a temporary URL for the Blob
      const url = URL.createObjectURL(blob);

      // Create a temporary anchor element and trigger the download
      const link = document.createElement("a");
      link.href = url;
      link.download = filename ? filename : "";
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);

      // Clean up the temporary URL
      URL.revokeObjectURL(url);
    } catch (error) {
      console.error("Error downloading resume:", error);
      // Handle error (e.g., show an error message to the user)
    } finally {
      setIsDownloading(false);
    }
  };

  return (
    <a
      href="#"
      onClick={handleDownload}
      className="text-primary underline cursor-pointer"
    >
      {isDownloading ? "Downloading..." : "Download"}
    </a>
  );
}
