'use client'
import { Card } from "@/components/ui/card";
import { useEffect, useState } from 'react';
import { applyFilters } from "./filteringdata";
import { apiService } from "@/app/api/service";
import { auth } from "@/app/components/firebaseConfig";
import {SoftSkill, IndustryType, Salary, Skill, TeamSize,JobCardProps} from "@/app/types/model";
import {educationEntry,companyEntry} from "@/components/filters/models";
import { IJobDetails } from "@/components/filters/models";
import { useRouter } from "next/navigation";
import { filterconfig } from "@/app/utils/filters/config";
import ResetChanges from "@/components/filters/reset-changes";
import { FilterByIndustry } from "@/components/filters/industry-filtering";
import { FilterByRemuneration } from "@/components/filters/remuneration-filtering";
import { FilterBySkills } from "@/components/filters/skills-filtering";
import { FilterByResponsibilities } from "@/components/filters/responsibilities-filtering";
import { FilterByPedigree } from "@/components/filters/pedigree-filtering";
import { FilterByAvailability } from "@/components/filters/availability-filtering";
import { FilterByWorkmode } from "@/components/filters/work-mode-filtering";
import { FilterByLocation } from "@/components/filters/location-filtering";
import { FilterBySoftskills } from "@/components/filters/soft-skill-filtering";
import { FilterByTransitionBehavior } from "@/components/filters/transition-behavior-filtering";
import { FilterByOther } from "@/components/filters/other-filters";

export default function Filtering() {
    const router = useRouter();
    const [activeIndex, setActiveIndex] = useState<number>(0);
    const [jobId, setJobId] = useState<string>("");
    const [jobCode, setJobCode] = useState<string>("");
    const [jobDetails, setJobDetails] = useState<IJobDetails | undefined>();
    const [industries, setIndustries] = useState<IndustryType[]>([]);
    const [isModified, setIsModified] = useState<boolean>(false);
    const [remuneration, setRemuneration] = useState<Salary>({
        min_value: 1,
        max_value: 2,
        errorMessage: ""
    });
    const [checked, setChecked] = useState<boolean>(true);
    const [skills, setSkills] = useState<Skill[]>([]);
    const [responsibilities, setResponsibilities] = useState<{ text: string; checked: boolean }[]>([]);
    const [educationEntries, setEducationEntries] = useState<educationEntry[]>([
        {
            filterType: "",
            qualification: "",
            institution: "",
            errorMessage: "",
        },
    ]);
    const [companyEntries, setCompanyEntries] = useState<companyEntry[]>([
        {
            filterType: "",
            industry: "",
            company: "",
            errorMessage: "",
        },
    ]);
    const [isEducationChecked, setIsEducationChecked] = useState<boolean>(true);
    const [isCompanyChecked, setIsCompanyChecked] = useState<boolean>(true);
    const [availability, setAvailability] = useState<number | null>(null);
    const [availabilityCheck, setAvailabilityCheck] = useState<boolean>(true)
    const [selectedWorkMode, setSelectedWorkMode] = useState<string | undefined>(undefined);
    const [firstPriority, setFirstPriority] = useState<string | undefined>(undefined);
    const [secondPriority, setSecondPriority] = useState<string | undefined>(undefined);
    const [softSkills, setSoftSkills] = useState<SoftSkill[]>([]);
    const [newResponsibility, setNewResponsibility] = useState<string>("");
    const [showInputField, setShowInputField] = useState<boolean>(false);
    const [responsibilitiesError, setResponsibilitiesError] = useState<string>("")
    const [errorMessage, setErrorMessage] = useState({
        industry: "",
        remuneration: "",
        skills: "",
        responsibilities: "",
        padding: "",
        availability: "",
        workmode: "",
        location: "",
        softSkills: "",
        transitionBehavior: "",
        otherFilters: "",
    });
    const hasErrors = Object.values(errorMessage).some((error) => error.trim() !== "");
    const [transitionBehavior, setTransitionBehavior] = useState<number | string | null>(null);
    const [trasitionPreference, setTransitionPreference] = useState<string>(filterconfig.transitionBehavior.transitionPreference)
    const [teamSize, setTeamSize] = useState<TeamSize>(filterconfig.otherFilter.teamSize);
    const [companySize, setCompanySize] = useState<TeamSize>(filterconfig.otherFilter.companySize);
    const [resetChanges,setResetChanges] = useState<boolean>(false)

    const commonProps = {
        errorMessage: errorMessage,
        setErrorMessage: setErrorMessage,
    };

    const industryProps = {
        industries: industries,
        setIndustries: setIndustries,
    };

    const remunerationProps = {
        remuneration: remuneration,
        setRemuneration: setRemuneration,
        checked: checked,
        setChecked: setChecked,
    };

    const skillsProps = {
        skills: skills,
        setSkills: setSkills,
    };

    const responsibilitiesProps = {
        responsibilities: responsibilities,
        setResponsibilities: setResponsibilities,
        newResponsibility: newResponsibility,
        setNewResponsibility: setNewResponsibility,
        showInputField: showInputField,
        setShowInputField: setShowInputField,
        responsibilitiesError: responsibilitiesError,
        setResponsibilitiesError: setResponsibilitiesError,
    };

    const pedigreeProps = {
        educationEntries: educationEntries,
        setEducationEntries: setEducationEntries,
        companyEntries: companyEntries,
        setCompanyEntries: setCompanyEntries,
        isEducationChecked: isEducationChecked,
        setIsEducationChecked: setIsEducationChecked,
        isCompanyChecked: isCompanyChecked,
        setIsCompanyChecked: setIsCompanyChecked,
    };

    const availabilityProps = {
        availability: availability,
        setAvailability: setAvailability,
        availabilityCheck: availabilityCheck,
        setAvailabilityCheck: setAvailabilityCheck,
    };

    const workmodeProps = {
        selectedWorkMode: selectedWorkMode,
        setSelectedWorkMode: setSelectedWorkMode,
        isModified: isModified,
        setIsModified: setIsModified,
    };

    const locationProps = {
        firstPriority: firstPriority,
        setFirstPriority: setFirstPriority,
        secondPriority: secondPriority,
        setSecondPriority: setSecondPriority,
    };
    const softskillsProps = {
        softSkills: softSkills,
        setSoftSkills: setSoftSkills,
    };
    const transitionBehaviorProps = {
        transitionBehavior: transitionBehavior,
        setTransitionBehavior: setTransitionBehavior,
        transitionPreference: trasitionPreference,
        setTransitionPreference: setTransitionPreference,
    };
    const otherFilterProps = {
        teamSize: teamSize,
        setTeamSize: setTeamSize,
        companySize: companySize,
        setCompanySize: setCompanySize,
    };

    useEffect(() => {
        const searchParams = new URLSearchParams(window.location.search);
        const jobIdFromParams = searchParams.get("jobId");
        const jobCodeFromParam = searchParams.get("job_code")
        if (jobIdFromParams) setJobId(jobIdFromParams);
        if (jobCodeFromParam) setJobCode(jobCodeFromParam);
    }, []);

    useEffect(() => {
        //if (!jobId) return; // Wait until jobId is available
        const unsubscribe = auth.onAuthStateChanged(async (user) => {
            if (user) {
                try {
                    const idToken = await user.getIdToken();
                    if (idToken) {
                        const jobData = await apiService(`/jobs/${jobId}`, 'GET', null); // Use jobId for API call
                        if (!jobData) throw new Error("Failed to fetch job details")
                        setJobDetails(jobData)
                    }
                } catch (error: any) {
                    console.log(error.message);
                } finally {

                }
            } else {

            }
        });

        return () => unsubscribe();
    }, [jobId,resetChanges]);

    useEffect(() => {
        if (!jobDetails) return;
        const { industry_type, salary, skills, transition_behaviour, location,availability,softskills,responsibilities,workmode } = jobDetails?.job.enhanced_description || {};
        if (industry_type) {
            const initialIndustries = industry_type.map((industry) => ({
                ...industry,
                isEditing: false,
                errorMessage: "",
                checked: true,
            }));
            setIndustries(initialIndustries);
        }
        if (skills) {
            if (Array.isArray(skills) && skills.length > 0) {
                const updatedSkills = skills.map(skill => ({
                    ...skill,
                    errorMessage: "",
                    checked: skill.checked || true,
                }));
                setSkills(updatedSkills);
            }
        }
        if (salary) {
            // Safely set the remuneration state with fallback values
            setRemuneration({
                min_value: salary.min_value ? Math.round(salary.min_value) : 0, // Divide by 100000 if value exists
                max_value: salary.max_value ? Math.round(salary.max_value) : 0,
                errorMessage: salary.errorMessage || "", // Use errorMessage if provided, else empty string
            });
        }

        if (transition_behaviour) {
            if (typeof transition_behaviour === "string" && transition_behaviour.includes("-")) {
                // If the value is like "0-5", take the max value
                const [min, max] = transition_behaviour.split("-").map(Number);
                setTransitionBehavior(max); // Set the max value (5 in this case)
            } else if (typeof transition_behaviour === "number" && transition_behaviour <= 5 && transition_behaviour >= 0) {
                // If the value is a number greater than 5, set it to ">5"
                setTransitionBehavior(transition_behaviour); // You can modify this to ">5" if required
            } else if (typeof transition_behaviour === "number" && transition_behaviour > 5) {
                setTransitionBehavior(5);
            }
            else {
                setTransitionBehavior(0);
            }
        }
        if (location) {
            setFirstPriority(location?.first_priority);
            setSecondPriority(location?.second_priority);
        }
        if(availability && typeof(availability)==="number"){
            setAvailability(availability);
        }else{
            setAvailability(0);
        }
        if(softskills){
            setSoftSkills(softskills);
        }
        if (responsibilities){
            setResponsibilities(
                responsibilities.map((responsibility: string) => ({
                    text: responsibility,
                    checked: true, // Default to checked
                }))
            );
        }
        if(workmode)setSelectedWorkMode(workmode.value);
    }, [jobDetails]);



    const items = [
        "Industry",
        "Remuneration",
        "Skills",
        "Responsibilities",
        "Pedigree",
        "Availability",
        "Work Mode",
        "Location",
        "Softskills",
        "Transition Behaviour",
        "Other Preferences"
    ];

    const renderContent = (index: string) => {
        switch (index) {
            case "Industry":
                return <FilterByIndustry {...commonProps} {...industryProps} />;
            case "Remuneration":
                return <FilterByRemuneration {...commonProps} {...remunerationProps} />;
            case "Skills":
                return <FilterBySkills {...commonProps} {...skillsProps} />;
            case "Responsibilities":
                return <FilterByResponsibilities {...commonProps} {...responsibilitiesProps} />;
            case "Pedigree":
                return <FilterByPedigree {...commonProps} {...pedigreeProps} />;
            case "Availability":
                return <FilterByAvailability {...commonProps} {...availabilityProps} />;
            case "Work Mode":
                return <FilterByWorkmode {...commonProps} {...workmodeProps} />;
            case "Location":
                return <FilterByLocation {...commonProps} {...locationProps} />;
            case "Softskills":
                return <FilterBySoftskills {...commonProps} {...softskillsProps} />;
            case "Transition Behaviour":
                return <FilterByTransitionBehavior {...commonProps} {...transitionBehaviorProps} />;
            case "Other Preferences":
                return <FilterByOther {...commonProps} {...otherFilterProps} />;
        }
    };

    const backToApplicants = () => {
        router.push(`/dashboard/view-job-page/all-applicants?jobId=${jobId}`)
    }

    return (
        <div className="w-full mx-[28px]">
            <div className="flex flex-col bg-gray-200 Inter my-5 bg-transparent">
                <h4 className="text-xl font-semibold">Advanced Preferences</h4>
                <p className="text-base font-normal">Modify your preferences to re-rank</p>
            </div>

            {/* Responsive grid: stacks vertically at 425px or below */}
            <div className="grid gap-0 sm:grid-cols-2 md:grid-cols-[0.9fr,4fr]">
                {/* First Card */}
                <div className="min-h-[712px]">
                    <Card className="flex flex-col h-full p-9 space-y-3 text-base font-normal text-slate-500 border-0 border-r border-slate-300 rounded-none rounded-tl-lg">                        {items.map((item, index) => (
                        <p
                            key={index}
                            onClick={() => setActiveIndex(index)} // Set active index on click
                            className={`cursor-pointer ${activeIndex === index ? 'text-primary font-bold' : ''}`}
                        >
                            {item}
                        </p>
                    ))}
                    </Card>
                </div>

                {/* Second Card */}
                <div className="min-h-[712px]">
                    <Card className="h-full border-0  border-slate-300 rounded-none rounded-tr-lg">
                        {renderContent(items[activeIndex])}
                    </Card>
                </div>
            </div>

            {/* Third Card */}
            <ResetChanges
                backToApplicants={backToApplicants}
                applyFilters={applyFilters}
                hasErrors={hasErrors}
                jobId={jobId}
                jobCode={jobCode} 
                resetChanges = {resetChanges}
                setResetChanges = {setResetChanges}
            />
        </div>
    );
}