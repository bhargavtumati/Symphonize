
type Salary = {
    max_value: number;
    min_value: number;
    errorMessage: String;
}
type Skill = {
    name: string;
    rating: number;
    pref: string;
    errorMessage: string;
    isEditing: boolean;
    checked: boolean;
}
type TeamSize = {
    value: string;
    preference: string;
}
type SoftSkill = {
    name: string;
    min_value: string;
    max_value: string;
    slider_value: number;
    pref: string;
    errorMessage: string;
    isEditing: boolean;
    checked: boolean;
}
type IndustryType = {
    name: string;
    pref: string;
    max: number;
    min: number;
    isEditing: boolean;
    errorMessage: string;
    checked: boolean;
}

export interface  ErrorMessages {
    industry: string,
    remuneration: string,
    skills: string,
    responsibilities: string,
    padding: string,
    availability: string,
    workmode: string,
    location: string,
    softSkills: string,
    transitionBehavior: string,
    otherFilters: string,
}
interface JobRequirement {
    enhanced_description:{
        salary: {
            max_value: number;
            min_value: number;
            errorMessage:string;
        };
        skills: Array<{
            name: string;
            rating: number;
            experience: number;
            pref: string;
            checked?: boolean; 
            errorMessage?: string; 
            isEditing: boolean;
        }>;
        location: {
            first_priority: string;
            second_priority: string;
        };
        workmode: {
            value: string;
        };
        team_size: {
            value: string;
            preference: string;
        };
        softskills: [];
        availability: string;
        company_size: {
            value: string;
            preference: string;
        };
        industry_type: Array<{
            name: string;
            pref: string;
            max: number;
            min: number;
        }>;
        responsibilities: string[];
        overall_experience: number;
        clarifying_questions: string[];
        transition_behaviour: string;
    }
}
export interface IJobDetails{
    job:JobRequirement;
}

export interface IIndustryFC {
    industries: IndustryType[];
    setIndustries: React.Dispatch<React.SetStateAction<IndustryType[]>>
    errorMessage: ErrorMessages;
    setErrorMessage: React.Dispatch<React.SetStateAction<ErrorMessages>>
}


export interface IRemunerationFC {
    remuneration: Salary;
    setRemuneration: React.Dispatch<React.SetStateAction<Salary>>
    checked: boolean;
    setChecked: React.Dispatch<React.SetStateAction<boolean>>
    errorMessage: ErrorMessages
    setErrorMessage: React.Dispatch<React.SetStateAction<ErrorMessages>>
}

export interface ISkillsFC {
    skills: Skill[];
    setSkills: React.Dispatch<React.SetStateAction<Skill[]>>
    errorMessage: ErrorMessages
    setErrorMessage: React.Dispatch<React.SetStateAction<ErrorMessages>>
}

type Responsibilities = {
    text: string;
    checked: boolean;
}

export interface IResponsibilitiesFC {
    responsibilities: Responsibilities[]
    setResponsibilities: React.Dispatch<React.SetStateAction<Responsibilities[]>>
    newResponsibility: string
    setNewResponsibility: React.Dispatch<React.SetStateAction<string>>
    showInputField: boolean
    setShowInputField: React.Dispatch<React.SetStateAction<boolean>>
    errorMessage: ErrorMessages
    setErrorMessage: React.Dispatch<React.SetStateAction<ErrorMessages>>
    responsibilitiesError: string
    setResponsibilitiesError: React.Dispatch<React.SetStateAction<string>>
}
export interface educationEntry {
    filterType: string;
    qualification: string;
    institution: string;
    errorMessage: string;
}
export interface companyEntry {
    filterType: string;
    industry: string;
    company: string;
    errorMessage: string;
}
export interface IPedigreeFC {
    educationEntries: educationEntry[];
    setEducationEntries: React.Dispatch<React.SetStateAction<educationEntry[]>>
    setCompanyEntries: React.Dispatch<React.SetStateAction<companyEntry[]>>;
    companyEntries: companyEntry[];
    isEducationChecked: boolean;
    setIsEducationChecked: React.Dispatch<React.SetStateAction<boolean>>;
    isCompanyChecked: boolean;
    setIsCompanyChecked: React.Dispatch<React.SetStateAction<boolean>>;
    setErrorMessage: React.Dispatch<React.SetStateAction<ErrorMessages>>;
}

export interface IAvailabilityFC {
    setAvailability: React.Dispatch<React.SetStateAction<number | null>>
    availability: number | null
    setAvailabilityCheck: React.Dispatch<React.SetStateAction<boolean>>
    availabilityCheck: boolean
}

export interface IWorkmodeFC {
    selectedWorkMode: string | undefined;
    setSelectedWorkMode: React.Dispatch<React.SetStateAction<string | undefined>>;
    isModified: boolean;
    setIsModified: React.Dispatch<React.SetStateAction<boolean>>
}
export interface ILocationFC {
    firstPriority: string | undefined;
    setFirstPriority: React.Dispatch<React.SetStateAction<string | undefined>>
    secondPriority: string | undefined;
    setSecondPriority: React.Dispatch<React.SetStateAction<string | undefined>>
}
export interface ISoftSkillFC {
    softSkills: SoftSkill[]
    setSoftSkills: React.Dispatch<React.SetStateAction<SoftSkill[]>>
}
export interface ITransitionBehaviorFC {
    transitionBehavior: number | string | null
    setTransitionBehavior: React.Dispatch<React.SetStateAction<number | string | null>>
    transitionPreference: string;
    setTransitionPreference: React.Dispatch<React.SetStateAction<string>>
}
export interface IOtherFiltersFC {
    teamSize: TeamSize;
    setTeamSize: React.Dispatch<React.SetStateAction<TeamSize>>;
    companySize: TeamSize
    setCompanySize: React.Dispatch<React.SetStateAction<TeamSize>>;
}




