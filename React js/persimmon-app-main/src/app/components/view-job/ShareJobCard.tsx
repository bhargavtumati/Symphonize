import { apiService } from "@/app/api/service";
import { ShareJobCardProps } from "@/app/types";
import { Card } from "@/components/ui/card";
import { Copy, Mail } from "lucide-react";
import Image from "next/image";
import { useEffect, useState } from "react";

export const ShareJobCard: React.FC<ShareJobCardProps> = ({
    jobTitle,
    organizationName,
    jobType,
    jobLocation,
    workExperience,
    jobCode,
    disable
}) => {
    const [isCopied, setIsCopied] = useState(false);
    const [careerPageUrl, setCareerPageUrl] = useState<string | null>(null);
    const storedUserEmail = sessionStorage.getItem("userEmail");
    const domain = storedUserEmail?.split("@")[1] || "";
    let jobLink: any;

    useEffect(() => {
        const fetchCareerPageUrl = async () => {
            try {
                const response = await apiService(`/careerpage/customization/domain/${domain}`, "GET", null);
                if (response?.data?.career_page_url) {
                    setCareerPageUrl(response.data.career_page_url);
                }
            } catch (error) {
                console.error("Error fetching career page URL:", error);
            }
        };

        if (domain) {
            fetchCareerPageUrl();
        }
    }, [domain]);

    if (careerPageUrl) {
        jobLink = `${careerPageUrl}?jobURL=${process.env.NEXT_PUBLIC_FE_URL}/connection/${domain}/jobs?jobCode=${jobCode}`;
    }
    else {
        jobLink = `${process.env.NEXT_PUBLIC_FE_URL}/connection/${domain}/jobs?jobCode=${jobCode}`;
    }

    const sharingTemplate = `#HiringAlert
  
  Join us as ${jobTitle} at ${organizationName}!
  
  **Location**: ${jobLocation}  
  **Experience**: ${workExperience}  
  **Job Type**: ${jobType}  
  
  Apply here: ${jobLink}
  
  Know someone perfect for the role? Share this with them!`;

    const handleShareClick = (
        platform: "mail" | "linkedin" | "whatsapp" | "twitter" | "instagram"
    ) => {
        let url: string | undefined;
        const to = "";
        const subject = encodeURIComponent(
            `Job Alert: ${jobTitle} at ${organizationName}`
        );
        const body = encodeURIComponent(sharingTemplate);
        switch (platform) {
            case "mail":
                url = `https://mail.google.com/mail/?view=cm&fs=1&to=${to}&su=${subject}&body=${body}`;
                break;

            case "linkedin":
                url = `https://www.linkedin.com/sharing/share-offsite/?url=${encodeURIComponent(
                    jobLink
                )}&title=${encodeURIComponent(jobTitle)}`;
                break;
            case "whatsapp":
                url = `https://wa.me/?text=${body}`;
                break;
            case "twitter":
                url = `https://twitter.com/intent/tweet?text=${body}`;
                break;
            case "instagram":
                // Copy the template to the clipboard
                navigator.clipboard
                    .writeText(sharingTemplate)
                    .then(() => {
                        window.open("https://www.instagram.com/direct/inbox/", "_blank");
                    })
                    .catch((err) => {
                        console.error("Could not copy text: ", err);
                        alert("Failed to copy text to clipboard. Please try again.");
                    });
                break;
            default:
                return;
        }
        if (url) {
            window.open(url, "_blank"); // Opens the URL in a new tab
        }
    };
    const handleCopyClick = () => {
        navigator.clipboard
            .writeText(jobLink)
            .then(() => {
                setIsCopied(true);
                setTimeout(() => setIsCopied(false), 1500); // Reset after 1.5 seconds
            })
            .catch((error) => {
                console.error("Failed to copy:", error);
            });
    };

    return (
        <Card className="bg-white px-6 py-4 rounded-lg mt-4 xl:h-[206px] flex flex-col justify-between  border-none">
            <h2 className="text-lg font-medium">Share Job</h2>
            <div className="flex justify-around mt-4 flex-wrap	">
                <span
                    className={`flex flex-col items-center ${!disable ? "cursor-pointer" : "opacity-20 cursor-not-allowed"}`}
                    onClick={() => { if (!disable) handleShareClick("mail") }}
                >
                    <div className="bg-[#F3F3F3] rounded-full w-[30px] h-[30px]">
                        <Mail size={22} className="m-[4px]" />
                    </div>
                    <p className="text-slate-500 text-sm Inter">Mail</p>
                </span>
                <span
                    className={`flex flex-col items-center ${!disable ? "cursor-pointer" : "opacity-20 cursor-not-allowed"}`}
                    onClick={() => { if (!disable) handleShareClick("linkedin") }}
                >
                    <Image
                        src="/images/view_job_page/linkedin_logo.png"
                        alt="LinkedIn Icon"
                        width={30} // Set the width
                        height={30} // Set the height
                        className="object-contain rounded-full"
                    />
                    <p className="text-slate-500 Inter text-sm">LinkedIn</p>
                </span>
                <span
                    className={`flex flex-col items-center ${!disable ? "cursor-pointer" : "opacity-20 cursor-not-allowed"}`}
                    onClick={() => { if (!disable) handleShareClick("whatsapp") }}
                >
                    <Image
                        src="/images/view_job_page/whatsapp_logo.png"
                        alt="WhatsApp Icon"
                        width={30} // Adjust width as needed
                        height={30} // Adjust height as needed
                        className="object-contain rounded-full"
                    />
                    <p className="text-slate-500 Inter text-sm">WhatsApp</p>
                </span>
                <span
                    className={`flex flex-col items-center ${!disable ? "cursor-pointer" : "opacity-20 cursor-not-allowed"}`}
                    onClick={() => { if (!disable) handleShareClick("twitter") }}
                >
                    <Image
                        src="/images/view_job_page/x_logo.png"
                        alt="X Icon"
                        width={30} // Set the desired width
                        height={30} // Set the desired height
                        className="object-contain rounded-full"
                    />
                    <p className="text-slate-500 Inter text-sm">Twitter</p>
                </span>
                <span
                    className={`flex flex-col items-center ${!disable ? "cursor-pointer" : "opacity-20 cursor-not-allowed"}`}
                    onClick={() => { if (!disable) handleShareClick("instagram") }}
                >
                    <Image
                        src="/images/view_job_page/instagram_logo.png"
                        alt="Instagram Icon"
                        width={30} // Set the desired width
                        height={30} // Set the desired height
                        className="object-contain rounded-full"
                    />
                    <p className="text-slate-500 Inter text-sm">Instagram</p>
                </span>
            </div>

            <div className="relative flex items-center mt-4">
                <input
                    type="text"
                    value={jobLink}
                    readOnly
                    className="w-full border rounded-md px-2 py-1 h-[40px] text-slate-500 pr-10" // Add pr-10 to make space for the icon
                />
                <button
                    className="absolute right-2 top-1/2 transform -translate-y-1/2 p-1" // Position the icon inside the input
                    onClick={handleCopyClick}
                >
                    <Copy size={16} color={isCopied ? "#0F8FC9" : "#000"} />{" "}
                    {/* Change color when copied */}
                </button>
            </div>
        </Card>
    );
};