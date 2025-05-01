import type React from "react";
import { Dispatch, SetStateAction, useState } from "react";
import { Editor } from "@tinymce/tinymce-react";

interface RichTextEditorProps {
  value: string;
  onChange: (value: string) => void;
  onFileAttach?: (file: File[]) => void;
  onEditorInit?: (editor: any) => void;
  placeholder?: string;
  attachedFiles: File[];
  setAttachedFiles: Dispatch<SetStateAction<File[]>>
}

const RichTextEditor: React.FC<RichTextEditorProps> = ({
  value,
  onChange,
  onFileAttach,
  onEditorInit,
  placeholder = "Enter the Job Description",
  attachedFiles,
  setAttachedFiles
}) => {
  const [loading, setLoading] = useState(true);
  const [attachedFile, setAttachedFile] = useState<File | null>(null);

  const handleEditorChange = (content: string) => {
    if (content !== value) {
        onChange(content);
        // Check if any attached file names are removed
        if (attachedFiles.length > 0) {
            const updatedFiles = attachedFiles.filter(file => content.includes(file.name));

            // If any files were removed, update the state
            if (updatedFiles.length !== attachedFiles.length) {
                setAttachedFiles(updatedFiles);
            }
        }
    }
};


  const handleEditorInit = (_: any, editor: any) => {
    setLoading(false);
    onEditorInit?.(editor);
  };

  return (
    <div style={{ position: "relative" }}>
      {loading && (
        <div className="flex justify-center items-center h-12">
          <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-gray-900"></div>
        </div>
      )}
      <Editor
        apiKey={process.env.NEXT_PUBLIC_TINYMCE_API_KEY}
        value={value}
        onEditorChange={handleEditorChange}
        onInit={handleEditorInit}
        init={{
          placeholder: placeholder,
          height: 400,
          menubar: false,
          plugins: "lists link image code",
          font_size_formats: "11px 12px 14px 16px 18px 24px 36px 48px",
          toolbar:
            "undo redo | fontsize | blocks | formatselect | bold italic underline strikethrough | alignleft aligncenter alignright alignjustify | forecolor backcolor | bullist numlist | link image | code",
          branding: false,
          file_picker_types: "file",
          file_picker_callback: (callback, value, meta) => {
            const input = document.createElement("input");
            input.setAttribute("type", "file");
            input.setAttribute("accept", "*/*");
            input.onchange = async (event) => {
              const file = (event.target as HTMLInputElement).files?.[0];
              if (file) {
                setAttachedFile(file);
                onFileAttach?.([file]);
                callback(file.name, { text: file.name });
              }
            };
            input.click();
          },
        }}
      />
    </div>
  );
};

export default RichTextEditor;
