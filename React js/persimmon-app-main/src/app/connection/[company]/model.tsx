import { enhancedDescription, audit } from "@/app/types";
export interface JobDetails{
    jobs: Job[];
  };
  export interface Job  {
    title: string;
    id:number;
    max_salary: number;
    min_experience: number;
    max_experience: number;
    location: string;
    description: string;
    min_salary: number;
    workplace_type:string;
    preview:boolean;
    domain:string | string[]
    type:string
    meta: {
      audit: audit;
    }
    code:string;
  };