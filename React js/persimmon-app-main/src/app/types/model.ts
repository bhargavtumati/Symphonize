export interface CompanyDetails {
  companyName: string;
  website: string;
  employees: string;
  industry: string;
  companyLinkedIn: string;
  companyType: string;
}

export interface RecruiterDetails {
  fullName: string;
  whatsappNumber: string;
  designation: string;
  linkedIn: string;
  email: string;
}

export interface JobKeyDetails {
  jobTitle: string;
  jobType: string;
  jobLocation: string;
  workplacetype: string;
  teamsize: string;
  minsalary: number | string;
  maxsalary: number | string;
  workmaxexp: number | string;
  workminexp: number | string;
  target_date: Date | undefined;
}

// Candidate type definition

export interface Candidates {
  about: string[];
  full_name: string[];
  address: string[];
  phone: string[];
  email: string[];
  job_title: string[];
  current_work_at: string[];
  work_experience: string;
  current_ctc: number;
  expected_ctc: number[];
  skills: string[];
  linkedin: string[];
  github: string[];
  industry_type: string[];
  responsibilities: string[];
  company: string[];
  education: string[];
  availability: number;
  workmode: string[];
  transition_behaviour: string;
  company_size: string[];
  team_size: string[];
  applicant_uuid: string;
  stage_uuid: string;
  job_code: string;
  id: string;
  _version_: number;
  _root_: string;
  score: number;
}
export interface PreferenceApiCandidateRespo {
  responseHeader: {
    zkConnected: boolean;
    status: number;
    QTime: number;
    params: {
      json: string;
      _forwardedCount: string;
    };
  };
  response: {
    numFound: number;
    start: number;
    maxScore: number;
    numFoundExact: boolean;
    docs: Candidates;
  };
  status: string;
  id: number;
  applicant_uuid: string;
  email:string[];
  stage_uuid:string;
}

export interface PublishedOnCardProps {
  views: {
    careerPageView: boolean;
    persimmonView: boolean;
    Indeed: boolean;
    linkedInView: boolean;
    monsterJobsView: boolean;
    hiristIconView: boolean;
    googleView: boolean;
  };
  setViews: (label: string, value: boolean) => void; // Accepts label and value
}

// Interfaces for job details

export interface Company {
  number_of_employees: string;
  name: string;
  website: string;
  linkedin: string;
  type: string;
  meta: {
    audit: {
      created_at: number;
      created_by: { email: string };
      updated_at: number;
      updated_by: { email: string };
    };
  };
  industry_type: string;
  id: number;
  domain: string;
}
export interface Salary {
  max_value: number;
  min_value: number;
  errorMessage: String;
}
export interface Skill {
  name: string;
  rating: number;
  pref: string;
  errorMessage: string;
  isEditing: boolean;
  checked: boolean;
}
export interface TeamSize {
  value: string;
  preference: string;
}
export interface SoftSkill {
  name: string;
  min_value: string;
  max_value: string;
  slider_value: number;
  pref: string;
  errorMessage: string;
  isEditing: boolean;
  checked: boolean;
}
export interface IndustryType {
  name: string;
  pref: string;
  max: number;
  min: number;
  isEditing: boolean;
  errorMessage: string;
  checked: boolean;
}
export interface Job {
  team_size: string;
  company_id: number;
  min_salary: number;
  max_salary: number;
  title: string;
  code: string;
  min_experience: number;
  ai_clarifying_questions: { answer: string; question: string }[];
  id: number;
  type: string;
  max_experience: number;
  publish_on_career_page: boolean;
  status: string;
  target_date: string;
  workplace_type: string;
  description: string;
  publish_on_job_boards: any[]; // Adjust the type if necessary
  location: string;
  is_posted_for_client: boolean;
  enhanced_description: enhancedDescription;
  meta: {
    audit: audit;
  };
}
export interface audit {
  created_at: number;
  created_by: { email: string };
  updated_at: number;
  updated_by: { email: string };
}
export interface enhancedDescription {
  salary: Salary;
  skills: Skill[];
  location: {
    first_priority: string;
    second_priority: string;
  };
  workmode: { value: string } | undefined;
  team_size: TeamSize;
  softskills: SoftSkill[];
  company_size: TeamSize;
  availability: number;
  industry_type: IndustryType[];
  responsibilities: string[];
  overall_experience: number;
  transition_behaviour: string | number;
}
export interface JobCardProps {
  job: Job;
  count: ApplicantCounts;
  company: Company;
 
}

export interface ApplicantCounts {
  all_applicants: 0;
  rejected: 0;
  other_stages: Array<{
    stage_uuid: string
    applicant_count: number
  }>
  selected: 0;
  shortlisted: 0;
}
export interface PageHeaderProps {
  code: string | undefined;
  status: string | undefined;
  isLoading:boolean
}
export interface ShareJobCardProps {
  jobTitle: string;
  organizationName: string;
  jobType: string;
  jobLocation: string;
  workExperience: string;
  jobCode: string;
  disable: boolean;
}
export interface JobApplicantsData {
  pagination: Pagination;
}
export interface Pagination {
  total_count: number;
}

export const qualifications = [
  "Class 10",
  "Class 12",
  "Diploma",
  "Degree",
  " B.Tech",
  "M.Tech",
  " PhD",
  "Post Graduate",
];
export const filtertype = ["Include", "Exclude"];
export const companySizes = [
  { value: "1-10", label: "1-10" },
  { value: "11-50", label: "11-50" },
  { value: "51-200", label: "51-200" },
  { value: "201-500", label: "201-500" },
  { value: "501-1000", label: "501-1000" },
  { value: "1001-5000", label: "1001-5000" },
  { value: "5001-10000", label: "5001-10000" },
  { value: "10000+", label: "10000+" },
];

export const teamSizes = [
  { value: "1-5", label: "1-5" },
  { value: "6-10", label: "6-10" },
  { value: "11-20", label: "11-20" },
  { value: "21-50", label: "21-50" },
  { value: "51-100", label: "51-100" },
  { value: "101-200", label: "101-200" },
  { value: "200+", label: "200+" },
];

export const industries = [
  "Technology",
  "Healthcare",
  "Finance",
  "Education",
  "Manufacturing",
];

export const companies = [
  "Example Corp",
  "Tech Solutions",
  "Global Industries",
  "Innovation Ltd",
];
export const workModes = [
  { value: "Any", label: "Any" },
  { value: "Work From Office", label: "Work From Office" },
  { value: "Work From Home", label: "Work From Home" },
  { value: "Hybrid", label: "Hybrid" },
];
export const firstLocation = [
  { value: "Bangalore", label: "Bangalore" },
  { value: "Hyderabad", label: "Hyderabad" },
  { value: "Chennai", label: "Chennai" },
  { value: "Mumbai", label: "Mumbai" },
];

export const secondLocation = [
  { value: "Delhi", label: "Delhi" },
  { value: "Pune", label: "Pune" },
  { value: "Kolkata", label: "Kolkata" },
  { value: "Ahmedabad", label: "Ahmedabad" },
];
export interface FileData {
  name: string;
  size: string;
  progress: number;
  file?: File;
  error?: string;
  type: "pdf" | "docx";
}

export interface PreferedData {
  filters: {
    industry_type: Array<{
      name: string;
      pref: string;
      max: number;
      min: number;
    }>;
    remuneration: {
      name: string;
      max: number;
      min: number;
    };
    current_ctc: string;
    skills: Array<{
      name: string;
      pref: string;
      value: number;
    }>;
    responsibilities: string[];
    pedigree: Array<{
      name: string;
      specifications: Array<{
        spec: string;
        qualification: string;
        institution_name: string;
      }>;
    }>;
    availability: {
      name: string;
      value: number | null;
    };
    workmode: {
      value: string | undefined;
    };
    location: {
      first_priority: string | undefined;
      second_priority: string | undefined;
    };
    soft_skills: Array<{
      name: string;
      pref: string;
      min_value: string;
      max_value: string;
    }>;
    transition_behaviour: Array<{
      name: string;
      preference: string;
      value: number;
    }>;
    advanced_filters: Array<{
      name: string;
      preference: string;
      value: string;
    }>;
  };
}
interface College {
  university: string;
  college: string;
  college_type: string;
  state: string;
  district: string;
}

export const applicantsPreferedData: PreferedData = {
  filters: {
    industry_type: [
      {
        name: "",
        pref: "",
        max: 2,
        min: 1,
      },
    ],
    remuneration: {
      name: "",
      max: 2,
      min: 1,
    },
    current_ctc: "0",
    skills: [
      {
        name: "",
        pref: "",
        value: 0,
      },
    ],
    responsibilities: [""],
    pedigree: [
      {
        name: "",
        specifications: [
          {
            spec: "",
            qualification: "",
            institution_name: "",
          },
        ],
      },
    ],
    availability: {
      name: "",
      value: 0,
    },
    workmode: {
      value: "",
    },
    location: {
      first_priority: "",
      second_priority: "",
    },
    soft_skills: [
      {
        name: "",
        pref: "",
        max_value: "",
        min_value: "",
      },
    ],
    transition_behaviour: [
      {
        name: "",
        preference: "",
        value: 0,
      },
    ],
    advanced_filters: [
      {
        name: "",
        preference: "",
        value: "",
      },
    ],
  },
};
export interface JobInfoProps {
  displayYears: number;
  displayMonths: number;
  current_ctc: number;
  job_location?: string;
  availabilityDays: number;
}

export interface SoftSkillSelectorProps {
  index: number;
  softSkill: SoftSkill;
  handleSoftSkillChange: (index: number, value: string) => void;
  handlePreferedChange: (index: number, value: string) => void;
  handleSearchChange: (event: React.ChangeEvent<HTMLInputElement>) => void;
  handleDoubleClick: (index: number) => void;
  handleBlur: (index: number) => void;
  handleRangeChange: (index: number, value: number[]) => void;
  searchTerm: string;
  filteredSkills: string[];
  softSkills: SoftSkill[];
}

export interface JobLocationSelectorProps {
  label: string;
  placeholder: string;
  selectedLocation: string | undefined;
  onSelect: (location: string) => void;
  jobLocations: string[];
  errorMessage?: string;
  isSubmitted?: boolean;
}
export interface PreferenceSelectProps {
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
}

export interface SalaryRangeFilterProps {
  remuneration: { min_value: number; max_value: number };
  remunerationRange: number;
  checked: boolean;
  addToFilter: () => void;
  handleMinInputChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
  handleMaxInputChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
  handleValueChange: (value: number[]) => void;
  getPosition: (value: number) => number;
}
export interface SelectPaddingFiltersProps {
  entry: any;
  index: number;
  handleChange: (index: number, field: string, value: string) => void;
  filterTypeOptions: string[];
  qualificationOptions: string[];
  institutionOptions: string[];
  industryOptions: string[];
  companyOptions: string[];
  isCompanyForm?: boolean; // Determines whether it's a company form or education form
}
export interface SkillItemProps {
  skill: {
    name: string;
    rating: number;
    pref: string;
    checked: boolean;
    isEditing: boolean;
  };
  index: number;
  handleCheckboxChange: (index: number, isChecked: boolean) => void;
  handleSkillChange: (index: number, value: string) => void;
  handleDoubleClick: (index: number) => void;
  handleSearchChange: React.ChangeEventHandler<HTMLInputElement>;
  searchTerm: string;
  filteredSkills: string[];
  handlePreferenceChange: (index: number, value: string) => void;
  handleRangeChange: (index: number, value: [number]) => void;
  handleInputChange: (
    index: number,
    e: React.ChangeEvent<HTMLInputElement>
  ) => void;
  setSkills: React.Dispatch<React.SetStateAction<any[]>>;
}

export interface Template {
  uuid: string|undefined;
  name: string|undefined;
  body: string;
  default: boolean;
  isActive?: boolean;
  subject:string;
  is_edited?:boolean;
}


export interface InputWithIconsProps {
  containerClassName?: string
  inputClassName?: string
  iconsContainerClassName?: string
  checkIconClassName?: string
  xIconClassName?: string
  placeholder?: string
  value?: string
  onChange?: (e: React.ChangeEvent<HTMLInputElement>) => void
  onCheckClick?: () => void
  onXClick?: () => void
}

export interface ITestMailData {
  from_email: string;
  to_email: string;
  subject: string;
  body: string;
  candidate_name: string;
  job_title: string | undefined;
  job_location: string | undefined;
  recruiter_name: string;
  recruiter_designation: string;
  company_name: string | undefined;
}

export interface Recruiter {
  full_name: string;
  whatsapp_number: string;
  designation: string;
  linkedin_url: string;
  email_id: string;
}

export interface RecruiterResponse {
  message: string;
  recruiter: Recruiter;
  status: number;
}
