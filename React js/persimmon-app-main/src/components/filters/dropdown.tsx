import React from "react";
import {
  Select,
  SelectTrigger,
  SelectValue,
  SelectContent,
  SelectGroup,
  SelectItem,
} from "../ui/select";

interface DropDownProp {
  searchTerm?: string; // Optional for cases without search
  handleSearchChange?: (event: React.ChangeEvent<HTMLInputElement>) => void;
  filter?: string[]; // Optional for cases with search-based dropdown
  handleChange: (index: number, key?: string, value?: string) => void;
  index: number;
  placeHolder: string;
  options?: string[]; // For Select with predefined options
  type?: "searchable" | "select"; // Determine the dropdown behavior
  value?: string; // To handle selected value in dropdown (useful for Select with predefined options)
  isSelect?: boolean; // Flag to determine if it's a simple Select dropdown
}

const DropDown: React.FC<DropDownProp> = ({
  searchTerm,
  handleSearchChange,
  filter,
  handleChange,
  index,
  placeHolder,
  options,
  type = "searchable",
  value,
  isSelect = false, // Default to false (not using Select component)
}) => {
  if (isSelect) {
    return (
      <div className="w-full">
        <Select
          value={value}
          onValueChange={(value) => handleChange(index, undefined, value)}
        >
          <SelectTrigger className="w-full h-10">

            <SelectValue placeholder={placeHolder} />
          </SelectTrigger>
          
          <SelectContent className="min-w-20">
            <SelectGroup>
              {options?.map((option) => (
                <SelectItem key={option} value={option}>
                  {option === "99" ? ">90" : option}{" "}
                  {/* Special case for availability */}
                </SelectItem>
              ))}
            </SelectGroup>
          </SelectContent>
        </Select>
      </div>
    );
  }

  // Default dropdown behavior (searchable or simple select)
  return (
    <div className="w-full">
      <Select
        value={value}
        onValueChange={(value) => handleChange(index, undefined, value)}
      >
        <SelectTrigger className="w-full h-10">
          <SelectValue placeholder={placeHolder} />
        </SelectTrigger>
        <SelectContent>
          {type === "searchable" ? (
            <>
              <div className="p-2">
                <input
                  type="text"
                  value={searchTerm}
                  onChange={handleSearchChange}
                  placeholder={"Search ".concat(placeHolder)}
                  className="w-full border border-gray-300 rounded-md px-2 py-1 focus:outline-none"
                  autoFocus={false}
                />
              </div>
              {filter?.length ? (
                filter.map((filterdata, idx) => (
                  <option
                    key={idx}
                    value={filterdata}
                    onClick={() => handleChange(index, undefined, filterdata)}
                    className="relative flex w-full cursor-default select-none items-center rounded-sm py-1.5 pl-4 pr-2 text-sm outline-none focus:bg-accent focus:text-accent-foreground data-[disabled]:pointer-events-none data-[disabled]:opacity-50"
                  >
                    {filterdata}
                  </option>
                ))
              ) : (
                <div
                  className="text-gray-500 text-center p-2 select-none cursor-default"
                  style={{ pointerEvents: "none", cursor: "default" }}
                >
                  No match
                </div>
              )}
            </>
          ) : (
            <SelectGroup>
              {options?.map((option) => (
                <SelectItem
                  key={option}
                  value={option}
                  onClick={() => handleChange(index, "filterType", option)}
                >
                  {option}
                </SelectItem>
              ))}
            </SelectGroup>
          )}
        </SelectContent>
      </Select>
    </div>
  );
};

export default DropDown;
