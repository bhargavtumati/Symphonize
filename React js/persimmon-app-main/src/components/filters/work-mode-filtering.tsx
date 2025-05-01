import { applicantsPreferedData, workModes } from "@/app/types/model";
import { useEffect } from "react";
import { IWorkmodeFC } from "@/components/filters/models";
import { Select, SelectContent, SelectGroup, SelectItem, SelectTrigger, SelectValue } from "../ui/select";

export const FilterByWorkmode: React.FC<IWorkmodeFC> = ({ selectedWorkMode, setSelectedWorkMode }) => {

    useEffect(() => {
        applicantsPreferedData.filters.workmode = { value: selectedWorkMode }
    }, [selectedWorkMode])

    const handleSelectChange = (value: string) => {
        setSelectedWorkMode(value);
    };

    return (
        <div className="py-11 px-6 Inter">
            <div className="flex items-center space-x-1 mb-1.5">
                <h1 className="text-lg font-semibold">Work Mode</h1>
            </div>
            {/* Select Dropdown */}
            <div className="w-[381px] flex-shrink-0 ">
                <Select value={selectedWorkMode} onValueChange={handleSelectChange}>
                    <SelectTrigger className="h-10">
                        <SelectValue placeholder="select"></SelectValue>
                    </SelectTrigger>
                    <SelectContent>
                        <SelectGroup>
                            {workModes?.map((mode) => (
                                <SelectItem key={mode.value} value={mode.value}>
                                    {mode.label}
                                </SelectItem>
                            ))}
                        </SelectGroup>
                    </SelectContent>
                </Select>
            </div>
        </div>
    )
};
