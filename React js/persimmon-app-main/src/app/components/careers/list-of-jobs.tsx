import { Card } from '@/components/ui/card';
import React from 'react';
import {Job} from "@/app/connection/[company]/model"
import { CustomizationSettings } from '@/app/types/customization';
import { cn } from '@/lib/utils';


interface ListOfJobsProps {
  jobs: Job[];
  selectedJobIndex: {job: Job | null; index: number | null;};
  handleJobClick: (job: Job, index: number) => void;
  settings:CustomizationSettings | null
}

const ListOfJobsRetrieved: React.FC<ListOfJobsProps> = ({ jobs, selectedJobIndex, handleJobClick , settings}) => {
  return (
    <Card className={`${settings?.darkMode ? 'bg-slate-800':'bg-[#f8fafc]'} border-none`} style={{ fontFamily: settings?.fontStyle }}>
      <h3 className={`font-semibold border-b w-full p-4 ${settings?.darkMode ? 'text-slate-50': 'text-black'}`}>All Jobs</h3>
      <div>
        {jobs.slice(0, 5).map((job, index) => (
          <div
            key={index}
            className={`p-3 border-b ${settings?.darkMode ? 'hover:bg-slate-700':'hover:bg-slate-50'} cursor-pointer`}
            onClick={() => handleJobClick(job, index)} 
            
          >
            <div
              className={cn("font-semibold mb-1", {
                "text-primary": selectedJobIndex.index === index,
                "text-slate-700": !settings?.darkMode && selectedJobIndex.index !== index,
                "text-slate-200": settings?.darkMode && selectedJobIndex.index !== index,
              })}
            >
              {job.title}
            </div>
            <div className={`text-[10px] font-medium ${settings?.darkMode ? 'text-slate-300':'text-slate-500'}`}>
              {`${job?.min_experience} - ${job?.max_experience}`} Years | {job.location} |{" "}
              {job.type?.replace(/_/g, " ")} | {job.workplace_type?.replace(/_/g, " ")}
            </div>
          </div>
        ))}
      </div>
    </Card>
  );
};

export default ListOfJobsRetrieved;
