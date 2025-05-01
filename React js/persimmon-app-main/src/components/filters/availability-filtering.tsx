import { applicantsPreferedData } from "@/app/types/model";
import { IAvailabilityFC } from "@/components/filters/models";
import { useEffect } from "react";
import { Checkbox } from "../ui/checkbox";
import { Slider } from "../ui/slider";
import { Select, SelectContent, SelectGroup, SelectItem, SelectTrigger, SelectValue } from "../ui/select";
import { filterconfig } from "@/app/utils/filters/config";
import DropDown from "./dropdown";
export const FilterByAvailability: React.FC<IAvailabilityFC> = ({ setAvailability, availability, setAvailabilityCheck, availabilityCheck }) => {

    useEffect(() => {
        if (availabilityCheck) {
            applicantsPreferedData.filters.availability = { name: "Can Join in", value: availability };
        }
        else {
            applicantsPreferedData.filters.availability = {
                name: "",
                value: 0,
            }
        }

    }, [availability, availabilityCheck])

    const breakpoints = filterconfig.availability.availabilityBreakPoints

    const getSliderValue = (daysRange: number) => {
        return breakpoints.findIndex(bp => daysRange <= bp);
    };

    const handleRangeChange = (value: number[]) => {
        const updatedAvailability = breakpoints[value[0]];
        setAvailability(updatedAvailability);
    };

    const handleSelectChange = (value: number) => {
        setAvailability(value);
    };

    return (
        <div className="py-11 px-6 Inter">
            <div className="flex items-center space-x-1">
                <h1 className="text-lg font-semibold">Availability</h1>
                <span className="text-sm font-normal text-slate-500">(in Days)</span>
            </div>


            <div className="flex flex-wrap items-center gap-4 p-4">
                {/* Checkbox and Label */}
                <div className="flex items-center space-x-2 min-w-[74px]">
                    <Checkbox checked={availabilityCheck}
                        onCheckedChange={(e) => setAvailabilityCheck(e === true)} />
                    <span className="text-sm cursor-pointer truncate w-[74px]">Can Join in</span>
                </div>
                <span className="flex w-[10px] h-[14px] items-center text-[#94A3B8]">0</span>
                <div className="flex items-center relative h-[8px] w-[451px]">
                    {availability !== null && <Slider
                        defaultValue={[getSliderValue(availability)]}
                        max={filterconfig.availability.availabilityRange}
                        step={1}
                        value={[getSliderValue(availability)]}
                        onValueChange={handleRangeChange}
                    />}
                </div>
                <span className="flex w-[10px] h-[14px] items-center text-[#94A3B8]">{"\u003E"}90</span>

                {/* Dropdown Select */}
                <div className="w-20 ml-4">
                    <DropDown
                        value={availability!=null && availability > 90 ? "90+": availability?.toString()}  // For availability
                        options={breakpoints.map((bp) =>(bp >90 ? "90+": bp.toString()))}  // For availability options
                        handleChange={(index, key, value) => handleSelectChange(value==="90+" ? 99: parseInt(value||""))}
                        index={2}
                        placeHolder="Select Availability"
                        isSelect={true}
                    />
                </div>
            </div>

        </div>
    );
};