import { PageHeaderProps } from "@/app/types";
import { ArrowLeft } from "lucide-react";
import { useRouter } from "next/navigation";
import FileUpload from "../fileUpload";

export const PageHeader: React.FC<PageHeaderProps> = ({ code,status }) => {
    const router = useRouter(); // Initialize useRouter
    const handleBackClick = () => {
      // Navigate back to the jobs page, or any specific URL if needed
      router.push("/dashboard"); // Adjust the URL as needed
    };
    return (
      <div className="flex justify-between items-center p-0">
        <div className="flex items-center" aria-label="Back to jobs">
          <ArrowLeft
            className="w-[16px] h-[16px] text-slate-500 cursor-pointer"
            onClick={handleBackClick}
          />
  
          <span className="Inter text-slate-500 pl-1">{code}</span>
        </div>
        <FileUpload disabled = {status === "CLOSED"}/>
      </div>
    );
  };