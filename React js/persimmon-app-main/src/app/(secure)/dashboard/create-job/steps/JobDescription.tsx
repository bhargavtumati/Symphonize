"use client";

import type React from "react";
import { useState, useEffect } from "react";
import { Card } from "@/components/ui/card";
import { Loader2, Sparkles, X } from "lucide-react";
import { marked } from "marked";
import { apiService } from "@/app/api/service";
// import ReactQuill from "react-quill";

// Dynamically import ReactQuill (client-side only)
// const QuillEditor = dynamic(() => import("@/app/components/richtexteditor"), { ssr: false })
// // Import Quill styles
// import "react-quill/dist/quill.snow.css";
// import RichTextEditor from "@/app/components/richtexteditor";
import QuillEditor from "@/app/components/richtexteditor";

interface JobDescription {
  description: string;
}

interface StepProps {
  data: JobDescription;
  onChange: (value: string) => void;
  errors: Partial<JobDescription>;
  onBack: () => void;
  onNext: () => void;
}

const Step2JobDescription: React.FC<StepProps> = ({
  errors,
  data,
  onChange,
  onBack,
  onNext,
}) => {
  const [valueDescription, setDescriptionValue] = useState<string>("");
  const [errorMessage, setErrorMessage] = useState<string>("");
  const [showAiModal, setShowAiModal] = useState<boolean>(false);
  const [aiLearningPrompt, setAiLearningPrompt] = useState<string>("");
  const [isAiGenerating, setIsAiGenerating] = useState<boolean>(false);

  useEffect(() => {
    if (data.description) {
      console.log("descriptions", data.description);
      setDescriptionValue(data.description);
    }
  }, [data.description]);

  const handleEditorChange = (content: string) => {
    console.log("Editor content changed:", content);
    setDescriptionValue(content);
    onChange(content);
    valueDescription.length < 3000 ? setErrorMessage("Job description must contain a minimum of 3000 characters") : setErrorMessage("");
  };

  const generateWithAI = async () => {
    const payload = {
      input: valueDescription,
      prompt: aiLearningPrompt,
    };

    try {
      setIsAiGenerating(true);
      const response = await apiService(
        "/ai/generate-job-description",
        "POST",
        payload
      );

      if (!response) {
        throw new Error("Network response was not ok");
      }

      if (response.job_description) {
        console.log("AI-generated job description:", response.job_description);
        const formattedDescription = await marked(response.job_description);
        setDescriptionValue(formattedDescription);
        onChange(formattedDescription);
      } else {
        throw new Error("Invalid API response format");
      }
    } catch (error) {
      console.error("Error creating job:", error);
    } finally {
      setIsAiGenerating(false);
      setShowAiModal(false);
    }
  };

  const handleNextClick = () => {
    if (valueDescription.length < 3000) {
      setErrorMessage(
        "Job description must contain a minimum of 3000 characters"
      );
    } else {
      setErrorMessage("");
      onNext();
    }
  };

  return (
    <div className="flex flex-col md:flex-row gap-4">
      <Card className="w-full md:w-[70%] border-none">
        <div className="">
          <div className="w-full md:w-[100%] bg-white p-10">
            <div className="flex justify-between">
              <h3 className="text-xl font-semibold mb-4">Job Description</h3>
              <button
                className="flex items-center bg-yellow-500 w-[155px] h-[38px] text-white rounded-lg text-[14px] font-medium"
                onClick={() => setShowAiModal(true)}
              >
                <Sparkles className="text-white mr-2 ml-2" />
                {valueDescription ? "Enhance with AI" : "Write with AI"}
              </button>
            </div>
            <div className="grid grid-cols-1 gap-6 pt-2">
              <div className="editor">
                <QuillEditor
                  value={valueDescription}
                  onChange={handleEditorChange}
                />

               
              </div>
            
            </div>
          </div>
          {errorMessage && (
                  <p className="text-red-500 text-sm mt-8 pl-10">{errorMessage}</p>
                )}
        </div>
        <div className="flex justify-end space-x-4 px-8 py-12">
          <button
            type="button"
            onClick={onBack}
            className="bg-white border border-[1px] border-gray-300 px-4 py-2 rounded-md w-[105px] h-[40px]"
          >
            Back
          </button>
          <button
            type="button"
            onClick={handleNextClick}
            className="bg-blue-600 text-white px-4 py-2 rounded-md w-[105px] h-[40px]"
          >
            Next
          </button>
        </div>
      </Card>

      {showAiModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
          <div className="bg-white rounded-lg p-6 h-[18em] w-[47em] relative">
            <button
              className="absolute top-3 right-3 text-gray-500 hover:text-gray-700"
              onClick={() => setShowAiModal(false)}
            >
              <X size={24} />
            </button>
            <h3 className="text-xl font-semibold mb-4">
              {valueDescription ? "Personalize with AI" : "Write with AI"}
            </h3>
            <textarea
              className="w-full p-2 border rounded-lg mb-4 max-h-36"
              placeholder="Enter your prompt"
              rows={4}
              value={aiLearningPrompt}
              onChange={(e) => setAiLearningPrompt(e.target.value)}
            />
            <div className="flex justify-end">
              <button
                className="bg-yellow-500 text-white px-4 py-2 rounded-md"
                onClick={generateWithAI}
              >
                {valueDescription ? "Enhance with AI" : "Generate with AI"}
              </button>
            </div>
          </div>
          {isAiGenerating && (
            <div className="loader absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 flex items-center justify-center">
              <Loader2 className="mr-2 h-[30px] w-12 animate-spin" />
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default Step2JobDescription;
