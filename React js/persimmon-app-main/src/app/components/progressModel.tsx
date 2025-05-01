"use client";

import type React from "react";
import { useState, useEffect, useRef } from "react";
import { FaCheckCircle } from "react-icons/fa";
import SuccessAnimation from "./successAnimation";
import Image from "next/image";
import AlertDialogWrapper from "../components/alertPopup";
import { useUpload } from "./uploadContext";
import { Minus, X } from "lucide-react";
import type { FileData } from "../types";
import { auth } from "../components/firebaseConfig";
import { toast } from "@/components/hooks/use-toast";
import { apiService } from "../api/service";
import { faL } from "@fortawesome/free-solid-svg-icons";
import { extractFilenames } from "@/app/components/resume-name-extraction";
import Draggable from "react-draggable";
interface ProgressModalProps {
  initialFiles: FileData[];
  onClose: () => void;
  onMinimize: () => void;
  isMinimized: boolean;
  onMaximize: () => void;
}

const ProgressModal: React.FC<ProgressModalProps> = ({
  initialFiles = [],
  onClose,
  onMinimize,
  isMinimized,
  onMaximize,
}) => {
  const { files, setFiles } = useUpload();
  const [isImportEnabled, setIsImportEnabled] = useState<boolean>(false);
  const [loader, setLoader] = useState<boolean>(false);
  const [confirmation, setConfirmation] = useState<boolean>(false);
  const [isImporting, setIsImporting] = useState<boolean>(false);
  const abortControllerRef = useRef<AbortController | null>(null);
  const hasAutoMaximizedRef = useRef(false);
  const [failedResumes, setFailedResumes] = useState([]);
  const [duplicateResumes, setDuplicateResumes] = useState<string[]>([]);
  const [retry, setRetry] = useState<boolean>(false);
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const { setApplicantCount } = useUpload();
  const [totalResumes, setTotalResumes] = useState(0);
  const [shouldContinueChecking, setShouldContinueChecking] = useState(true);
  const [modalState, setModalState] = useState<{
    type: "delete" | "cancel" | null;
    index?: number;
  }>({ type: null });
  const fileInputRef = useRef<HTMLInputElement>(null);

  const truncateFileName = (name: string) => {
    const truncateLength = Math.ceil(name.length * 0.2); // Calculate 20% of the name length
    return name.slice(0, truncateLength) + "...";
  };

  const handleAddFiles = (event: React.ChangeEvent<HTMLInputElement>) => {
    function getFileType(fileName: string): "pdf" | "docx" {
      return fileName.toLowerCase().endsWith(".pdf") ? "pdf" : "docx";
    }
    const newFiles: FileData[] = Array.from(event.target.files || [])
      .filter((file) => /(\.pdf|\.docx)$/i.test(file.name))
      .map((file) => ({
        name: file.name,
        size: (file.size / 1024).toFixed(2),
        progress: 0,
        file,
        type: getFileType(file.name),
      }));

    setFiles((prevFiles) => {
      const updatedFiles = [...prevFiles];
      newFiles.forEach((newFile) => {
        const existingFileIndex = updatedFiles.findIndex(
          (f) => f.name === newFile.name
        );
        if (existingFileIndex !== -1) {
          updatedFiles[existingFileIndex] = newFile;
        } else {
          updatedFiles.push(newFile);
        }
      });
      return updatedFiles;
    });

    startUpload(newFiles);

    // Reset the file input
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  const cancelModelPopup = () => {
    if (isImporting) {
      setModalState({ type: "cancel" });
    } else {
      setModalState({ type: "cancel" });
    }
  };
  const cancelImport = () => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
    setIsImporting(false);
    setLoader(false);
    onClose();
  };

  const startUpload = (fileList: FileData[]) => {
    fileList.forEach((file) => {
      const interval = setInterval(() => {
        setFiles((prevFiles) => {
          const updatedFiles = prevFiles.map((f) => {
            if (f.name === file.name && f.progress < 100) {
              return { ...f, progress: f.progress + 10 };
            }
            return f;
          });

          if (updatedFiles.every((f) => f.progress === 100)) {
            clearInterval(interval);
          }

          return updatedFiles;
        });
      }, 500);
    });
  };

  useEffect(() => {
    if (initialFiles.length > 0) {
      startUpload(initialFiles);
    }
  }, [initialFiles, startUpload]);

  useEffect(() => {
    const allFilesUploaded = files.every((file) => file.progress === 100);
    const shouldEnableImport =
      allFilesUploaded &&
      duplicateResumes.length === 0 &&
      failedResumes.length === 0;
    setIsImportEnabled(shouldEnableImport);
    if (files.length === 0) {
      setIsImportEnabled(false);
    }
  }, [files, duplicateResumes, failedResumes]);

  const calculateTotalProgress = () => {
    if (files.length === 0) return 0;
    const totalProgress = files.reduce((sum, file) => sum + file.progress, 0);
    return Math.round(totalProgress / files.length);
  };

  useEffect(() => {
    const totalProgress = calculateTotalProgress();
    if (totalProgress === 100 && !hasAutoMaximizedRef.current && isMinimized) {
      onMaximize();
      hasAutoMaximizedRef.current = true;
    }
  }, [calculateTotalProgress, isMinimized, onMaximize]);

  const handleDeleteFile = (index: number) => {
    setModalState({ type: "delete", index });
  };

  const closeModal = () => {
    setModalState({ type: null });
    onClose;
  };

  const handleRemoveFile = (index: number | undefined) => {
    setFiles((prevFiles) => {
      const updatedFiles = prevFiles.filter((_, i) => i !== index);

      // Get the name of the deleted file
      const deletedFileName = prevFiles[index!]?.name;

      // Check if there are no files left after removal
      if (updatedFiles.length === 0) {
        setIsImportEnabled(false);
      }

      // Remove the deleted file from duplicateResumes if it exists
      setDuplicateResumes((prevDuplicates) =>
        prevDuplicates.filter(
          (duplicate) => !duplicate.includes(deletedFileName)
        )
      );

      return updatedFiles;
    });

    // Reset the file input
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  // TO Do state when the we have multiple duplicate files we will use this to delete them at once.

  // const clearProblematicResumes = () => {
  //   // Remove files that are in duplicateResumes or failedResumes
  //   setFiles((prevFiles) =>
  //     prevFiles.filter(
  //       (file) =>
  //         !duplicateResumes.includes(file.name) && !failedResumes.some((status: any) => status.includes(file.name)),
  //     ),
  //   )

  //   // Clear the lists
  //   setDuplicateResumes([])
  //   setFailedResumes([])

  //   // Reset the file input
  //   if (fileInputRef.current) {
  //     fileInputRef.current.value = ""
  //   }
  // }

  /**
   * Handles the import of the resumes. This method is called when the user
   * clicks the "Import Resumes" button. It sends a POST request to the server
   * with the selected files and waits for the response. If the response is
   * successful, it starts the status checks for the uploaded files.
   *
   * @returns {Promise<void>}
   *
   */
  const handleImport = async () => {
    const queryString = window.location.search;
    console.log("Full query string:", queryString);

    // Remove the leading '?' from the query string
    const queryWithoutQuestionMark = queryString.substring(1);

    // Split the query string by '&' but only for the first occurrence
    const [jobIdPart, jobCodePart] = queryWithoutQuestionMark.split("&", 2);

    // Function to extract value after '='
    const getValueAfterEquals = (param: string): string => {
      const [, value] = param.split("=");
      return decodeURIComponent(value);
    };

    // Extract jobId
    const jobId = getValueAfterEquals(jobIdPart);
    console.log("jobId:", jobId);

    // Extract jobCode (including any '&' characters)
    const jobCode = getValueAfterEquals(
      queryWithoutQuestionMark.substring(jobIdPart.length + 1)
    );
    console.log("jobCode:", jobCode);
    const formData = new FormData();
    setShouldContinueChecking(true);

    if (failedResumes.length > 0) {
      setFiles((prevFiles) =>
        prevFiles.filter((file) =>
          failedResumes.some((status: any) => status.includes(file.name))
        )
      );
      console.log("Filtered Files:", files);
    }
    console.log();
    if (uploadedFiles.length > 0) {
      return startStatusChecks(uploadedFiles, jobId);
    }

    files.forEach((file) => {
      if (file.file) {
        formData.append("files", file.file, file.name);
      }
    });

    setIsImporting(true);
    setLoader(true);

    try {
      const idToken = localStorage.getItem("firebaseIdToken");

      // Function to extract parameter value
      const encodedJobCode = encodeURIComponent(jobCode.trim());
      const headers = {
        ...(idToken && { Authorization: `Bearer ${idToken}` }),
      };

      abortControllerRef.current = new AbortController();
      const signal = abortControllerRef.current.signal;

      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API}api/v1/resumes/upload?job_code=${encodedJobCode}`,
        {
          method: "POST",
          headers,
          body: formData,
          signal,
        }
      );

      const responseData = await response.json();
      if (
        response.ok &&
        responseData.pubsub_status === "Message sent successfully"
      ) {
        const uploadedFiles = responseData.uploaded_files || [];
        console.log("Uploaded Files:", uploadedFiles);

        if (responseData.errors.length > 0) {
          setTotalResumes(responseData.total_files);
          setIsImportEnabled(false);
          const extractedFilenames = extractFilenames(responseData.errors);
          if (extractedFilenames.length > 0) {
            setLoader(false);
            setDuplicateResumes(extractedFilenames);
            setUploadedFiles(responseData.uploaded_files);
          }
          if (uploadedFiles.length === 0) {
            setIsImportEnabled(false);
            return;
          }
        } else {
          startStatusChecks(uploadedFiles, jobId);
          setTotalResumes(uploadedFiles.length);
          setDuplicateResumes(responseData.errors);
        }
      } else {
        console.error("Failed to upload files");
        setLoader(false);
        onClose();
      }
    } catch (error: any) {
      toast({
        variant: "destructive",
        title: "Error uploading resumes",
        description: error.message || "An unexpected error occurred",
      });
      if (error.name === "AbortError") {
        console.log("Upload aborted");
      } else {
        console.error("Error uploading files:", error);

        setLoader(false);
        toast({
          variant: "destructive",
          title: "Error uploading resumes",
          description: error.message || "An unexpected error occurred",
        });
      }
    }
  };
  console.log(isImportEnabled);

  const startStatusChecks = (uploadingFiles: string[], jobId: string) => {
    const unsubscribe = auth.onAuthStateChanged(async (user) => {
      if (user) {
        let intervalId: NodeJS.Timeout | null = null;

        const checkStatus = async () => {
          // Ensure shouldContinueChecking is always the latest value
          if (!shouldContinueChecking) {
            console.log(
              "Stopping status checks as shouldContinueChecking is false"
            );
            if (intervalId) clearTimeout(intervalId);
            return;
          }

          try {
            const idToken = await user.getIdToken(true);
            if (!idToken) {
              throw new Error("Failed to get ID token");
            }

            const headers = {
              Authorization: `Bearer ${idToken}`,
              "Content-Type": "application/json",
            };

            const response = await fetch(
              `${process.env.NEXT_PUBLIC_API}api/v1/resumes/get-status`,
              {
                method: "POST",
                headers,
                body: JSON.stringify({ file_paths: uploadingFiles }),
              }
            );

            const statusData = await response.json();

            const responseApplicants = await apiService(
              `/jobs/${jobId}`,
              "GET",
              null
            );
            console.log("Applicatns data", responseApplicants);
            setApplicantCount(responseApplicants.count.all_applicants);

            const failedResumesData = statusData.statuses
              .filter(
                (item: any) =>
                  item.stages_status.overall_status.toLowerCase() === "failed"
              )
              .map((item: any) => item.resume);

            setFailedResumes(failedResumesData);

            console.log("Status Data:", statusData);
            console.log("Failed Resumes:", failedResumesData);

            if (
              statusData.process === "Completed" &&
              failedResumesData.length === 0
            ) {
              setFiles([]);
              setConfirmation(true);
              setRetry(false);
              onMaximize();
              setShouldContinueChecking(false);
            } else if (
              statusData.process === "Completed" &&
              failedResumesData.length > 0
            ) {
              setLoader(false);
              setRetry(true);
              onMaximize();
              setFiles((prevFiles) =>
                prevFiles.filter((file) =>
                  failedResumesData.some((status: any) =>
                    status.includes(file.name)
                  )
                )
              );
            } else if (shouldContinueChecking) {
              // Continue status checks
              intervalId = setTimeout(checkStatus, 5000);
            }
          } catch (error) {
            console.error("Error checking status:", error);
            onMaximize();
            setLoader(false);
            if (shouldContinueChecking) {
              intervalId = setTimeout(checkStatus, 5000);
            }
          }
        };

        // Start the first status check
        checkStatus();

        // Cleanup function for unsubscribing and clearing intervals
        return () => {
          if (intervalId) clearTimeout(intervalId);
        };
      }
    });

    // Cleanup the auth subscription on component unmount
    return () => unsubscribe();
  };

  const getButtonClass = (isEnabled: boolean) =>
    isEnabled
      ? "bg-primary text-white px-[16px] text-[14px] py-[8px] mt-[10px] cursor-pointer rounded-lg border-none"
      : "bg-primary text-white p-[10px] text-[14px] mt-[10px] cursor-not-allowed rounded-lg border-none opacity-40";

  const isRetry =
    retry ||
    ((uploadedFiles?.length ?? 0) > 0 && duplicateResumes.length === 0);
  const isEnabled =
    duplicateResumes.length === 0 && (isRetry || isImportEnabled);
  const buttonText = isRetry ? "Retry" : "Import";

  if (isMinimized) {
    const totalProgress = calculateTotalProgress();
    const isComplete = totalProgress === 100;
    const fileCount = files.length;
    const isPlural = fileCount !== 1;

    return (
      <Draggable>
        <div className="fixed minimize-popup bottom-4 right-4 bg-white shadow-lg rounded-lg p-4 w-[403px] h-[100px] z-50 shadow-xl cursor-move">
          {!loader ? (
            <>
              {/* Maximize Button */}
              <div className="flex justify-end">
                <Image
                  src="/images/maximize.png"
                  width={16}
                  height={16}
                  alt="Maximize"
                  onClick={onMaximize}
                  className="cursor-pointer"
                />
              </div>

              {/* Uploading Information */}
              <div className="flex justify-between items-center">
                <span className="text-[#334155] text-[14px] font-semibold">
                  {isComplete ? "Uploaded" : "Uploading"} {fileCount} resume
                  {isPlural ? "s" : ""}
                </span>
              </div>

              {/* Progress Percentage */}
              <div className="flex justify-end">
                <span className="text-sm font-medium text-gray-500">
                  {totalProgress}%
                </span>
              </div>

              {/* Progress Bar */}
              <div className="bg-[#e0e0e0] h-[5px] flex-1 rounded-sm w-full">
                <div
                  className="h-full bg-[#4caf50] rounded-sm transition-all duration-500 rounded"
                  style={{ width: `${totalProgress}%` }}
                ></div>
              </div>
            </>
          ) : (
            <div className="items-center justify-center h-full text-center text-[#334155] text-[14px] font-medium">
              <div className="flex justify-end">
                <Image
                  src="/images/maximize.png"
                  width={16}
                  height={16}
                  alt="Maximize"
                  onClick={onMaximize}
                  className="cursor-pointer"
                />
              </div>
              Parsing...
            </div>
          )}
        </div>
      </Draggable>
    );
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-5 flex items-center justify-center z-50">
      {/* <div className="bg-white rounded-lg pl-6 pr-6 pb-6 w-full max-w-md"> */}
      {!isMinimized && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex justify-center items-center z-[1000]">
          <Draggable>
          <div className="bg-white pl-6 pr-6 pb-6 pt-[12px]  w-[534px] h-auto rounded-lg shadow-md cursor-move">
            {!loader ? (
              <>
                <div className="flex space-x-2 justify-end ">
                  <Minus className="cursor-pointer mt-2" onClick={onMinimize} />
                  <Image
                    src={"/images/crossIcon.svg"}
                    width={16}
                    height={16}
                    alt={""}
                    onClick={cancelModelPopup}
                  />
                </div>
                <div className="flex justify-between text-left">
                  <h2 className="text-[14px] text-[#334155] font-semibold">
                    Upload Resumes
                  </h2>
                </div>
                {duplicateResumes.length === 0 &&
                  failedResumes.length === 0 &&
                  uploadedFiles.length === 0 && (
                    <div className="text-left">
                      <label
                        htmlFor="file-upload"
                        className="text-[12px] text-primary cursor-pointer"
                      >
                        Add more files
                      </label>
                    </div>
                  )}
                <input
                  id="file-upload"
                  ref={fileInputRef}
                  multiple
                  type="file"
                  accept=".pdf,.docx"
                  onChange={handleAddFiles}
                  style={{ display: "none" }}
                />

                {failedResumes.length > 0 && (
                  <div className="text-sm text-red-500">
                    {failedResumes.length} out of {totalResumes} resumes failed
                    to parse.
                  </div>
                )}

                {duplicateResumes.length > 0 && (
                  <div className="text-sm text-red-500">
                    {duplicateResumes.length} out of {totalResumes} resumes are
                    duplicates. Please remove them and continue your import
                    process
                  </div>
                )}
                {/* {(duplicateResumes.length > 0) && (
                  <div className="mt-2">
                    <button
                      onClick={clearProblematicResumes}
                      className="text-[12px] text-white bg-red-500 px-2 py-1 rounded-md hover:bg-red-600"
                    >
                      Clear Problematic Files
                    </button>
                  </div>
                )} */}
              </>
            ) : !confirmation ? (
              <div>
                <div className="flex justify-end text-left space-x-2">
                  <Minus
                    className="cursor-pointer mt-[2px]"
                    onClick={onMinimize}
                  />
                  <X className="text-gray-400 h-5 w-5" />
                </div>
              </div>
            ) : (
              <div className="flex justify-end mt-2 ml-2 cursor-pointer">
                <Image
                  src={"/images/crossIcon.svg"}
                  width={16}
                  height={16}
                  alt={""}
                  onClick={onClose}
                />
              </div>
            )}

            <div className="file-list max-h-[350px] overflow-y-auto mt-4 pr-2 rounded-lg text-left">
              {loader ? (
                confirmation ? (
                  <div className="text-center">
                    <SuccessAnimation />
                    <div className="text-[#000000] text-[18px] font-semibold">
                      {files.length === 1 ? "Resume" : "Resumes"} Parsed
                      Successfully
                    </div>
                  </div>
                ) : (
                  <div className="loading-container items-center">
                    <div className="loading"></div>
                    <div id="loading-text">parsing</div>
                  </div>
                )
              ) : (
                files.map((file, index) => (
                  <div
                    key={index}
                    className="file-list items-center justify-between mb-2.5 p-3 border-[1px] border-[#E2E8F0] rounded-sm"
                  >
                    <div className="flex justify-between pb-2">
                      <div className="flex-1 pr-2 overflow-hidden">
                        <span className="text-[14px] leading-6 text-[#000000] ">
                          {truncateFileName(file.name)} {file.type}
                        </span>
                        <span className="text-[10px] text-[#94A3B8] ml-2">
                          {file.size}
                        </span>
                      </div>
                      <div className="flex items-center">
                        <span className="flex items-center progress-text mr-2">
                          {file.progress}%
                        </span>
                        <span className="flex items-center space-x-2">
                          {file.progress === 100 ? (
                            <>
                              <FaCheckCircle color="green" />
                              <Image
                                src="/images/trash.svg"
                                alt=""
                                width={16}
                                height={16}
                                onClick={() => handleDeleteFile(index)}
                                className="cursor-pointer"
                              />
                            </>
                          ) : (
                            <X
                              className="text-gray-400 h-5 w-5 cursor-pointer"
                              onClick={() => handleRemoveFile(index)}
                            />
                          )}
                        </span>
                      </div>
                    </div>

                    <div className="bg-[#e0e0e0] h-[5px] flex-1 rounded-sm w-full">
                      <div
                        className="h-full bg-[#4caf50] rounded-sm transition-all duration-500 rounded"
                        style={{ width: `${file.progress}%` }}
                      ></div>
                    </div>
                    {duplicateResumes.includes(file.name) && (
                      <div className="text-sm text-red-500">{file.name}</div>
                    )}
                  </div>
                ))
              )}
            </div>

            <div className="">
              {!loader ? (
                <>
                  <div className="flex justify-end space-x-2 pt-4 bottom-2">
                    <button
                      onClick={cancelModelPopup}
                      className="cancel-btn text-[#0F172A] px-[16px] py-[8px] text-[14px]"
                    >
                      Cancel
                    </button>

                    <button
                      onClick={() => {
                        handleImport();
                        setLoader(true);
                      }}
                      className={getButtonClass(isEnabled)}
                      disabled={!isEnabled}
                      title={
                        duplicateResumes.length > 0
                          ? "Please remove duplicate resumes first"
                          : ""
                      }
                    >
                      {buttonText}
                    </button>
                  </div>
                </>
              ) : confirmation ? (
                <div className="text-center mt-[40px] mb-[10px]">
                  <button
                    onClick={onClose}
                    className="justify-center items-center bg-primary text-white pl-[22px] pr-[22px] pt-[8px] pb-[8px] cursor-pointer rounded-lg border-none "
                  >
                    Done
                  </button>
                </div>
              ) : (
                ""
              )}
            </div>
          </div>
          </Draggable>
        </div>
      )}

      <AlertDialogWrapper
        isOpen={modalState.type === "delete"}
        onClose={closeModal}
        title="Are you sure you want to delete?"
        description=""
        confirmText="Delete"
        cancelText="Cancel"
        onConfirm={() => handleRemoveFile(modalState.index)}
      />

      <AlertDialogWrapper
        isOpen={modalState.type === "cancel"}
        onClose={closeModal}
        title="Are you sure you want to cancel?"
        description=""
        confirmText="Yes"
        cancelText="No"
        onConfirm={() => cancelImport()}
      />
    </div>
  );
};

export default ProgressModal;
