"use client";
import React, { useState, ChangeEvent, FormEvent } from "react";
import axios from "axios";
import styles from "./page.module.css";
import Header from "../components/header";
import Footer from "../components/footer";

interface Candidate {
  "Candidate Name": string;
  "Email Address": string;
  Result: string;
  Score: number;
  Probabilities: string;
  "Job Title": string;
  "Company/Client": string;
}

interface ApiResponse {
  json: Candidate[];
  csv?: string;
}

interface ErrorState {
  modelVersion: string;
  vectorizerVersion: string;
  jobDescription: string;
  jobTitle: string;
  companyName: string;
  uploadedFiles: string;
}

interface MessageState {
  type: "success" | "error";
  text: string;
}

export default function Home() {
  const [modelVersion, setModelVersion] = useState<string>("");
  const [vectorizerVersion, setVectorizerVersion] = useState<string>("");
  const [jobDescription, setJobDescription] = useState<string>("");
  const [jobTitle, setJobTitle] = useState<string>("");
  const [companyName, setCompanyName] = useState<string>("");
  const [uploadedFiles, setUploadedFiles] = useState<FileList | null>(null);
  const [response, setResponse] = useState<ApiResponse | null>(null);
  const [message, setMessage] = useState<MessageState | null>(null);
  const [showPopup, setShowPopup] = useState<boolean>(false);
  const [expandedCandidate, setExpandedCandidate] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [expandedCandidates, setExpandedCandidates] = useState<Record<string, boolean>>({});
  const [errors, setErrors] = useState<ErrorState>({
    modelVersion: "",
    vectorizerVersion: "",
    jobDescription: "",
    jobTitle: "",
    companyName: "",
    uploadedFiles: "",
  });

  // State for managing collapsed sections
  const [collapsedSections, setCollapsedSections] = useState({
    match: true,
    moderateMatch: true,
    notMatch: true,
  });


  const handleFileChange = (e: ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 200) {
      setErrors((prev) => ({ ...prev, uploadedFiles: "You can upload a maximum of 200 files." }));
    } else {
      setUploadedFiles(files);
      setErrors((prev) => ({ ...prev, uploadedFiles: "" }));
    }
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();

    const newErrors: Partial<ErrorState> = {};
    if (!modelVersion) newErrors.modelVersion = "Please select a model version.";
    if (!vectorizerVersion) newErrors.vectorizerVersion = "Please select a vectorizer version.";
    if (!jobDescription) newErrors.jobDescription = "Please enter the job description.";
    if (!jobTitle) newErrors.jobTitle = "Please enter the job title.";
    if (!companyName) newErrors.companyName = "Please enter the company/client name.";
    if (!uploadedFiles || uploadedFiles.length === 0) newErrors.uploadedFiles = "Please upload at least one resume.";

    if (Object.keys(newErrors).length > 0) {
      setErrors((prev) => ({ ...prev, ...newErrors }));
      return;
    }

    const formData = new FormData();
    formData.append("job_description", jobDescription);
    formData.append("job_title", jobTitle);
    formData.append("company_name", companyName);
    formData.append("classifier_version", modelVersion);
    formData.append("vectorizer_version", vectorizerVersion);

    if (uploadedFiles) {
      Array.from(uploadedFiles).forEach((file) => {
        formData.append("files", file);
      });
    }

    setLoading(true);

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || "";
      const result = await axios.post<ApiResponse>(apiUrl, formData);
      setResponse(result.data);
      setError(null)
    } catch (error) {
      console.error("Error submitting data:", error);
      setResponse(null)
      setShowPopup(true)
      // Extract error message
      if (axios.isAxiosError(error)) {
        setError(error.response?.data?.message || "An unknown error occurred.");
      } else {
        setError("An unexpected error occurred.");
      }
    } finally {
      setLoading(false);
    }
  };

  const closePopup = () => {
    setShowPopup(false);
  };

  const sendCsvToWebhook = async (csvData?: string) => {
    setLoading(true)
    const webhookUrl =
      "https://connect.pabbly.com/workflow/sendwebhookdata/IjU3NjUwNTY0MDYzMzA0MzU1MjY0NTUzNTUxMzEi_pc";

    try {
      const result = await axios.post(webhookUrl, { csv_data: csvData });

      if (result.status === 200) {
        setMessage({ type: "success", text: "CSV data sent to webhook successfully!" });
      } else {
        setMessage({ type: "error", text: `Failed to send CSV data to webhook. Status code: ${result.status}` });
      }
    } catch (error) {
      setMessage({ type: "error", text: `An error occurred: ${error}` });
    } finally {
      setShowPopup(true);
      setLoading(false)
    }
  };

  const toggleSection = (section: keyof typeof collapsedSections) => {
    setCollapsedSections(prev => ({
      ...prev,
      [section]: !prev[section]
    }));
  };

  const toggleCandidate = (candidateName: string) => {
    setExpandedCandidates(prev => ({
      ...prev,
      [candidateName]: !prev[candidateName]
    }));
  };

  // Assuming response is the result of an API call
  const match = Array.isArray(response?.json)
    ? response.json.filter((candidate: any) => candidate.Result === "Match")
    : [];

  const moderateMatch = Array.isArray(response?.json)
    ? response.json.filter((candidate: any) => candidate.Result === "Moderate Match")
    : [];

  const notMatch = Array.isArray(response?.json)
    ? response.json.filter((candidate: any) => candidate.Result === "Not Match")
    : [];


  return (
    <div className={styles.container}>
      <Header />
      <main className={styles.main}>
        <h1 className={styles.title}>Resume Matcher</h1>
        <form onSubmit={handleSubmit} className={styles.form}>
          {/* Form fields remain unchanged */}
          <label className={styles.label}>
            Select the model version:
            <select
              value={modelVersion}
              onChange={(e) => {
                setModelVersion(e.target.value);
                setErrors((prev) => ({ ...prev, modelVersion: "" }));
              }}
              className={styles.select}
            >
              <option value="">Select...</option>
              <option value="v0.001-07">v0.001-07</option>
              <option value="v0.001-06">v0.001-06</option>
              <option value="v0.001-05">v0.001-05</option>
              <option value="v0.001-04">v0.001-04</option>
              <option value="v0.001-03">v0.001-03</option>
              <option value="v0.001-01">v0.001-01</option>
            </select>
            {errors.modelVersion && <span className={styles.error}>{errors.modelVersion}</span>}
          </label>

          <label className={styles.label}>
            Select the vectorizer version:
            <select
              value={vectorizerVersion}
              onChange={(e) => {
                setVectorizerVersion(e.target.value);
                setErrors((prev) => ({ ...prev, vectorizerVersion: "" }));
              }}
              className={styles.select}
            >
              <option value="">Select...</option>
              <option value="v0.001-07">v0.001-07</option>
              <option value="v0.001-06">v0.001-06</option>
              <option value="v0.001-05">v0.001-05</option>
              <option value="v0.001-04">v0.001-04</option>
              <option value="v0.001-03">v0.001-03</option>
              <option value="v0.001-01">v0.001-01</option>
            </select>
            {errors.vectorizerVersion && <span className={styles.error}>{errors.vectorizerVersion}</span>}
          </label>

          <label className={styles.label}>
            Enter Job Description (JD):
            <textarea
              value={jobDescription}
              onChange={(e) => {
                setJobDescription(e.target.value);
                setErrors((prev) => ({ ...prev, jobDescription: "" }));
              }}
              className={styles.textarea}
            />
            {errors.jobDescription && <span className={styles.error}>{errors.jobDescription}</span>}
          </label>

          <label className={styles.label}>
            Enter Job Title:
            <input
              type="text"
              value={jobTitle}
              onChange={(e) => {
                setJobTitle(e.target.value);
                setErrors((prev) => ({ ...prev, jobTitle: "" }));
              }}
              className={styles.input}
            />
            {errors.jobTitle && <span className={styles.error}>{errors.jobTitle}</span>}
          </label>

          <label className={styles.label}>
            Enter Company/Client Name:
            <input
              type="text"
              value={companyName}
              onChange={(e) => {
                setCompanyName(e.target.value);
                setErrors((prev) => ({ ...prev, companyName: "" }));
              }}
              className={styles.input}
            />
            {errors.companyName && <span className={styles.error}>{errors.companyName}</span>}
          </label>

          <label className={styles.label}>
            Upload Resumes (PDF):
            <p style={{ fontSize: '12px', marginTop: '5px' }}>Note: limit is 200 PDFs</p>
            <input
              type="file"
              onChange={handleFileChange}
              accept="application/pdf"
              multiple
              className={styles.input}
            />
            {errors.uploadedFiles && <span className={styles.error}>{errors.uploadedFiles}</span>}
          </label>

          {loading && !response ? (
            <button className={`btn btn-primary ${styles.button}`} type="button" disabled>
              <span className="spinner-grow spinner-grow-sm" role="status" aria-hidden="true"></span>
              Loading...
            </button>
          ) : (
            <button type="submit" className={styles.button}>
              Submit
            </button>
          )}
        </form>
        {error && showPopup && (
          <div className={styles.popupOverlay}>
            <div className={styles.popupMessage}>
              <p>{error}</p>
              <button onClick={closePopup} className={styles.popupbutton}>
                Ok
              </button>
            </div>
          </div>
        )}

        {response && response.json && Array.isArray(response.json) && (
          <div>
            <div className={styles.buttons}>
              {response.csv && (
                <div className={styles.actionbutton}>
                  <a href={`data:file/csv;base64,${response.csv}`} download="resume_matches.csv">
                    Download Result as CSV
                  </a>
                </div>
              )}
              {loading && response ? (
                <button className={`btn btn-primary ${styles.actionbutton}`} type="button" disabled>
                  <span className="spinner-grow spinner-grow-sm" role="status" aria-hidden="true"></span>
                  Sending...
                </button>
              ) : (
                <button onClick={() => sendCsvToWebhook(response.csv)} className={styles.actionbutton}>
                  Send to Webhook
                </button>
              )}

            </div>

            {message && showPopup && (
              <div className={styles.popupOverlay}>
                <div className={styles.popupMessage}>
                  <p>{message?.text}</p>
                  <button onClick={closePopup} className={styles.popupbutton}>
                    Ok
                  </button>
                </div>
              </div>
            )}

            <div className={styles.response}>
              <h2>Response from API:</h2>

              {/* Match Section */}
              <div>
                <h3 onClick={() => toggleSection('match')} className={styles.collapseHeader}>
                  {collapsedSections.match ? "▲ Match" : "▼ Match"}
                </h3>
                {!collapsedSections.match && (
                  match?.length > 0 ? (
                    match.map((candidate, index) => (
                      <div key={index} className={styles.candidate}>
                        <p
                          onClick={() => toggleCandidate(candidate["Candidate Name"])}
                          className={styles.candidateName}
                        >
                          {expandedCandidates[candidate["Candidate Name"]] ? "▼ " + candidate["Candidate Name"] : "▲ " + candidate["Candidate Name"]}
                        </p>

                        {expandedCandidates[candidate["Candidate Name"]] && (
                          <div className={styles.candidateDetails}>
                            <p><strong>Result:</strong> {candidate["Result"]}</p>
                            <p><strong>Score:</strong> {candidate["Score"]}</p>
                            <p><strong>Probabilities:</strong> {candidate["Probabilities"]}</p>
                            <p><strong>Job Title:</strong> {candidate["Job Title"]}</p>
                            <p><strong>Company Name:</strong> {candidate["Company/Client"]}</p>
                          </div>
                        )}
                      </div>
                    ))
                  ) : (
                    <div className={styles.candidate}>
                      <p>No matches available in this section.</p>
                    </div>
                  )
                )}
              </div>

              {/* Moderate Match Section */}
              <div>
                <h3 onClick={() => toggleSection('moderateMatch')} className={styles.collapseHeader}>
                  {collapsedSections.moderateMatch ? "▲ Moderate Match" : "▼ Moderate Match"}
                </h3>
                {!collapsedSections.moderateMatch && (
                  moderateMatch?.length > 0 ? (
                    moderateMatch.map((candidate, index) => (
                      <div key={index} className={styles.candidate}>
                        <p
                          onClick={() => toggleCandidate(candidate["Candidate Name"])}
                          className={styles.candidateName}
                        >
                          {expandedCandidates[candidate["Candidate Name"]] ? "▼ " + candidate["Candidate Name"] : "▲ " + candidate["Candidate Name"]}
                        </p>

                        {expandedCandidates[candidate["Candidate Name"]] && (
                          <div className={styles.candidateDetails}>
                            <p><strong>Result:</strong> {candidate["Result"]}</p>
                            <p><strong>Score:</strong> {candidate["Score"]}</p>
                            <p><strong>Probabilities:</strong> {candidate["Probabilities"]}</p>
                            <p><strong>Job Title:</strong> {candidate["Job Title"]}</p>
                            <p><strong>Company Name:</strong> {candidate["Company/Client"]}</p>
                          </div>
                        )}
                      </div>
                    ))
                  ) : (
                    <div className={styles.candidate}>
                      <p>No matches available in this section.</p>
                    </div>
                  )
                )}
              </div>

              {/* Not Match Section */}
              <div>
                <h3 onClick={() => toggleSection('notMatch')} className={styles.collapseHeader}>
                  {collapsedSections.notMatch ? "▲ Not Match" : "▼ Not Match"}
                </h3>
                {!collapsedSections.notMatch && (
                  notMatch?.length > 0 ? (
                    notMatch.map((candidate, index) => (
                      <div key={index} className={styles.candidate}>
                        <p
                          onClick={() => toggleCandidate(candidate["Candidate Name"])}
                          className={styles.candidateName}
                        >
                          {expandedCandidates[candidate["Candidate Name"]] ? "▼ " + candidate["Candidate Name"] : "▲ " + candidate["Candidate Name"]}
                        </p>

                        {expandedCandidates[candidate["Candidate Name"]] && (
                          <div className={styles.candidateDetails}>
                            <p><strong>Result:</strong> {candidate["Result"]}</p>
                            <p><strong>Score:</strong> {candidate["Score"]}</p>
                            <p><strong>Probabilities:</strong> {candidate["Probabilities"]}</p>
                            <p><strong>Job Title:</strong> {candidate["Job Title"]}</p>
                            <p><strong>Company Name:</strong> {candidate["Company/Client"]}</p>
                          </div>
                        )}
                      </div>
                    ))
                  ) : (
                    <div className={styles.candidate}>
                      <p>No matches available in this section.</p>
                    </div>
                  )
                )}
              </div>
            </div>
          </div>
        )}
      </main>
      <Footer />
    </div>
  );
}
