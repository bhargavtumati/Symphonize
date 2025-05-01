import type React from "react";
import { useState, useEffect, useCallback } from "react";
import { Button } from "@/components/ui/button";
import EmailTemplates from "./email-templates";
import EmailVariables from "./email-variables";
import { ScrollArea } from "@/components/ui/scroll-area";
import ComposeMail from "./compose-mail";
import { Loader2, X } from "lucide-react";
import {
  JobCardProps,
  PreferenceApiCandidateRespo,
  RecruiterResponse,
  Template,
} from "../types/model";
import { apiService } from "../api/service";
import EmailSentToast from "./EmailSentToast";
import { getCurrentUserEmail } from "./AuthProvider";
import { cleanHTMLContent } from "../utils/resume-name-extraction";
import { useRouter } from "next/navigation";
import { cn } from "@/lib/utils";
import Image from "next/image";

interface SentEmailProps {
  className?: string;
  icon: React.ReactNode;
  iconClassName?: string;
  text: string;
  onVerifyEmailService: boolean;
  selectedCandidates: string[];
  selectedCandidatesDetails: PreferenceApiCandidateRespo[];
  onScheduleClick: () => Promise<{
    emailServiceStatus: boolean;
    indidualEmailServiceStatus: boolean;
  } | null>;
  jobDetails: JobCardProps | null;
  originalStages: {
    uuid: string;
    name: string;
  }[];
  toggleCandidateSelection?: (candidateIds: string[], candidateDetails: PreferenceApiCandidateRespo[]) => void;
}

const SentEmail: React.FC<SentEmailProps> = ({
  className,
  icon,
  iconClassName,
  text,
  selectedCandidates,
  onScheduleClick,
  selectedCandidatesDetails,
  jobDetails,
  onVerifyEmailService,
  originalStages,
  toggleCandidateSelection
}) => {
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [selectedTemplate, setSelectedTemplate] = useState<Template>();
  const [editorInstance, setEditorInstance] = useState<any>(null);
  const [candidateStage, setCandidateStage] = useState<string>("");
  const [templates, setTemplates] = useState<Template[]>([]);
  const [newTemplateName, setNewTemplateName] = useState("");
  const [allSameStage, setAllSameStage] = useState<boolean>(false);
  const [isDifferentStages, setIsDifferentStages] = useState<boolean>(false);
  const [attachedFiles, setAttachedFiles] = useState<File[]>([]);
  const [isMailSent, setIsMailSent] = useState<boolean>(false);
  const [emailServiceStatus, setEmailServiceStatus] = useState(true);
  const [indidualEmailServiceStatus, setIndidualEmailServiceStatus] =
    useState(true);
  const threeHrsFromNow = new Date();
  threeHrsFromNow.setHours(threeHrsFromNow.getHours() + 3);
  const [sendToAllData, setSendToAllData] = useState<{
    from_email: string;
    to_email: string[];
    subject: string;
    body: string;
    job_code: string;
  }>({
    from_email: "careers@tekworks.ai",
    to_email: [],
    subject: "",
    body: "",
    job_code: "",
  });

  const [showCustomInput, setShowCustomInput] = useState(false);
  const [recruiterData, setRecruiterData] = useState<RecruiterResponse>();
  const router = useRouter();
  useEffect(() => {
    const fetchRecruiterData = async () => {
      try {
        const recruiterResponse = await apiService("/recruiter", "GET", null);
        setRecruiterData(recruiterResponse);
      } catch (error) {
        console.error("Error fetching recruiter data:", error);
      }
    };

    fetchRecruiterData();
  }, []);

  useEffect(() => {
    setSendToAllData((prevData) => ({
      ...prevData,
      to_email:
        selectedCandidatesDetails?.flatMap(
          (candidate) => candidate.email || []
        ) || [],
    }));
  }, [selectedCandidatesDetails]);

  useEffect(() => {
    if (isMailSent) {
      const timer = setTimeout(() => {
        setIsMailSent(false); // Hide message after 2 seconds
      }, 3000);
      return () => clearTimeout(timer); // Cleanup timer on unmount
    }
  }, [isMailSent]);

  useEffect(() => {
    if (selectedCandidatesDetails.length === 0) return;

    const stageNames = selectedCandidatesDetails.map((candidate) => {
      const stage = originalStages.find((s) => s.uuid === candidate.stage_uuid);
      return stage ? stage.name : "Unknown Stage";
    });

    // Check if all stages are the same
    setAllSameStage(stageNames.every((stage) => stage === stageNames[0]));

    setCandidateStage(
      stageNames.every((stage) => stage === stageNames[0])
        ? stageNames[0]
        : "Shortlisted"
    );
  }, [selectedCandidatesDetails, originalStages]);

  useEffect(() => {
    if (isDialogOpen) {
      document.body.classList.add("overflow-hidden");
    } else {
      document.body.classList.remove("overflow-hidden");
    }

    return () => {
      document.body.classList.remove("overflow-hidden");
    };
  }, [isDialogOpen]);

  const handleButtonClick = () => {
    if (selectedCandidates.length > 0) {
      setIsDialogOpen(true);
    }
    handleScheduleClick();
  };
  const handleScheduleClick = async () => {
    const result = await onScheduleClick();
    if (result) {
      setEmailServiceStatus(result.emailServiceStatus);
      setIndidualEmailServiceStatus(result.indidualEmailServiceStatus);
    }
  };

  const handleClose = () => {
    setIsDialogOpen(false);
    // Reset selected candidates when dialog is closed
    if (selectedCandidates.length > 0 && toggleCandidateSelection) {
      toggleCandidateSelection([], []);
    }
  };

  const handleEditorInit = useCallback((editor: any) => {
    setEditorInstance(editor);
  }, []);

  const handleVariableClick = (variable: string) => {
    if (editorInstance) {
      editorInstance.insertContent(variable);
    }
  };

  const handleIsDifferentStages = () => {
    setIsDifferentStages(false);
  };

  const handleSendToAllSubmit = useCallback(async () => {
    const formData = new FormData();

    Object.entries(sendToAllData).forEach(([key, value]) => {
      if (key === "job_code") {
        formData.append(key, jobDetails?.job?.code || "");
      } else if (typeof value === "string") {
        if (key === "body") {
          // Remove anchor tags and trim the content
          let cleanedValue = value;

          // Replace {{TomorrowDate}} with next day's date
          cleanedValue = cleanedValue.replace(/{{TomorrowDate}}/g, () => {
            const tomorrow = new Date();
            tomorrow.setDate(tomorrow.getDate() + 1); // Add 1 day
            return tomorrow.toISOString().split("T")[0]; // Format as YYYY-MM-DD
          });

          // Replace {{3HrsFromNow}} with time 3 hours ahead
          cleanedValue = cleanedValue.replace(/{{3HrsFromNow}}/g, () => {
            const now = new Date();
            now.setHours(now.getHours() + 3); // Add 3 hours
            const hours = String(now.getHours()).padStart(2, "0"); // Ensure 2-digit hours
            const minutes = String(now.getMinutes()).padStart(2, "0"); // Ensure 2-digit minutes
            return `${hours}:${minutes}`; // Format as HH:mm
          });

          //Remove attached file names from the editor body
          attachedFiles.forEach((file) => {
            const fileName = file.name;

            // Escape special characters in filename to prevent regex issues
            const escapedFileName = fileName.replace(/[-\/\\^$*+?.()|[\]{}]/g, "\\$&");
    
            // Remove entire <a> tag if it contains the file name
            cleanedValue = cleanHTMLContent(cleanedValue, escapedFileName);
        });

          formData.append(key, cleanedValue);
        } else {
          formData.append(key, value);
        }
      } else if (Array.isArray(value)) {
        formData.append(key, value.join(","));
      }
    });

    attachedFiles.forEach((file) => {
      formData.append(`files`, file);
    });

    try {
      const response = await apiService(
        "/email/send-email",
        "POST",
        formData,
        true
      );
      setIsMailSent(true);
      if (!response.ok) {
        throw new Error(`Error: ${response.status} ${response.statusText}`);
      }
      if (toggleCandidateSelection) {
        toggleCandidateSelection([], []);
      }
    } catch (error) {
      console.error("Failed to send data:", error);
    }
    setIsDifferentStages(false);
    setIsDialogOpen(false);
    setAttachedFiles([]);
  }, [sendToAllData, jobDetails, attachedFiles]);

  const handleCustomTemplateConfirm = useCallback(async () => {
    if (newTemplateName.trim() || selectedTemplate?.uuid) {
      try {
        var template;
        if (newTemplateName.trim()) {
          const newTemplate: Template = {
            uuid: "",
            name: newTemplateName.trim(),
            body: sendToAllData.body,
            subject: sendToAllData.subject,
            default: false,
          };
          template = newTemplate;
        } else {
          const oldTemplate: Template = {
            uuid: selectedTemplate?.uuid,
            name: selectedTemplate?.name,
            body: sendToAllData.body,
            subject: sendToAllData.subject,
            default: false,
            is_edited: true,
          };
          template = oldTemplate;
        }

        const userEmail = (await getCurrentUserEmail()) as string;
        const CompanyDomain = userEmail.split("@")[1];
        const response = await apiService(
          `/template/update?domain=${CompanyDomain}`,
          "PATCH",
          template
        );
        setTemplates(response.data.template_data.templates);

        setNewTemplateName("");
        setShowCustomInput(false);
      } catch (err) {
        console.error("Error saving template:", err);
      }
    }
    setIsDifferentStages(false);
  }, [newTemplateName, sendToAllData, setShowCustomInput]);

  const handleSenderMails = () => {
    setEmailServiceStatus(true);
    setIndidualEmailServiceStatus(true);
    setSendToAllData((prev: any) => ({
      ...prev,
      sender: process.env.NEXT_PUBLIC_EMAIL_SERVICE_ACCOUNT,
    }));
  };

  const navigateEmailIntegrationPage = () => {
    router.push("/integrations");
  };
  return (
    <div>
      {/* Button to Open Dialog */}
      <Button
        className={`${className}`}
        variant="none"
        disabled={
          selectedCandidates.length === 0 || jobDetails?.job.status === "CLOSED"
        }
        onClick={handleButtonClick}
      >
        <span className={`${iconClassName}`}>{icon}</span>
        <span>{text}</span>
      </Button>

      {/* Manual Dialog Box */}
      {isDialogOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex justify-center items-center z-50">
          <div
            className={cn(
              "relative bg-white rounded-lg shadow-lg max-h-[95vh] overflow-hidden",
              emailServiceStatus ? "sm:w-[900px]": "w-[564px]"
            )}
          >
            {/* Close Button */}
            <Button
              variant="none"
              className="absolute top-1 right-1 text-gray-600 hover:text-black cursor-pointer z-50"
              onClick={handleClose}
            >
              <X size={24} />
            </Button>
            {onVerifyEmailService ? (
              <div className="flex flex-col items-center justify-center h-64 max-w-[564px]">
                <Loader2 className="h-8 w-8 animate-spin text-primary" />
                <p className="mt-4 text-sm text-gray-500">
                  Verifying email service...
                </p>
              </div>
            ) : !emailServiceStatus || !indidualEmailServiceStatus ? (
              <div className="flex flex-col items-center justify-center space-y-4 py-16 px-8">
                {!emailServiceStatus && (
                  <>
                    {" "}
                    <Image
                      src={"/images/email-integration.svg"}
                      alt={""}
                      height={100}
                      width={100}
                    />
                    <h1 className="text-xl font-bold text-slate-800">
                      Email Not Integrated
                    </h1>
                    <p className="text-base text-slate-500 font-medium text-center">
                      You haven{"'"}t integrated your company email yet. The
                      email would be persimmon email Id, integrate your
                      companies email Id for professional experience to your
                      receipts.
                    </p>
                    {/* <a
                        onClick={handleSenderMails}
                        className="underline text-primary text-base font-medium cursor-pointer justify-center items-center p-2"
                      >
                        Continue with persimmon email (0/100)
                      </a> */}
                    <Button onClick={navigateEmailIntegrationPage}>
                      Integrate email
                    </Button>
                    <a onClick={handleSenderMails} className="text-primary text-sm font-medium cursor-pointer">
                      Continue with persimmon email (0/100)
                    </a>
                  </>
                )}

                {!indidualEmailServiceStatus && (
                  <p className="text-xl text-slate-800 p-8 text-center">
                    Your email is not found within any integrated email service.
                    Please contact your administrator.
                  </p>
                )}
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-[220px_1fr] h-[calc(95vh-4rem)]">
                {/* Sidebar */}
                <div className="flex flex-col border-b md:border-r md:border-b-0">
                  <div className="h-[calc(47.5vh-2rem)] overflow-hidden">
                    <EmailTemplates
                      setSelectedTemplate={setSelectedTemplate}
                      apiResponseTemplateName={candidateStage}
                      sendToAllData={sendToAllData}
                      setSendToAllData={setSendToAllData}
                      setShowCustomInput={setShowCustomInput}
                      showCustomInput={showCustomInput}
                      handleCustomTemplateConfirm={handleCustomTemplateConfirm}
                      templates={templates}
                      setTemplates={setTemplates}
                      setNewTemplateName={setNewTemplateName}
                      newTemplateName={newTemplateName}
                    />
                  </div>
                  <div className="h-[calc(47.5vh-2rem)] overflow-hidden">
                    <EmailVariables onVariableClick={handleVariableClick} />
                  </div>
                </div>

                {/* Main Content */}
                <div className="flex flex-col">
                  <ScrollArea className="flex-grow h-[calc(95vh-8rem)]">
                    <div className="py-6 pl-6 pr-10">
                      <ComposeMail
                        selectedTemplate={selectedTemplate}
                        onEditorInit={handleEditorInit}
                        sendToAllData={sendToAllData}
                        setSendToAllData={setSendToAllData}
                        setShowCustomInput={setShowCustomInput}
                        showCustomInput={showCustomInput}
                        selectedCandidatesDetails={selectedCandidatesDetails}
                        jobDetails={jobDetails}
                        handleCustomTemplateConfirm={
                          handleCustomTemplateConfirm
                        }
                        allSameStage={allSameStage}
                        setIsDifferentStages={setIsDifferentStages}
                        handleSendToAllSubmit={handleSendToAllSubmit}
                        setAttachedFiles={setAttachedFiles}
                        setIsDialogOpen={setIsDialogOpen}
                        setIsMailSent={setIsMailSent}
                        attachedFiles={attachedFiles}
                        threeHrsFromNow={threeHrsFromNow}
                        recruiterData={recruiterData}
                      />
                    </div>
                  </ScrollArea>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {isDifferentStages && (
        <div className="fixed inset-0 bg-black bg-opacity-60 flex justify-center items-center z-50">
          <div className="relative bg-white rounded-lg shadow-lg w-[450px] max-h-[80vh] p-6">
            {/* Close Button */}
            <Button
              variant="none"
              className="absolute top-1 right-1 text-gray-600 hover:text-black cursor-pointer z-50"
              onClick={handleIsDifferentStages}
            >
              <X size={24} />
            </Button>

            <p>Applicants are in different stages. Continue?</p>

            <div className="flex justify-end gap-2">
              <Button className="mt-4" onClick={handleSendToAllSubmit}>
                Yes
              </Button>
              <Button className="mt-4" onClick={handleIsDifferentStages}>
                No
              </Button>
            </div>
          </div>
        </div>
      )}
      <EmailSentToast
        emailSent={isMailSent}
        variant="default"
        title="Success"
        description="Email has been sent successfully"
        duration={3000}
      />
    </div>
  );
};

export default SentEmail;
