import { applicantsPreferedData } from "@/app/types/model";
import { ILocationFC } from "@/components/filters/models";
import { useEffect } from "react";
import allCities from "@/app/(secure)/dashboard/create-job/Indian Citites list.json"
import JobLocationSelector from "./Location-items";

export const FilterByLocation: React.FC<ILocationFC> = ({ firstPriority, setFirstPriority, secondPriority, setSecondPriority }) => {
    const jobLocations = Object.values(allCities).flat();
    jobLocations.unshift("Any");

    useEffect(() => {
        applicantsPreferedData.filters.location.first_priority = firstPriority;
        applicantsPreferedData.filters.location.second_priority = secondPriority;
    }, [firstPriority, secondPriority])

    return (
        <div className="py-11 px-6 Inter">
            <div className="flex items-center space-x-1 mb-1.5">
                <h1 className="text-lg font-semibold">Location</h1>
            </div>
            {/* Select Dropdown */}
            <div className="w-1/2 flex-shrink-0 space-y-3 items-center font-normal">
                <div className="flex justify-between items-center">
                    <span className="mr-16">First Priority</span>
                    <JobLocationSelector
                        label=""
                        placeholder="Enter City"
                        selectedLocation={firstPriority}
                        onSelect={(location) => setFirstPriority(location)}
                        jobLocations={jobLocations}
                    />
                </div>
                <div className="flex justify-between items-center ">
                    <span className="mr-10">Second Priority</span>
                    <JobLocationSelector
                        label=""
                        placeholder="Enter City"
                        selectedLocation={secondPriority}
                        onSelect={(location) => setSecondPriority(location)}
                        jobLocations={jobLocations}
                    />
                </div>
            </div>
        </div>
    )
};