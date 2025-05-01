"use client";

import { useState, useEffect } from "react";
import { Card } from "@/components/ui/card";
import { ResumeDownloadLink } from "./resume-download";
import { Applicant } from "../types/applicants";
interface ResumesProps {
  applicantData: Applicant | undefined;
}

export function Resume({ applicantData }: ResumesProps) {
  const [pdfUrl, setPdfUrl] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchPdfUrl = async () => {
      const idToken = localStorage.getItem("firebaseIdToken");
      const headers = {
        ...(idToken && { Authorization: `Bearer ${idToken}` }),
      };

      try {
        const response = await fetch(
          `${process.env.NEXT_PUBLIC_API}/api/v1/applicants/${applicantData?.uuid}/resume?action=view`,
          {
            method: "GET",
            headers,
          }
        );
        if (!response.ok) {
          throw new Error("Failed to fetch PDF");
        }
        const blob = await response.blob();
        const url = URL.createObjectURL(blob);
        setPdfUrl(url);
      } catch (err) {
        setError("Failed to load PDF");
        console.error(err);
      } finally {
        setIsLoading(false);
      }
    };

    fetchPdfUrl();

    return () => {
      if (pdfUrl) {
        URL.revokeObjectURL(pdfUrl);
      }
    };
  }, []);

  return (
    <Card className="p-6">
      <div className="flex justify-between items-center">
        <h3 className="text-lg font-semibold mb-4">Resume</h3>
        <ResumeDownloadLink applicantId={applicantData?.uuid} />
      </div>

      {isLoading ? (
        <p className="text-muted-foreground">Loading resume...</p>
      ) : error ? (
        <p className="text-red-500">{error}</p>
      ) : pdfUrl ? (
        <div className="w-full h-[600px] overflow-hidden">
          <embed
            src={pdfUrl}
            type="application/pdf"
            width="100%"
            height="100%"
            className="w-full h-full"
          />
        </div>
      ) : (
        <p className="text-muted-foreground">No resume available.</p>
      )}
    </Card>
  );
}
