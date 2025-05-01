"use client";

import { useState } from "react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { ApplicantCard } from "./applicant-card";
import { BasicDetails } from "./basic-details";
import { Resume } from "./resume";
import type { Applicant, TabType } from "@/app/types/applicants";
import { Skeleton } from "@/components/ui/skeleton";
import SkeletonComponent from "./skeleton/card-skeleton";
import { SkeletonType } from "../utils/constants";

const tabsData = [
  { value: "ai-analysis", label: "AI Analysis", disabled: true },
  { value: "basic-details", label: "Basic Details", disabled: false },
  { value: "resume", label: "Resume", disabled: false },
  { value: "screening", label: "Screening Questions", disabled: true },
  { value: "feedback", label: "Feedback", disabled: true },
  { value: "activity", label: "Activity", disabled: true },
] as const;

interface ApplicantProps {
  applicantData: Applicant | undefined;
  isLoading: boolean
}

export function ApplicantProfile({ applicantData, isLoading }: ApplicantProps) {

  return (
    <div className="space-y-6 bg-white border border-1 border-[#E2E8F0] rounded-lg">
      {isLoading && <>
        <div className="p-6">
          <SkeletonComponent type={SkeletonType.Flat} className="h-5 w-28 ml-auto" />

          <div className="flex gap-6 mt-2">
            <SkeletonComponent type={SkeletonType.Circle} className="w-[88px] h-[88px] ml-2" />

            <div className="flex-grow">
              <div className="flex justify-between items-start">
                <div>
                  <SkeletonComponent type={SkeletonType.Flat} className="w-40 h-6 mb-2" />
                  <SkeletonComponent type={SkeletonType.Flat} className="w-48 h-5" />
                </div>
              </div>

              <div className="mt-4 flex gap-4">
                <SkeletonComponent type={SkeletonType.Flat} className="w-32 h-5" />
                <SkeletonComponent type={SkeletonType.Flat} className="w-48 h-5" />
              </div>
            </div>
          </div>
        </div>
      </>}
      {!isLoading && applicantData && <ApplicantCard applicant={applicantData} isLoading={isLoading} />
      }

      <Tabs defaultValue="basic-details" className="w-full p-1">
        {isLoading ? (
          <Skeleton className="w-full h-[40px] rounded-md"></Skeleton>

        ) : (
          <TabsList className="w-full justify-start h-[40px] bg-[#F1F5F9] rounded-md">
            {tabsData.map((tab) => (
              <TabsTrigger
                key={tab.value}
                value={tab.value}
                disabled={tab.disabled}
                className="px-5 py-1.5 text-[#64748B] text-[14px] data-[state=active]:text-foreground data-[state=active]:bg-white data-[state=active]:border-b-0 rounded-md border border-transparent data-[state=active]:border-border data-[state=active]:border-b-white "
              >
                {tab.label}
              </TabsTrigger>
            ))}
          </TabsList>)}
        <div className="mt-6">
          <TabsContent value="basic-details">
            <BasicDetails applicant={applicantData} isLoading={isLoading} />
          </TabsContent>
          <TabsContent value="resume">
            <Resume applicantData={applicantData} />
          </TabsContent>
          {/* Add more TabsContent components for additional tabs */}
        </div>
      </Tabs>
    </div>
  );
}
