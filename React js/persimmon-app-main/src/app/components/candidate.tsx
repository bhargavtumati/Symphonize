import React, { useState } from "react";
import Image from "next/image";
import { Briefcase, IndianRupee, MapPin, DoorOpen, Loader2 } from "lucide-react";
import { useRouter } from "next/navigation";
// Define props interface
import { Candidates } from "../types";
import CandidateMatch from "./CandidateMatch";
import Link from "next/link";
import { Input } from "@/components/ui/input";
import { apiService } from "../api/service";
import { toast } from "@/components/hooks/use-toast";
import { Skeleton } from "@/components/ui/skeleton";
import { JobCard } from "./careers/job-card";
import { JOB_COLUMNS } from "../utils/constants";
import { faL } from "@fortawesome/free-solid-svg-icons";
interface CandidateCardProps {
  candidate: Candidates;
  isSelected: boolean;
  toggleSelection: () => void;
  stages: { uuid: string; name: string }[];
  originalStages: { uuid: string; name: string }[];
  disable?: boolean 
}

interface InfoItem {
  icon: React.ElementType;
  content: string;
}

function CandidateCard({
  candidate,
  isSelected,
  toggleSelection,
  stages,
  disable=false,
  originalStages,
}: CandidateCardProps) {
  //const { name, position, experience, salary, location, joiningTime, summary } =
  //candidate;
  const full_name = candidate?.full_name || "";
  const job_title = candidate?.job_title || "";
  const work_experience = Number(candidate?.work_experience || 0);
  const current_ctc = candidate?.current_ctc || 0;
  const current_work_at = candidate?.company?.[0] || "";
  const job_location = candidate?.address?.[0] || "";
  const availabilityDays = candidate?.availability || 0;
  const [loading, setLoading] = useState<boolean>(false)
  const years = Math.floor(work_experience);
  const months = Math.round((work_experience - years) * 12);

  const displayYears = isNaN(work_experience) ? 0 : years;
  const displayMonths = isNaN(work_experience) ? 0 : months || 0;

  const formatSalary = (ctc: number): string => {
    const lpa = ctc * 12;
    const formattedCTC = Math.round(lpa / 100000);
    return `${formattedCTC} LPA`;
  };

  const linkedIn = candidate.linkedin && candidate.linkedin.length > 0;
  const searchParams = new URLSearchParams(window.location.search);
  const jobId = searchParams.get("jobId");
  const jobCode = searchParams.get("jobCode");

  const handleMoveTo = async (stageId: string) => {
    setLoading(true)
    const payload = {
      applicant_uuids: [candidate.applicant_uuid],
      stage_uuid: stageId,
    };

    try {
      const result = await apiService(
        `/applicants?job_id=${jobId}`,
        "PATCH",
        payload
      );
      window.location.reload();
      console.log(result)
    } catch (error: any) {
      toast({
        variant: "destructive",
        title: "Error on Moving applicants",
        description: error.message || "An unexpected error occurred",
      });
    } finally {
      setLoading(false)
    }
  };
  const infoItems: InfoItem[] = [
    {
      icon: Briefcase,
      content: `${displayYears} Years ${displayMonths} months`,
    },
    {
      icon: IndianRupee,
      content: 'N/A',
    },
    {
      icon: MapPin,
      content: 'N/A',
    },
    {
      icon: DoorOpen,
      content: 'N/A',
    },
  ];
  const confirmInfoItems = [
    { label: "Work experience" },
  ];

  const router = useRouter();

  const applicantsPage = (applicantId: string, jobId:string | null) => {
    const status = disable ? "Closed" : "Active";
    router.push(`/dashboard/view-job-page/all-applicants/${applicantId}?jobId=${jobId}&jobCode=${jobCode}&status=${status}`);
  };

  return (
   
        <div className="bg-white rounded-lg shadow-sm border border-gray-100" >
          <div className="p-4 cursor-pointer">
            <div className="flex items-start justify-between">
              <div className="flex items-start gap-4">
                <Input
                  type="checkbox"
                  checked={isSelected}
                  onChange={toggleSelection}
                  className="h-3 w-3 rounded border-gray-300"
                />
                <div onClick={() => applicantsPage(candidate.applicant_uuid, jobId)}>
                  <div className="flex items-center gap-2 mb-1">
                    <h3 className="text-lg font-semibold text-gray-900 hover:text-primary cursor-pointer" >
                      {full_name}
                    </h3>
                    {linkedIn && (
                      <Link
                        href={candidate.linkedin[0]}
                        target="_blank"
                        rel="noopener noreferrer"
                      >
                        <Image
                          src="/images/applicants/Linkedin2.png"
                          alt="LinkedIn"
                          width={20}
                          height={20}
                          className="opacity-80"
                        />
                      </Link>
                    )}
                  </div>
                  <p className="text-gray-600 text-sm mb-3">
                    {job_title}{" "}
                    {current_work_at && <span>@ {current_work_at}</span>}
                  </p>

                  <div className="flex flex-wrap gap-2">
                    {infoItems.map((item, index) => (
                      <div
                        key={index}
                        className="inline-flex items-center px-3 py-1.5 bg-gray-50 rounded-full text-sm text-gray-600"
                      >
                        <item.icon className="w-4 h-4 mr-2 text-gray-500" />
                        <span>{item.content}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              <div className="flex items-center gap-4" onClick={() => applicantsPage(candidate.applicant_uuid, jobId)}>
                <ul className="space-y-1">
                  {confirmInfoItems.map((item, index) => (
                    <li
                      key={index}
                      className="flex items-center gap-2 text-gray-500 text-sm"
                    >
                      <Image
                        src="/images/check.png"
                        width={16}
                        height={16}
                        alt=""
                        className="opacity-80"
                      />
                      <span>{item.label}</span>
                    </li>
                  ))}
                </ul>
                <CandidateMatch score={candidate.score} />
              </div>
            </div>
          </div>

          <div className="flex items-center justify-between p-4 bg-teal-50 border-t border-teal-100">
            <div className="flex items-center gap-3 max-w-[70%]">
              <Image
                src="/images/AIIcon.png"
                width={32}
                height={32}
                alt=""
                className="mt-1 h-[32px] w-[32px]"
              />
              <p className="text-sm text-gray-600 leading-relaxed">
                To achieve high career growth through hard work and perseverance and
                keep myself dynamic, visionary and competitive with the changing
                scenario of the world.
              </p>
            </div>
            <div className="flex items-center gap-3">
              <span className="text-sm text-gray-600">Move to</span>
              <select
                className={`px-4 py-2 bg-white border border-gray-200 rounded-lg text-sm text-gray-600 focus:outline-none focus:ring-2 focus:ring-teal-500 ${disable ? 'cursor-not-allowed' : 'cursor-pointer'}`}
                onChange={(e) => handleMoveTo(e.target.value)}
                value={candidate.stage_uuid}
                disabled={disable}
              >
                <option value="">Select</option>
                {originalStages?.map((stage) => (
                  <option key={stage.uuid} value={stage.uuid}>
                    {stage.name}
                  </option>
                ))}
              </select>
            </div>
          </div>
       </div>
  );
}

export default CandidateCard;
