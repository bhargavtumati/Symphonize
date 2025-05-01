import Image from "next/image";
import { Mail, Phone } from "lucide-react";
import type { Applicant } from "@/app/types/applicants";
import { formatRelativeDate } from "@/app/utils/format-relative-date";
import { FaLinkedin } from "react-icons/fa";
interface ApplicantCardProps {
  applicant: Applicant;
  isLoading: boolean
}

export function ApplicantCard({ applicant }: ApplicantCardProps) {
  const imageSource = applicant.details?.applicant_image
    ? `data:image/jpeg;base64,${applicant.details.applicant_image}`
    : "/images/avatar.svg"
  return (
    <div className="p-6">
      <div className="text-sm text-muted-foreground text-right">
            Applied {formatRelativeDate(applicant.details.applied_date)}
          </div>
      <div className="flex gap-6">
        <div className="flex-shrink-0">
          <Image
            src={imageSource}
            alt={""}
            width={100}
            height={88}
            className="rounded-full w-[90px] h-[90px]"
          />
        </div>
        <div className="flex-grow">
          <div className="flex justify-between items-start">
            <div>
            <h2 className="text-[18px] font-semibold leading-7 text-slate-800 flex items-center gap-2">
                {applicant.details.personal_information?.full_name}
                {applicant.details.social_media?.linkedin && (
                <a
                  href={`${applicant.details.social_media?.linkedin}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="font-medium text-center text-primary hover:underline text-wrap"
                >
                <FaLinkedin className="bg-white text-primary w-6 h-6" />
                </a>
                )}
              </h2>
              <p className="text-[16px] leading-7 text-slate-600">
                {applicant.details.job_information?.job_title}
              </p>
            </div>
          </div>
          <div className="mt-4 flex gap-4">
            <a
              href={`tel:${applicant.details.personal_information?.phone}`}
              className="flex items-center gap-2 text-sm text-muted-foreground hover:text-primary"
            >
              <Phone className="h-4 w-4" />
              <span className="text-[14px] leading-6 text-slate-700">
                {applicant.details.personal_information?.phone}
              </span>
            </a>
            <a
              href={`mailto:${applicant.details.personal_information?.email}`}
              className="flex items-center gap-2 text-sm text-muted-foreground hover:text-primary"
            >
              <Mail className="h-4 w-4" />
              <span className="text-[14px] leading-6 text-slate-700 hover:text-primary">
                {applicant.details.personal_information?.email}
              </span>
            </a>
          </div>
        </div>
      </div>
    </div>
  );
}
