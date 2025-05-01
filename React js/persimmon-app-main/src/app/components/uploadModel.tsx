import React, { useState } from "react";
import { X } from "lucide-react";
import Image from "next/image";

interface UploadModalProps {
  onClose: () => void;
  onUpload: (event: React.ChangeEvent<HTMLInputElement>) => void;
}

const UploadModal: React.FC<UploadModalProps> = ({ onClose, onUpload }) => {
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files;
    if (files) {
      const invalidFiles = Array.from(files).filter(
        file => !file.name.toLowerCase().match(/\.(pdf|docx)$/)
      );
      
      if (invalidFiles.length > 0) {
        setErrorMessage("Only PDF and DOCX files are allowed.");
      } else {
        setErrorMessage(null);
        onUpload(event);
      }
    }
  };
  const handleFileClick = () => {
    const fileInput = document.getElementById("fileInput") as HTMLInputElement;
    if (fileInput) fileInput.click();
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex justify-center items-center z-[1000]">
      <div className="bg-white p-4 w-[534px] h-auto rounded-lg shadow-md">
        <div className="flex justify-end">
          <button
            aria-label="Close upload modal"
            className="flex right-3 text-gray-500 hover:text-gray-700"
            onClick={onClose}
          >
            <Image
              src={"/images/crossIcon.svg"}
              width={16}
              height={16}
              alt={""}
            />
          </button>
        </div>
        <div>
          <div className="flex justify-between pl-[16px] ">
            <h2 className="text-[14px] font-semibold text-[#334155]">
              Upload Resumes
            </h2>
          </div>

          <div
            className="border-[1px] border-dashed border-[#1BA5DC] p-10 text-center text-[#555] items-center bg-[#F1F9FE] p-8 m-4 cursor-pointer"
            onClick={handleFileClick}
          >
            <div
              className="flex justify-center items-center mb-2.5 cursor-pointer"
              role="button"
              aria-label="Click to upload files"
            >
              <Image
                src="/images/upload.png"
                width={100}
                height={100}
                alt="Upload icon"
              />
            </div>

            <p className="text-[#334155]">Click to Upload</p>
            <div className="items-center text-center">
              <span>or</span>
              <span className="text-primary cursor-pointer text-center">
                <span> Browse</span>
              </span>
            </div>

            <input
              type="file"
              id="fileInput"
              multiple
              accept=".pdf,.docx"
              style={{ display: "none" }}
              onChange={handleFileChange}
            />
            <p className="text-[12px] text-[#94A3B8] leading-5">
              Accepted file types: PDF & .docx
            </p>
          </div>
          {errorMessage && (
          <div className="text-red-500 text-sm text-center mt-2">
            {errorMessage}
          </div>
        )}
        </div>
      </div>
    </div>
  );
};

export default UploadModal;
