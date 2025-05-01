import { SkillItemProps } from "@/app/types/model";
import { Checkbox } from "../ui/checkbox";
import { Input } from "../ui/input";
import PreferenceSelect from "./preference-select";
import { Slider } from "../ui/slider";
import { filterconfig } from "@/app/utils/filters/config";
import React from 'react';
import DropDown from "./dropdown";

const SkillItem: React.FC<SkillItemProps> = ({
    skill,
    index,
    handleCheckboxChange,
    handleSkillChange,
    handleDoubleClick,
    handleSearchChange,
    searchTerm,
    filteredSkills,
    handlePreferenceChange,
    handleRangeChange,
    handleInputChange,
    setSkills,
}) => {
    return (
        <div className="flex flex-wrap items-center gap-4 p-4">
            {/* Checkbox and Label */}
            <div className="flex items-center space-x-2 min-w-[225px]">
                <Checkbox
                    checked={skill.checked || false}
                    onCheckedChange={(isChecked) => handleCheckboxChange(index, isChecked === true)}
                />
                <div className="flex items-center space-x-2 space-y-0 w-[200px]">
                {skill.isEditing ? (
                        <DropDown
                            searchTerm={searchTerm}
                            handleSearchChange={handleSearchChange}
                            filter={filteredSkills}
                            handleChange={(index, _, value) => handleSkillChange(index, value!)}
                            index={index}
                            placeHolder="Skill Name"
                        />
                    

                ) : (
                    <span
                        className="text-sm cursor-pointer truncate max-w-[220px]]"
                        onDoubleClick={() => handleDoubleClick(index)}
                        tabIndex={0}
                    >
                        {skill.name}
                    </span>
                )}
                </div>
            </div>

            {/* Preference Dropdown */}
            <PreferenceSelect
                key={index}
                value={skill.pref}
                onChange={(value) => handlePreferenceChange(index, value)}
                placeholder="Select a preference"
            />

            {/* Skill Rating */}
            <span className="flex w-[10px] h-[14px] items-center text-[#94A3B8]">0</span>
            <div className=" flex flex-wrap w-[450px] items-center relative h-[8px]">
                <Slider
                    defaultValue={[skill.rating]}
                    max={filterconfig.skills.skillRange}
                    step={1}
                    value={[skill.rating]}
                    onValueChange={(value: any) => handleRangeChange(index, value)}
                />
            </div>
            <span className="flex w-[10px] h-[14px] items-center text-[#94A3B8]">10</span>

            {/* Rating Input */}
            <Input
                className="w-20 h-10 flex-shrink-0"
                type="number"
                placeholder="Value"
                value={skill.rating}
                max={10}
                min={0}
                onChange={(e) => handleInputChange(index, e)}
                onBlur={(e) => {
                    let value = parseInt(e.target.value, 10);
                    value = isNaN(value) ? 0 : Math.min(Math.max(value, 0), 10);
                    setSkills((prevSkills: any) => {
                        const updatedSkills = [...prevSkills];
                        updatedSkills[index].rating = value;
                        return updatedSkills;
                    });
                }}
            />
        </div>
    );
};

export default SkillItem;