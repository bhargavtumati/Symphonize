import React, { useState } from 'react';
import Image from 'next/image';
import { ScrollArea, ScrollBar } from "@/components/ui/scroll-area";
import { cn } from "@/lib/utils";
import { JobCardProps } from '../types';
import { useUpload } from './uploadContext';

interface Stage {
  uuid: string;
  name: string;
}

interface StagesListProps {
  applicants: number
  stages: Stage[];
  jobDetails: JobCardProps | null;
  selectedTab: string;
  stageCounts: Record<string, number>;
  onStageClick: (uuid: string, name: string) => void;
}

const RibbonStages: React.FC<StagesListProps> = ({ applicants, stages, jobDetails, selectedTab, stageCounts, onStageClick }) => {
const counts = jobDetails?.count;
console.log('counts more',counts)
const getStageCount = (stageName: string, stageUuid: string): number => {
  if (!jobDetails || !jobDetails.count) return 0

  const counts = jobDetails.count

  switch (stageName.toLowerCase()) {
    case "all applicants":
      return counts.all_applicants
    case "shortlisted":
      return counts.shortlisted
    case "selected":
      return counts.selected
    case "rejected":
      return counts.rejected
    default:
      const otherStage = counts.other_stages.find((stage) => stage.stage_uuid === stageUuid)
      return otherStage ? otherStage.applicant_count : 0
  }
}

  const { applicantCount } = useUpload()
  return (
    <ScrollArea className="h-full max-w-[calc(100vw-200px)]">
      <div className="flex h-full items-center gap-3">
        <button
          className={cn(
            "whitespace-nowrap px-2 py-1 text-sm transition-colors",
            selectedTab === "All Applicants" && "font-semibold text-primary"
          )}
          onClick={() => onStageClick("", "All Applicants")}
        >
          All Applicants
        <span className="ml-4">{applicantCount > 0 ? applicantCount : applicants}</span>

        </button>
        <Image
          src="/images/Union.png"
          width={20}
          height={21}
          alt="separator"
          className="object-contain"
        />

        <button
          className={cn(
            "whitespace-nowrap px-2 py-1 text-sm text-gray-600 transition-colors",
            selectedTab === "AI Top Results" && "font-semibold text-primary"
          )}
          onClick={() => onStageClick("", "AI Top Results")}
        >
          AI Top Results
        </button>
        <Image
          src="/images/Union.png"
          width={21}
          height={20}
          alt="separator"
          className="object-contain"
        />

        {stages.map((stage, index) => (
          <React.Fragment key={stage.name}>
            <button
              className={cn(
                "whitespace-nowrap px-2 py-1 text-[14px] text-[#64748B] transition-colors",
                selectedTab === stage.name && "font-semibold text-primary"
              )}
              disabled={
                stage.name === "All Applicants" ||
                stage.name === "AI Top Results"
              }
              onClick={() => onStageClick(stage.uuid, stage.name)}
            >
              {stage.name}{" "}
              <span className="ml-2">
              {getStageCount(stage.name, stage.uuid)}
              </span>
            </button>
            {index < stages.length - 1 && (
              <Image
                src="/images/Union.png"
                width={21}
                height={21}
                alt="separator"
                className="object-contain"
              />
            )}
          </React.Fragment>
        ))}
      </div>
      <ScrollBar orientation="horizontal" className="h-2" />
    </ScrollArea>
  );
};

export default RibbonStages;

