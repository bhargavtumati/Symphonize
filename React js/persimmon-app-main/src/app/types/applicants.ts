export interface Applicant {
  details: {
    id: string;
    name: string;
    email: string;
    phone: string;
    designation: string;
    linkedinUrl: string;
    githubUrl: string;
    about: string;
    personal_information: {
      full_name: string;
      email: string;
      gender: string | null;
      date_of_birth: string;
      address: string;
      phone: string;
    };
    job_information: {
      job_title: string;
      department: string;
      current_work_at: string;
      work_experience: string;
      job_location: string | null;
      skills: string[];
      current_ctc: number | null;
      expected_ctc: number | null;
    };
    social_media: {
      linkedin: string;
      github: string;
      instagram:string
      facebook:string
    };
    applied_date: string;
    applicant_image: string;
  };
  job_id: number;
  stage_uuid: string;
  uuid: string;
  job_code:string
}

export interface Rating {
  skill: number;
  communication: number;
  professionalism: number;
}

export type TabType =
  | "ai-analysis"
  | "basic-details"
  | "resume"
  | "screening"
  | "feedback"
  | "activity";
