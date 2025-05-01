import { JobLocationSelectorProps } from "@/app/types/model";
import React, { useState, useRef, useEffect } from "react";


const JobLocationSelector: React.FC<JobLocationSelectorProps> = ({
  label,
  placeholder,
  selectedLocation,
  onSelect,
  jobLocations,
  errorMessage,
  isSubmitted = false,
}) => {
  const [searchQuery, setSearchQuery] = useState(selectedLocation || ""); // Initialize with pre-selected location
  const [showDropdown, setShowDropdown] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  const filteredJobLocations = jobLocations.filter((location) =>
    location.toLowerCase().startsWith(searchQuery.toLowerCase())
  );

  const handleSelectLocation = (location: string) => {
    onSelect(location);
    setSearchQuery(location);
    setShowDropdown(false);
  };

  const handleOutsideClick = (event: MouseEvent) => {
    if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
      setShowDropdown(false);
    }
  };

  const handleScroll = () => {
    setShowDropdown(false);
  };

  useEffect(() => {
    document.addEventListener("click", handleOutsideClick);
    window.addEventListener("scroll", handleScroll);
    return () => {
      document.removeEventListener("click", handleOutsideClick);
      window.removeEventListener("scroll", handleScroll);
    };
  }, []);

  return (
    <div className="flex flex-col flex-1 relative" ref={dropdownRef}>
      <label className="mb-1 font-medium">{label}</label>
      <input
        type="text"
        name="jobLocation"
        placeholder={placeholder}
        value={searchQuery}
        onChange={(e) => {
          const value = e.target.value;
          if (/^[^0-9]*$/.test(value)) {
            setSearchQuery(value);
          }
        }}
        onFocus={() => {
          setShowDropdown(true);
        }}
        className="h-10 mt-1 block w-full px-3 py-2 border rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
      />

      {showDropdown && filteredJobLocations.length > 0 && (
        <ul className="absolute bg-white border rounded-md mt-[50px] max-h-60 overflow-auto z-10 w-full shadow-lg">
          {filteredJobLocations.map((jobLocation) => (
            <li
              key={jobLocation}
              onClick={() => handleSelectLocation(jobLocation)}
              className={`px-4 py-2 cursor-pointer hover:bg-gray-200 ${
                selectedLocation === jobLocation ? "bg-gray-100" : ""
              }`}
            >
              {jobLocation}
            </li>
          ))}
        </ul>
      )}

      {(selectedLocation ||
        (!searchQuery && isSubmitted && errorMessage)) && (
        <p className="text-red-500 text-xs mt-1">{errorMessage}</p>
      )}
    </div>
  );
};

export default JobLocationSelector;
