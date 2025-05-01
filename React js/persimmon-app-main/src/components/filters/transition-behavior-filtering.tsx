import { applicantsPreferedData } from "@/app/types/model";
import { ITransitionBehaviorFC } from "@/components/filters/models";
import { useEffect } from "react";
import PreferenceSelect from "./preference-select";
import { Slider } from "../ui/slider";
import { Select, SelectContent, SelectGroup, SelectItem, SelectTrigger, SelectValue } from "../ui/select";
import { filterconfig } from "@/app/utils/filters/config";
import { cond } from "lodash";

export const FilterByTransitionBehavior: React.FC<ITransitionBehaviorFC> = ({ transitionBehavior, setTransitionBehavior, transitionPreference, setTransitionPreference }) => {
    // Store a single value
    const breakpoints = filterconfig.transitionBehavior.transitionBreakPoints; 

    // This function parses the value coming from the backend and sets the appropriate values for slider and input field.

    useEffect(() => {
        applicantsPreferedData.filters.transition_behaviour = [{ name: filterconfig.transitionBehavior.transitionName, preference: transitionPreference, value: Number(transitionBehavior) }];
    }, [transitionBehavior, transitionPreference])

    const handleRangeChange = (value: number[]) => {
        setTransitionBehavior(breakpoints[value[0]]);
    };

    const handleSelectChange = (value: number) => {
        setTransitionBehavior(value);
    };

    const getSliderValue = (daysRange: number) => {
        return breakpoints.findIndex(bp => daysRange <= bp);
    };

    return (
        <div className="py-11 px-6 Inter">
            <div className="flex items-center space-x-1">
                <h1 className="text-lg font-semibold">Transition behavior</h1>
                <span className="text-sm font-normal text-slate-500">(in Years)</span>
            </div>

            {/* Single value input and slider */}
            <div className="flex flex-wrap items-center gap-4 p-4">
                <div className="flex items-center space-x-2 min-w-[74px]">
                    <h1 className="block w-[200px]">Avg. Duration in <br/>Previous Companies</h1>
                    <PreferenceSelect
                        value={transitionPreference}
                        onChange={setTransitionPreference}
                        placeholder="Good to have"
                    />
                </div>

                <span className="flex w-[10px] h-[14px] items-center text-[#94A3B8]">0</span>

                <div className="flex items-center relative h-[8px] w-[451px]">
                    <Slider
                        defaultValue={[getSliderValue(Number(transitionBehavior))]}
                        max={filterconfig.transitionBehavior.transitionRange}
                        step={1}
                        value={[getSliderValue(Number(transitionBehavior))]}
                        onValueChange={handleRangeChange}
                    />
                </div>

                <span className="flex w-[10px] h-[14px] items-center text-[#94A3B8]">{"\u003E"}5</span>

                {/* Dropdown Select */}
                <div className="w-20 ml-4">
                    <Select
                        value={Number(transitionBehavior) > 5 ? "5+" : transitionBehavior?.toString()} // Convert to string for comparison with SelectItem values
                        onValueChange={(value) => handleSelectChange( value === "5+" ? 50 : parseInt(value))}
                    >
                        <SelectTrigger className="w-full">
                            <SelectValue placeholder="value">
                            {transitionBehavior != null && Number(transitionBehavior) > 5 ? "5+" : transitionBehavior?.toString()} {/* Explicitly handle 0 */}
                            </SelectValue>
                        </SelectTrigger>
                        <SelectContent className="min-w-20">
                            <SelectGroup>
                                {breakpoints.map((bp) => (
                                    <SelectItem key={bp} value={bp>5 ? "5+" : bp.toString()}>
                                        {bp > 5 ? "5+" : bp}
                                    </SelectItem>
                                ))}
                            </SelectGroup>
                        </SelectContent>
                    </Select>
                </div>
            </div>
        </div>
    );
};
