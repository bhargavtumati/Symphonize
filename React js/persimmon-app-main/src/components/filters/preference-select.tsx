import React from "react";
import { Select, SelectContent, SelectGroup, SelectItem, SelectTrigger, SelectValue } from "../ui/select";
import { PreferenceSelectProps } from "@/app/types/model";
import { preferenceOptions } from "@/app/utils/filters/config";
  
  const PreferenceSelect: React.FC<PreferenceSelectProps> = ({ value, onChange, placeholder = "Select" }) => {
  return (
    <div className="w-[155px] flex-shrink-0">
      <Select value={value} onValueChange={onChange}>
        <SelectTrigger className="h-10 pl-[10px]">
          <SelectValue placeholder={placeholder} />
        </SelectTrigger>
        <SelectContent>
          <SelectGroup>
          {preferenceOptions.map((option) => (
            <SelectItem key={option.value} value={option.value}>
              {option.label}
            </SelectItem>
          ))}
          </SelectGroup>
        </SelectContent>
      </Select>
    </div>
  );
};

export default PreferenceSelect;
