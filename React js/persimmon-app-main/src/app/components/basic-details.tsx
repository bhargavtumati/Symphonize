import type { Applicant } from "@/app/types/applicants";
import { useEffect, useRef, useState } from "react";
import LabelValuePair from "./label-value-pair";
import { Skeleton } from "@/components/ui/skeleton";
import SkeletonComponent from "./skeleton/card-skeleton";
import { SkeletonType } from "../utils/constants";
interface BasicDetailsProps {
  applicant: Applicant | undefined;
  isLoading: boolean
}

interface InfoItem {
  label: string;
  value: string | React.ReactNode;
}
export function BasicDetails({ applicant, isLoading }: BasicDetailsProps) {
  const [isExpanded, setIsExpanded] = useState(false);
  const [showReadMore, setShowReadMore] = useState(false);
  const aboutRef = useRef<HTMLParagraphElement>(null);
  if (applicant)
    applicant.details.about =
      "As a seasoned software engineer with over a decade of experience, I've had the privilege of working on a diverse range of projects that have honed my skills in full-stack development, cloud architecture, and machine learning. My passion lies in creating scalable, efficient solutions that not only meet but exceed client expectations. I'm particularly adept at translating complex technical concepts into user-friendly applications, always keeping the end-user experience at the forefront of my design philosophy. Throughout my career, I've led teams in developing cutting-edge web and mobile applications, implemented robust CI/CD pipelines, and architected cloud-native solutions on platforms like AWS and Azure. I'm a strong advocate for clean code practices, test-driven development, and agile methodologies. Outside of work, I contribute to open-source projects and mentor aspiring developers, believing strongly in giving back to the tech community that has supported my growth. I'm always excited about learning new technologies and methodologies, constantly pushing the boundaries of what's possible in software engineering.";

  useEffect(() => {
    if (aboutRef.current) {
      const lineHeight = parseInt(
        window.getComputedStyle(aboutRef.current).lineHeight
      );
      const maxHeight = lineHeight * 3; // 3 lines
      setShowReadMore(aboutRef.current.scrollHeight > maxHeight);
    }
  }, [applicant?.details.about]);

  const personalInfoItems: InfoItem[] = [
    {
      label: "Full Name",
      value: applicant?.details.personal_information?.full_name,
    },
    {
      label: "Email ID",
      value: applicant?.details.personal_information?.email,
    },
    {
      label: "Gender",
      value: applicant?.details.personal_information?.gender,
    },
    {
      label: "Date of Birth",
      value: applicant?.details.personal_information?.date_of_birth,
    },
    {
      label: "Address",
      value: applicant?.details.personal_information?.address,
    },
  ];

  const jobInfoItems: InfoItem[] = [
    {
      label: "Job Title",
      value: applicant?.details.job_information?.job_title,
    },
    {
      label: "Department",
      value: applicant?.details.job_information?.department,
    },
    {
      label: "Current Organization",
      value: applicant?.details.job_information?.current_work_at,
    },
    {
      label: "Work Experience",
      value: applicant?.details.job_information?.work_experience,
    },
    {
      label: "Job Location",
      value: applicant?.details.job_information?.job_location,
    },
    {
      label: "Current CTC",
      value: "N/A",
    },
    {
      label:"Skills",
      value: applicant && applicant.details.job_information?.skills.length > 0 ? applicant?.details.job_information?.skills.join(", ") : "N/A",
    }
 
  ];

  const socialMedia: InfoItem[] = [
    {
      label:"LinkedIn Profile URL",
      value: applicant?.details.social_media?.linkedin,
    },
    {
      label: "GitHub URL",
      value: applicant?.details.social_media?.github,
    },
    {
      label: "Instagram URL",
      value: applicant?.details.social_media?.instagram,
    },
    {
      label: "Facebook URL",
      value: applicant?.details.social_media?.facebook,
    },
  ];
  return (
    <div className="space-y-6 bg-white">
      <div className="px-4">
       <h3 className="font-semibold mb-2 text-[18px] leading-7">About</h3>
        {isLoading ?
          (<div className="pr-3 pl-3">
            <SkeletonComponent type={SkeletonType.Description} className="h-4 w-full" rows={5} />
            
          </div>
          ) :
          (applicant?.details.about ? (
            <div>
              <p
                ref={aboutRef}
                className={`text-[16px] leading-7 text-slate-800 p-2 ${!isExpanded ? "line-clamp-3" : ""
                  }`}
              >
                {applicant?.details.about}
              </p>
              {showReadMore && (
                <button
                  onClick={() => setIsExpanded(!isExpanded)}
                  className="text-primary font-medium ml-2"
                >
                  {isExpanded ? "Read less" : "Read more"}
                </button>
              )}
            </div>
          ) : (
            <p className="text-[16px] leading-7 text-slate-800 p-2">
              Profile summary not available
            </p>
          )
          )}
      </div>
      <div className="px-4">
        {isLoading ? (
          <>
            <SkeletonComponent type={SkeletonType.Card} className="h-7 w-48" rows={3} columns={2} />
           
          </>
        ) : applicant?.details.personal_information ? (
          <div className="px-4">
            <h3 className="font-semibold text-[18px] leading-7">
              Personal Information
            </h3>

            <div className="grid grid-cols-2 gap-4 p-3">
              {personalInfoItems.map((item, index) => (
                <LabelValuePair
                  key={index}
                  label={item.label}
                  value={item.value}
                  labelClassName="text-slate-500 text-[14px]"
                  valueClassName="text-[16px] leading-7 text-slate-800"
                />
              ))}
            </div>
          </div>
        ) : (
          <p className="text-gray-500">No personal information available</p>
        )}
      </div>


      <div className="px-4">
      {isLoading ? (
          <>
          <SkeletonComponent type={SkeletonType.Card} className="h-7 w-48" rows={3} columns={2} />
          </>
        ) : (
          <>
            {
              applicant?.details.job_information && (
                <div className="px-4">
                  <h3 className="font-semibold mb-2 text-[18px] leading-7">
                    Job Information
                  </h3>
                  <div className="grid grid-cols-2 gap-4 p-3">
                    {jobInfoItems &&
                      jobInfoItems.map((item, index) => (
                        <LabelValuePair
                          key={index}
                          label={item.label}
                          value={item.value}
                          labelClassName="text-slate-500 text-[14px]"
                          valueClassName="text-[16px] leading-7 text-slate-800"
                        />
                      ))}
                  </div>
                </div>
              )
            }
          </>
        )}
      </div>  
      <div className="px-4">
        {isLoading ? (
            <SkeletonComponent type={SkeletonType.Card} className="h-7 w-48" rows={3} columns={2} />
       
        ) : (
          <>
            {
              applicant?.details.social_media && (
                <div className="px-4">
                  <h3 className="font-semibold mb-2 text-[18px] leading-7">
                    Social Media
                  </h3>
                  <div className="grid grid-cols-2 gap-4 p-3">
                    {socialMedia &&
                      socialMedia.map((item) => (
                        <div key={item.label}>
                          <p className="text-slate-500 text-[14px]">{item.label}</p>
                          {item.value ? (
                            <a
                              href={`${item.value}`}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="font-medium text-primary hover:underline"
                            >
                              {item.value}
                            </a>
                          ) : (
                            <p className="text-[16px] leading-7 text-slate-800">N/A</p>
                          )}
                        </div>
                      ))}
                  </div>
                </div>
              )
            }
          </>
         )}
      </div>
    </div>
  );
}
