import { SoftSkillSelectorProps } from "@/app/types/model";
import PreferenceSelect from "./preference-select";
import { Slider } from "../ui/slider";
import DropDown from "./dropdown";


const SoftSkillSelector: React.FC<SoftSkillSelectorProps> = ({
    index,
    softSkill,
    handleSoftSkillChange,
    handlePreferedChange,
    handleSearchChange,
    handleDoubleClick,
    handleBlur,
    handleRangeChange,
    searchTerm,
    filteredSkills,
    softSkills,
}) => {
    return (
        <div className="flex flex-wrap items-center gap-4 pr-4 pt-4 w-full md:w-fit">
            {/* Checkbox and Label */}
            <div className="flex items-center space-x-2 space-y-0 w-[200px]">
                {softSkill.isEditing ? (
                    <DropDown
                        searchTerm={searchTerm}
                        handleSearchChange={handleSearchChange}
                        filter={filteredSkills}
                        handleChange={(index, _, value) => handleSoftSkillChange(index, value!)}
                        index={index}
                        placeHolder="Soft Skill Name"
                    />
                ) :
                    (<span
                        className="text-sm cursor-pointer truncate w-[200px]"
                        onDoubleClick={() => handleDoubleClick(index)}
                        tabIndex={0}
                        onBlur={() => handleBlur(index)}
                    >
                        {softSkill.name}
                    </span>)

                }
            </div>

            {/* Select Dropdown */}
            <PreferenceSelect
                key={index}
                value={softSkill.pref}
                onChange={(value) => handlePreferedChange(index, value)}
                placeholder="Select a preference"
            />

            {/* Slider */}
            <div className="flex-1 flex items-start relative h-[8px] w-[450px]">
                <Slider
                    max={2}
                    step={1}
                    value={[softSkills[index].slider_value]} // Bind to the updated state
                    onValueChange={(value: number[]) => handleRangeChange(index, value)}
                    className="relative w-full"
                />

                <div className="absolute flex justify-between w-full text-xs text-gray-600 -bottom-5">
                    <span>Basic</span>
                    <span>Medium</span>
                    <span>Advanced</span>
                </div>
            </div>
        </div>
    );
};

export default SoftSkillSelector;