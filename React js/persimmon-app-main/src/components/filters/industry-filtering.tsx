import { applicantsPreferedData } from "@/app/types/model";
import { IIndustryFC } from "@/components/filters/models";
import industryTypes from "@/app/multi-form/industry-type.json";
import { useEffect, useState } from "react";
import { validateCompareWorkExp } from "@/app/utils/validations";
import IndustryItem from "@/components/filters/industry-items";
import { filterconfig } from "@/app/utils/filters/config";

export const FilterByIndustry: React.FC<IIndustryFC> = ({ industries, setIndustries, setErrorMessage }) => {
    const[searchTerm, setSearchTerm] = useState("")
    const [filteredIndustries,setFilteredIndustries] = useState(industryTypes)
    const experienceRange = filterconfig.industry.industryExperienceRange;
    const hasErrors = industries.some(industry => industry.errorMessage);

    useEffect(() => {
        // Validate and add only checked industries to the applicantsPreferedData
        applicantsPreferedData.filters["industry_type"] = industries
            .filter((industry) => industry.checked) // Include only selected industries
            .map((industry) => ({
                name: industry.name,
                pref: industry.pref,
                min: industry.min,
                max: industry.max,
            }));
    }, [industries]);

    const handleSearchChange = (e: any) => {
        const value = e.target.value;
        setSearchTerm(value);
        // Filter skills based on search input
        const filtered = industryTypes.filter((industry) =>
            industry.toLowerCase().startsWith(value.toLowerCase())
        );
        setFilteredIndustries(filtered);
    };
    
    const handlePreferenceChange = (index: number, value: string) => {
        setIndustries((prevIndustries) => {
            const newIndustries = [...prevIndustries];
            newIndustries[index].pref = value;
            return newIndustries;
        });
    };

    const handleIndustryChange = (index: number, value: string) => {
        if (industries.some((industry, i) => industry.name === value && i !== index)) {
            // Set the error message only for the currently edited industry
            setIndustries((prevIndustries) => {
                const newIndustries = [...prevIndustries];
                newIndustries[index].errorMessage = "Industry type already exists";
                setErrorMessage((prev)=>({...prev,industry:newIndustries[index].errorMessage}));
                setSearchTerm("");
                return newIndustries;
            });
        } else {
            setIndustries((prevIndustries) => {
                const newIndustries = [...prevIndustries];
                newIndustries[index].name = value;
                newIndustries[index].isEditing = false;
                newIndustries[index].errorMessage = ""; // Clear error message if it's a unique industry
                setErrorMessage((prev)=>({...prev,industry:newIndustries[index].errorMessage}));
                setSearchTerm("")
                return newIndustries;
            });
        }
    };

    const handleDoubleClick = (index: number) => {
        const updatedIndustries = [...industries];
        updatedIndustries[index].isEditing = true; // Enter editing mode
        setIndustries(updatedIndustries);
    };

    const handleBlur = (index: number) => {
        const updatedIndustries = [...industries];
        updatedIndustries[index].isEditing = false; // Exit editing mode on blur
        setIndustries(updatedIndustries);
    };

    const handleValueChange = (index: number, newRange: any) => {
        const updatedIndustries = [...industries];
        const min = Math.min(
            newRange[0] === experienceRange
                ? experienceRange - 1
                : newRange[0],
            newRange[1] - 1
        );
        const max = newRange[0] === experienceRange
            ? experienceRange
            : Math.max(newRange[1], newRange[0] + 1);
        updatedIndustries[index].min = min;
        updatedIndustries[index].max = max;
        setIndustries(updatedIndustries);
    };

    const handleMaxInputChange = (index: number, e: any) => {
        let value = parseInt(e.target.value, 10);
        if (value === 1) {
            value = 1;
        } else {
            value = Math.min(Math.max(value, 2), experienceRange);
        }
        const updatedIndustries = [...industries];
        updatedIndustries[index].max = value;
        const errorMessage = validateCompareWorkExp(updatedIndustries[index].min, updatedIndustries[index].max);
        setIndustries((prevIndustries) => {
            const newIndustries = [...prevIndustries];
            newIndustries[index].errorMessage = errorMessage;
            setErrorMessage((prev)=>({...prev,industry:errorMessage}));
            return newIndustries;
        });

        setIndustries(updatedIndustries);
    };

    const handleMinInputChange = (index: number, e: any) => {
        let value = parseInt(e.target.value, 10);
        value = Math.min(Math.max(value, 1), experienceRange-1); // Constrain the value within 1 to 49
        const updatedIndustries = [...industries];
        updatedIndustries[index].min = value;
        const errorMessage = validateCompareWorkExp(updatedIndustries[index].min, updatedIndustries[index].max);
        setIndustries((prevIndustries) => {
            const newIndustries = [...prevIndustries];
            newIndustries[index].errorMessage = errorMessage;
            setErrorMessage((prev)=>({...prev,industry:errorMessage}));
            return newIndustries;
        });
        setIndustries(updatedIndustries);
    };

    const handleCheckboxChange = (index: number, isChecked: boolean) => {
        setIndustries((prevIndustries) => {
            const updatedIndustries = [...prevIndustries];
            updatedIndustries[index].checked = isChecked;
            return updatedIndustries;
        });
    };
    const addNewIndustry = () => {
        if (industries.length >= 10) return;
        setIndustries([
            ...industries,
            {...filterconfig.industry.addIndustry},
        ]);
    };

    const getPosition = (value: number, experienceRange: any) => {
        return (value / experienceRange) * 100;
    };

    return (
        <div className="py-11 pl-4 pr-0 Inter">
            <div className="flex items-center space-x-1">
                <h1 className="text-lg font-semibold">Industry</h1>
                <span className="text-sm font-normal text-slate-500">(Experience in Years)</span>
            </div>

            {industries?.map((industry, index) => (
                <div key={index}>
                    <IndustryItem
                        industry={industry}
                        index={index}
                        handleCheckboxChange={handleCheckboxChange}
                        handleIndustryChange={handleIndustryChange}
                        handleDoubleClick={handleDoubleClick}
                        handleBlur={handleBlur}
                        handlePreferenceChange={handlePreferenceChange}
                        handleMinInputChange={handleMinInputChange}
                        handleMaxInputChange={handleMaxInputChange}
                        handleValueChange={handleValueChange}
                        handleSearchChange={handleSearchChange}
                        searchTerm={searchTerm}
                        filteredIndustries={filteredIndustries}
                        getPosition={getPosition} // Pass function
                        experienceRange={experienceRange} // Pass range
                        setIndustries={setIndustries} // Pass state updater
                    />
                    {industry.errorMessage && (
                        <div className="ml-10">
                            <p className="text-red-500 text-xs mr-4 mb-4">{industry.errorMessage}</p>
                        </div>
                    )}
                </div>
            ))}

            <button
                className={`text-base font-normal hover:font-semibold ${industries?.length >= 10 || hasErrors ? 'text-gray-400 cursor-not-allowed' : 'text-primary'
                    }`}
                onClick={addNewIndustry}
                disabled={industries?.length >= 10 || hasErrors}
            >
                + Add New Industry
            </button>
        </div>

    );
};