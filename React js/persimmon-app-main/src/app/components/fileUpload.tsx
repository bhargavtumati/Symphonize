import React, { useState } from "react";
import { Plus } from "lucide-react";
import UploadModal from "./uploadModel";
import { useUpload } from "./uploadContext";
import { FileData } from "../types";
import { set } from "lodash";
interface FileUploadProps {
 disabled?: boolean
 isLoading?:boolean
}
const FileUpload: React.FC<FileUploadProps> = ({disabled, isLoading}) => {
  const { isMinimized, setFiles, setIsMinimized, setShowProgressModal } =
    useUpload();
  const [showUploadModal, setShowUploadModal] = useState<boolean>(false);
  const handleUploadClick = () => { 
    if (!disabled && !isLoading) 
    setShowUploadModal(true);
  };

  function getFileType(fileName: string): 'pdf' | 'docx' {
    return fileName.toLowerCase().endsWith('.pdf') ? 'pdf' : 'docx';
  }

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const newFiles: FileData[] = Array.from(event.target.files || [])
      .filter((file) => /(\.pdf|\.docx)$/i.test(file.name))
      .map((file) => ({
        name: file.name,
        size: `${(file.size / 1024).toFixed(2)} KB`,
        progress: 0,
        file,
        type: getFileType(file.name)
      }));

    setFiles((prevFiles) => [...prevFiles, ...newFiles]);
    setShowUploadModal(false);
    setShowProgressModal(true);
    setIsMinimized(false);
    startUpload(newFiles);
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
          if (file.progress >= 100) {
            clearInterval(interval);
          }

          return updatedFiles;
        });
      }, 500);
    });
  };


  const handleCloseModal = () => {
    setShowUploadModal(false);
    setShowProgressModal(false);
    setIsMinimized(false);
    setFiles([]);
  };

  return (
    <>
      <div
        onClick={disabled || isLoading || isMinimized ? undefined : handleUploadClick}
        className={`rounded-lg flex import-resumes-btn items-center bg-white text-[14px] w-[166px] h-[38px] space-x-2 pl-4 font-medium ${
        disabled || isLoading || isMinimized
            ? "cursor-not-allowed opacity-50"
            : "cursor-pointer hover:bg-gray-100 hover:text-slate-800"
        }`}
      >
        <Plus className="w-[16px] h-[16px] text-bold" />
        <span className={ disabled || isLoading ||isMinimized ? "text-gray-400" : "text-slate-800"}>
          Import Resumes
        </span>
      </div>

      {showUploadModal && (
        <UploadModal onClose={handleCloseModal} onUpload={handleFileChange} />
      )}
    </>
  );
};

export default FileUpload;
