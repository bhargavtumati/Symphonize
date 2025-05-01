"use client";
import React, { useState, useEffect, useRef } from "react";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import citiesData from "../Indian Citites list.json"; // Corrected spelling
import AILearnings from "../AILearnings";
import { JobKeyDetails } from "../../../../types/model";
import { DatePicker } from "@/app/components/date-picker";
import { invalidInput } from "@/app/utils/validations";
import { CustomSelect } from "@/components/filters/custom-select";
import { JOB_TYPE, WORK_TYPE, TEAM_SIZE  } from "@/app/utils/constants";
import { set } from "lodash";
interface ErrorType {
  jobTitle: string;
  jobType: string;
  jobLocation: string;
  workplacetype: string;
  teamsize: string;
  salary: string;
  workExp: string;
  target_date: string;
}

interface StepProps {
  data: JobKeyDetails;
  onChange: (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>
  ) => void;
  onBlur: (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => void;
  errors: Partial<ErrorType>;
  onJobLocationSelect: (jobLocation: string) => void;
  onBack: () => void;
  onNext: () => void;
  handleTargetFunc: (name: string, value: Date | undefined) => void;
}

// Helper function to trigger onChange for Select component
const handleSelectChange = (
  name: string,
  value: string,
  onChange: (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => void
) => {
  const event = {
    target: {
      name,
      value,
    },
  } as React.ChangeEvent<HTMLInputElement | HTMLSelectElement>;
  onChange(event);
};
const Step1JobKeyDetails: React.FC<StepProps> = ({
  data,
  onChange,
  onBlur,
  errors,
  onJobLocationSelect,
  onNext,
  handleTargetFunc,
}) => {
  const [isSubmitted, setIsSubmitted] = useState(false);
  const [searchQuery, setSearchQuery] = useState(data.jobLocation);
  const [filteredJobLocation, setFilteredJobLocation] = useState<string[]>([]);
  const [showDropdown, setShowDropdown] = useState(false);
  const [showSearchList, setShowSearchList] = useState(true);
  const [date, setDate] = React.useState<Date | undefined>(data.target_date);
  const dropdownRef = useRef<HTMLDivElement>(null);
  useEffect(() => {
    if (data.jobLocation) {
      setSearchQuery(data.jobLocation);
    }
    if (data.target_date) {
      setDate(data.target_date);
    }
  }, [data.jobLocation, data.target_date]);

  useEffect(() => {
    if (searchQuery) {
      const allCities = Object.values(citiesData).flat();
      const filteredCities = allCities.filter((city: string) =>
        city.toLowerCase().startsWith(searchQuery.toLowerCase())
      );
      if (allCities.includes(searchQuery)) {
        setShowSearchList(false);
      } else {
        setShowSearchList(true);
      }

      // Set the filtered cities
      setFilteredJobLocation(filteredCities);
      setShowDropdown(true);
    } else {
      setFilteredJobLocation([]);
      setShowDropdown(false);
    }
    if (!searchQuery && data.jobLocation) {
      errors.jobLocation = "Please select the Job location";
    }
  }, [searchQuery, citiesData]);


  const handleSelectJobLocation = (jobLocation: string) => {
    onJobLocationSelect(jobLocation);
    setSearchQuery(jobLocation);
    setFilteredJobLocation([]);
    setShowDropdown(false);
    setShowSearchList(false); // Hide the dropdown after selection
    setShowDropdown(false);
  };
  const handleClickOutside = (e: any) => {
    // Close dropdown if clicking outside of it
    if (dropdownRef.current && !dropdownRef.current.contains(e.target)) {
      setShowSearchList(false);
      setShowDropdown(false);
    }
  };

  useEffect(() => {
    // Add mousedown event listener to close the dropdown on any click
    if (showSearchList || showDropdown) {
      document.addEventListener('mousedown', handleClickOutside);
    } else {
      document.removeEventListener('mousedown', handleClickOutside);
    }
    // Cleanup the event listener on unmount or when dropdown is closed
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [showSearchList, showDropdown]);

  return (
    <div className="flex flex-col md:flex-row gap-4 mt-4">
      <Card className="w-full md:w-[70%] border-none">
        <h1 className="font-semibold text-xl pt-6 pl-6">Job Key Details</h1>
        <div className="p-12 pt-2">
          <div className="flex flex-row space-x-4 pt-4">
            {/* Job Title */}
            <div className="flex flex-col flex-1">
              <label className="mb-2 font-medium">Title</label>
              <Input
                type="text"
                name="jobTitle"
                placeholder="Title that describes the role"
                value={data.jobTitle}
                onChange={onChange}
                onFocus={() => setShowDropdown(false)}
                className="h-10 mt-1 block w-full px-3 py-2 border rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm placeholder:text-slate-400"
              />
              {isSubmitted && errors.jobTitle && (
                <p className="text-red-500 text-xs mt-1">{errors.jobTitle}</p>
              )}
            </div>
            {/* Job Type */}
            <div className="flex flex-col flex-1" style={{ cursor: "default" }}> 
              <label className="mb-3 font-medium">Job type</label>
              <CustomSelect
                options={JOB_TYPE}
                value={data.jobType}
                onValueChange={(value) =>
                  handleSelectChange("jobType", value, onChange)
                }
                onFocus={() => setShowDropdown(false)} 
                placeholder="Select"
                triggerClassName={ `
                  ${!data.jobType ? "text-slate-400" : "text-black"}`
                }
              />
                
              {isSubmitted && errors.jobType && (
                <p className="text-red-500 text-xs mt-1">{errors.jobType}</p>
              )}
            </div>
          </div>

          <div className="flex flex-row space-x-4 pt-4">
            {/* Workplace Type */}
            <div className="flex flex-col flex-1">
              <label className="mb-2 font-medium">Workplace type</label>
              <CustomSelect
               options={ WORK_TYPE}
               value={data.workplacetype}
                onValueChange={(value) =>
                  handleSelectChange("workplacetype", value, onChange)
                }
                onFocus={() => setShowDropdown(false)} 
                placeholder="Select"
                triggerClassName={
                  !data.workplacetype ? "text-slate-400" : "text-black"
                }  
              />
                
              {isSubmitted && errors.workplacetype && (
                <p className="text-red-500 text-xs mt-1">
                  {errors.workplacetype}
                </p>
              )}
            </div>
            {/* Job Location */}
            <div className="flex flex-col flex-1 relative" ref={dropdownRef}>
              <label className="mb-1 font-medium">Job Location</label>
              <input
                type="text"
                name="jobLocation"
                placeholder="Enter City"
                autoComplete="off"  
                value={searchQuery}
                onChange={(e) => {
                  const value = e.target.value;
                  if (/^[^0-9]*$/.test(value)) {
                    setSearchQuery(value);
                  }
                }}
                onFocus={() => {
                  if (searchQuery) setShowDropdown(true);
                }}
                className="h-10 mt-1 block w-full px-3 py-2 border rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm placeholder:text-slate-400"
              />
              {showSearchList && showDropdown && (
                <ul className="absolute bg-white border rounded-md mt-[75px] max-h-60 overflow-auto z-10 w-[100%]">
                  {filteredJobLocation.length > 0 ? (
                    filteredJobLocation.map((jobLocation) => (
                      <li
                        key={jobLocation}
                        onClick={() => handleSelectJobLocation(jobLocation)}
                        className={`px-4 py-2 cursor-pointer hover:bg-gray-200 ${data.jobLocation === jobLocation ? "bg-gray-100" : ""}`}
                      >
                        {jobLocation}
                      </li>
                    ))
                  ) : (
                    <li className="px-4 py-2 text-gray-500">Location not found</li>
                  )}
                </ul>
              )}
              {(data.jobLocation ||
                (isSubmitted && errors.jobLocation)) && (
                  <p className="text-red-500 text-xs mt-1">
                    {errors.jobLocation}
                  </p>
                )}
            </div>
          </div>

          <div className="flex flex-row space-x-4 pt-4">
            {/* Team Size */}
            <div className="flex flex-col flex-1">
              <label className="mb-2 font-medium">Project Team Size</label>
              <CustomSelect
              options={TEAM_SIZE}
              placeholder="Select"
              value={data.teamsize}
                onValueChange={(value) =>
                  handleSelectChange("teamsize", value, onChange)
                }
                onFocus={() => setShowDropdown(false)} 
                contentClassName={"max-h-[200px] w-full"}
                triggerClassName={
                  !data.teamsize ? "text-slate-400" : "text-black"
                } 
               
              />
               
              {isSubmitted && errors.teamsize && (
                <p className="text-red-500 text-xs mt-1">{errors.teamsize}</p>
              )}
            </div>
            <div className="flex flex-col flex-1">
              <label className="mb-2 font-medium">
                Work Experience (in years)
              </label>
              <div className="flex flex-row items-center">
                <Input
                  type="number"
                  name="workminexp"
                  placeholder="Min"
                  min="1"
                  max="49"
                  value={data.workminexp}
                  onChange={onChange}
                  onBlur={onBlur}
                  onKeyDown={(e) => {
                    if (invalidInput[e.key as keyof typeof invalidInput]) {
                      e.preventDefault();
                    }
                  }}
                  className="h-10 w-[50%] placeholder-shown placeholder:text-slate-400"
                />
                <span className="mx-2 px-1">to</span>
                <Input
                  type="number"
                  name="workmaxexp"
                  placeholder="Max"
                  max="50"
                  min="2"
                  value={data.workmaxexp}
                  onChange={onChange}
                  onBlur={onBlur}
                  onKeyDown={(e) => {
                    if (invalidInput[e.key as keyof typeof invalidInput]) {
                      e.preventDefault();
                    }
                  }}
                  className="h-10 w-[50%] placeholder-shown placeholder:text-slate-400"
                />
              </div>
              {isSubmitted && errors.workExp && (
                <p className="text-red-500 text-xs mt-1">{errors.workExp}</p>
              )}
            </div>
          </div>
          <div className="flex flex-row space-x-4 pt-4">
            <div className="flex flex-col flex-1">
              <label className="mb-2 font-medium">Salary (in LPA)</label>
              <div className="flex flex-row items-center">
                <Input
                  type="number"
                  name="minsalary"
                  placeholder="₹ Min Salary"
                  value={data.minsalary}
                  onChange={onChange}
                  onBlur={onBlur}
                  onKeyDown={(e) => {
                    if (invalidInput[e.key as keyof typeof invalidInput]) {
                      e.preventDefault();
                    }
                  }}
                  min="1"
                  max="99"
                  className="h-10 w-[50%] placeholder-shown placeholder:text-slate-400"
                />
                <span className="mx-2 px-1">to</span>
                <Input
                  type="number"
                  name="maxsalary"
                  value={data.maxsalary}
                  placeholder="₹ Max Salary"
                  onChange={onChange}
                  onBlur={onBlur}
                  onKeyDown={(e) => {
                    if (invalidInput[e.key as keyof typeof invalidInput]) {
                      e.preventDefault();
                    }
                  }}
                  max="100"
                  min="2"
                  className="h-10 w-[50%] placeholder-shown placeholder:text-slate-400"
                />
              </div>
              {isSubmitted && errors.salary && (
                <p className="text-red-500 text-xs mt-1">{errors.salary}</p>
              )}
            </div>
            <div className="flex flex-col flex-1">
              <label className="mb-2 font-medium">Target Date</label>
              <DatePicker
                date={date}
                setDate={setDate}
                targetFunc={handleTargetFunc}
              />
              {isSubmitted && errors.target_date && (
                <p className="text-red-500 text-xs mt-1">
                  {errors.target_date}
                </p>
              )}
            </div>
          </div>

          <div className="flex justify-end space-x-4 mt-14">
            <Button
              type="button"
              onClick={() => {
                const hasError = Object.values(errors).some(
                  (error) => error !== undefined && error !== ""
                );
                setIsSubmitted(true); // Trigger validation messages
                if (!hasError) {
                  onNext(); // Move to the next step if there are no errors
                }
              }}
              className="flex w-24 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
            >
              Next
            </Button>
          </div>
        </div>
      </Card>
      {/* <AILearnings /> */}
    </div>
  );
};

export default Step1JobKeyDetails;
