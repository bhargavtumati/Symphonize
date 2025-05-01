import { applicantsPreferedData } from "@/app/types/model";
import { useEffect, useState } from "react";
import skillList from "@/app/(secure)/dashboard/view-job-page/all-applicants/filtering/skills.json"
import SkillItem from "./skill-Items";
import { filterconfig } from "@/app/utils/filters/config";
import { ISkillsFC } from "@/components/filters/models";


export const FilterBySkills: React.FC<ISkillsFC> = ({ skills, setSkills, setErrorMessage }) => {
    // Check if there are any validation errors in skills
    const hasErrors = skills.some(skill => skill.errorMessage);
    const [searchTerm, setSearchTerm] = useState(""); // State to track the search input
    const [filteredSkills, setFilteredSkills] = useState(skillList); // State for filtered skills

    // Handle search input change
    const handleSearchChange = (e: any) => {
        const value = e.target.value;
        setSearchTerm(value);

        // Filter skills based on search input
        const filtered = skillList.filter((skill) =>
            skill.toLowerCase().startsWith(value.toLowerCase())
        );

        setFilteredSkills(filtered.length > 0 ? filtered : ["No skill found - Add new"]);
    };

    // Update applicantsPreferedData whenever skills change
    useEffect(() => {
        applicantsPreferedData.filters["skills"] = skills
            .filter((skill) => skill.checked) // Include only selected industries
            .map((skill) => ({
                name: skill.name,
                pref: skill.pref,
                value: skill.rating,
            }));
    }, [skills]);

    // Handle changes to skill name
    const handleSkillChange = (index: number, value: string) => {
        if (skills.some((skill, i) => skill.name === value && i !== index)) {
            // Set the error message only for the currently edited industry
            setSkills((prevSkill) => {
                const newSkill = [...prevSkill];
                newSkill[index].errorMessage = "Skill already exists";
                setErrorMessage((prev)=>({...prev,skills:newSkill[index].errorMessage}));
                setSearchTerm("");
                return newSkill;
            });
        } else {
            setSkills((prevSkill) => {
                const newSkill = [...prevSkill];
                if (value === "No skill found - Add new") {
                    newSkill[index].name = searchTerm;
                    setSearchTerm("");
                } else {
                    newSkill[index].name = value;
                    setSearchTerm("");
                }
                newSkill[index].isEditing = false;
                newSkill[index].errorMessage = ""; // Clear error message if it's a unique industry
                setErrorMessage((prev)=>({...prev,skills:newSkill[index].errorMessage}));
                return newSkill;
            });
        }
    };


    const handlePreferenceChange = (index: number, value: string) => {
        setSkills(prevSkills => {
            const updatedSkills = [...prevSkills];
            updatedSkills[index].pref = value;
            return updatedSkills;
        });
    };

    // Handle checkbox toggle
    const handleCheckboxChange = (index: number, isChecked: boolean) => {
        setSkills(prevSkills => {
            const updatedSkills = [...prevSkills];
            updatedSkills[index].checked = isChecked;
            return updatedSkills;
        });
    };

    // Enter editing mode for skill name
    const handleDoubleClick = (index: number) => {
        setSkills(prevSkills => {
            const updatedSkills = [...prevSkills];
            updatedSkills[index].isEditing = true;
            return updatedSkills;
        });
    };

    // Handle numeric input change for rating
    const handleInputChange = (index: number, e: React.ChangeEvent<HTMLInputElement>) => {
        let value = parseInt(e.target.value, 10);
        value = isNaN(value) ? 0 : Math.min(Math.max(value, 0), 10);

        setSkills(prevSkills => {
            const updatedSkills = [...prevSkills];
            updatedSkills[index].rating = value;
            return updatedSkills;
        });
    };

    // Handle slider change for rating
    const handleRangeChange = (index: number, value: number[]) => {
        setSkills(prevSkills => {
            const updatedSkills = [...prevSkills];
            updatedSkills[index].rating = value[0];
            return updatedSkills;
        });
    };

    // Add a new skill
    const addNewSkill = () => {
        if (skills.length >= 25) return;

        setSkills(prevSkills => [
            ...prevSkills,
           {...filterconfig.skills.addSkill},
        ]);
    };

    return (
        <div className="py-11 px-6 Inter">
            <div className="flex items-center space-x-1">
                <h1 className="text-lg font-semibold">Skills</h1>
                <span className="text-sm font-normal text-slate-500">(Proficiency level!)</span>
            </div>

            {skills.map((skill, index) => (
                <div key={index}>
                    <SkillItem
                        key={index}
                        skill={skill}
                        index={index}
                        handleCheckboxChange={handleCheckboxChange}
                        handleSkillChange={handleSkillChange}
                        handleDoubleClick={handleDoubleClick}
                        handleSearchChange={handleSearchChange}
                        searchTerm={searchTerm}
                        filteredSkills={filteredSkills}
                        handlePreferenceChange={handlePreferenceChange}
                        handleRangeChange={handleRangeChange}
                        handleInputChange={handleInputChange}
                        setSkills={setSkills}
                    />
                    {skill.errorMessage && (
                        <div className="ml-10">
                            <p className="text-red-500 text-xs mb-4">{skill.errorMessage}</p>
                        </div>
                    )}
                </div>
            ))}

            <button
                className={`text-base font-normal hover:font-semibold ${skills.length >= 25 || hasErrors
                    ? "text-gray-400 cursor-not-allowed"
                    : "text-primary"
                    }`}
                onClick={addNewSkill}
                disabled={skills.length >= 25 || hasErrors}
            >
                + Add New Skill
            </button>
        </div>
    );
};
