import { applicantsPreferedData } from "@/app/types/model";
import { ISoftSkillFC } from "@/components/filters/models";
import softSkillsList from "@/app/(secure)/dashboard/view-job-page/all-applicants/filtering/soft-skills.json";
import { useEffect, useState } from "react";
import SoftSkillSelector from "./soft-skill-items";
import { filterconfig } from "@/app/utils/filters/config";

export const FilterBySoftskills: React.FC<ISoftSkillFC> = ({softSkills, setSoftSkills }) => {
    const [searchTerm, setSearchTerm] = useState(""); // State to track the search input
    const [filteredSkills, setFilteredSkills] = useState(softSkillsList); // State for filtered skills

    const handleSearchChange = (e: any) => {
        const value = e.target.value;
        setSearchTerm(value);

        // Filter skills based on search input
        const filtered = softSkillsList.filter((softSkill) =>
            softSkill.toLowerCase().startsWith(value.toLowerCase())
        );

        setFilteredSkills(filtered.length > 0 ? filtered : ["No skill found - Add new"]);
    };

    useEffect(() => {
        applicantsPreferedData.filters["soft_skills"] = softSkills
            .map((skill) => ({
                name: skill.name,
                pref: skill.pref,
                min_value: skill.min_value,
                max_value: skill.max_value
            }));
    }, [[softSkills]])


    const handleSoftSkillChange = (index: number, value: string) => {
        if (softSkills.some((softSkill, i) => softSkill.name === value && i !== index)) {
            // Set the error message only for the currently edited industry
            setSoftSkills((prevSoftSkill) => {
                const newSoftSkill = [...prevSoftSkill];
                newSoftSkill[index].errorMessage = "Soft skill type already exists";
                setSearchTerm("");
                return newSoftSkill;
            });
        } else {
            setSoftSkills((prevSoftSkill) => {
                const newSoftSkill = [...prevSoftSkill];
                if (value === "No skill found - Add new") {
                    newSoftSkill[index].name = searchTerm;
                    setSearchTerm("");
                } else {
                    newSoftSkill[index].name = value;
                    setSearchTerm("");
                }
                newSoftSkill[index].isEditing = false;
                newSoftSkill[index].errorMessage = "";
                return newSoftSkill;
            });
        }
    };
    const handlePreferedChange = (index: number, value: string) => {
        setSoftSkills((prevSoftSkill) => {
            const newSoftSkill = [...prevSoftSkill];
            newSoftSkill[index].pref = value;
            return newSoftSkill;
        });
    };

    const handleDoubleClick = (index: number) => {
        const updatedSoftSkills = [...softSkills];
        updatedSoftSkills[index].isEditing = true; // Enter editing mode
        setSoftSkills(updatedSoftSkills);
    };

    const handleBlur = (index: number) => {
        const updatedSoftSkills = [...softSkills];
        updatedSoftSkills[index].isEditing = false; // Exit editing mode on blur
        setSoftSkills(updatedSoftSkills);
    };



    const handleRangeChange = (index: number, value: number[]) => {
        const updatedSoftSkills = [...softSkills];
        if (value[0] === 0) {
            updatedSoftSkills[index].min_value = "0";
            updatedSoftSkills[index].max_value = "4";
            updatedSoftSkills[index].slider_value = value[0] // Basic
        } else if (value[0] === 1) {
            updatedSoftSkills[index].min_value = "5";
            updatedSoftSkills[index].max_value = "7";
            updatedSoftSkills[index].slider_value = value[0]  // Medium
        } else {
            updatedSoftSkills[index].min_value = "8";
            updatedSoftSkills[index].max_value = "10";
            updatedSoftSkills[index].slider_value = value[0] // Advanced
        }
        setSoftSkills(updatedSoftSkills); // Trigger re-render
    };



    const addNewSkill = () => {
        if (softSkills.length >= 25) return;
        setSoftSkills([
            ...softSkills,
            {...filterconfig.softSkills.addSoftSkill},
        ]);
    };

    return (
        <div className="py-11 px-6 Inter">
            <div className="flex items-center space-x-1">
                <h1 className="text-lg font-semibold">Softskills</h1>
            </div>

            {softSkills.map((softSkill, index) => (
                <div key={index}>
                    <SoftSkillSelector
                        key={index}
                        index={index}
                        softSkill={softSkill}
                        handleSoftSkillChange={handleSoftSkillChange}
                        handlePreferedChange={handlePreferedChange}
                        handleSearchChange={handleSearchChange}
                        handleDoubleClick={handleDoubleClick}
                        handleBlur={handleBlur}
                        handleRangeChange={handleRangeChange}
                        searchTerm={searchTerm}
                        filteredSkills={filteredSkills}
                        softSkills={softSkills}
                    />
                    {softSkill.errorMessage && (
                        <div className="mt-2">
                            <p className="text-red-500 text-xs mr-4 mb-4">{softSkill.errorMessage}</p>
                        </div>
                    )}
                </div>
            ))}
            <button
                className={`text-base font-normal hover:font-semibold ${softSkills.length >= 25 ? 'text-gray-400 cursor-not-allowed' : 'text-primary'
                    }`}
                onClick={addNewSkill}
                disabled={softSkills.length >= 25}
            >
                + Add New Soft Skill
            </button>
        </div>

    );
};