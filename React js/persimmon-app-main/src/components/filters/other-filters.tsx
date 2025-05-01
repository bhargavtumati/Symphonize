import { applicantsPreferedData, companySizes, teamSizes } from "@/app/types/model";
import { IOtherFiltersFC } from "@/components/filters/models";
import { useEffect } from "react";
import PreferenceSelect from "./preference-select";
import { Select, SelectContent, SelectGroup, SelectItem, SelectTrigger, SelectValue } from "../ui/select";
import DropDown from "./dropdown";

export const FilterByOther: React.FC<IOtherFiltersFC> = ({ teamSize, setTeamSize, companySize, setCompanySize }) => {

    useEffect(() => {
        applicantsPreferedData.filters["advanced_filters"] = [
            {
                name: "team size",
                preference: teamSize.preference,
                value: teamSize.value,
            },
            {
                name: "company size",
                preference: companySize.preference,
                value: companySize.value,
            },
        ];
    }, [teamSize, companySize])
    return (
        <div className="py-11 px-6 Inter">
            <div className="flex items-center space-x-1 mb-6">
                <h1 className="text-lg font-semibold">Other Preferences</h1>
            </div>
            <div className="space-y-6">
                {/* Company Size Dropdown */}
                <div className="text-sm font-normal  flex items-center space-x-2">
                    <p className="block w-[130px]">Company Size</p>
                    <PreferenceSelect
                        value={companySize?.preference}
                        onChange={(value) => {
                            setCompanySize((prev) => ({ ...prev, preference: value }));
                        }}
                    />
                    <div className="w-[384px] ">
                        <DropDown
                            value={companySize?.value} // Passing the selected value
                            options={companySizes.map((size) => size.value)} // Pass only the values for select options
                            handleChange={(index, key, value) =>
                                setCompanySize((prev) => ({
                                    ...prev,
                                    value: value || '',
                                    preference: prev.preference
                                }))
                            }
                            index={0}
                            placeHolder="Select Company Size"
                            type="select"
                            isSelect={true} // Pass isSelect as true for this specific case
                        />

                    </div>
                </div>

                {/* Team Size Dropdown */}
                <div className="text-sm font-normal  flex items-center space-x-2">
                    <h1 className="block w-[130px]">Team Size</h1>
                    <PreferenceSelect
                        value={teamSize?.preference}
                        onChange={(value) => {
                            setTeamSize((prev) => ({ ...prev, preference: value }));
                        }}

                    />
                    <div className="w-[384px]">
                    <DropDown
                        value={teamSize?.value}  // Pass selected value for team size
                        options={teamSizes.map((size) => size.value)}  // Pass team sizes as options
                        handleChange={(index, key, value) => {
                            setTeamSize((prev) => ({
                                ...prev,
                                value: value || '', // Update team size value
                                preference: prev.preference,  // Keep other properties of teamSize intact
                            }));
                        }}
                        index={1}  // Pass index if necessary for handling different states
                        placeHolder="Select Team Size"  // Placeholder text
                        isSelect={true}  // Use Select dropdown for this case
                    />
                    </div>

                </div>
            </div>
        </div>
    );

};
