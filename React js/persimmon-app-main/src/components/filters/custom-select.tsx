import React from "react";
import {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { TypeIcon as type, LucideIcon } from 'lucide-react';

interface SelectOption {
  value: string;
  label: string;
}

interface CustomSelectProps {
  options: SelectOption[]
  placeholder: string
  value?: string
  onValueChange?: ((value: string) => void)
  contentClassName?: string
  triggerClassName?: string
  icon?: LucideIcon
  onFocus?: (() => void) | null;
  disabled?: boolean;

}

export function CustomSelect({
  options,
  placeholder,
  onValueChange,
  value,
  triggerClassName = "",
  contentClassName = "",
  icon: Icon,
  onFocus=null,
  disabled=false,
}: CustomSelectProps) {
  // Find the selected option's label
  return (
    <Select value={value} onValueChange={onValueChange} disabled={disabled}  onOpenChange={() => {
      if (onFocus) onFocus()
      
    }}>
      <SelectTrigger className={`${triggerClassName}`}
       onFocus={() => {
        if (onFocus)  onFocus()}
      }>
        {Icon && <Icon className="mr-2 h-4 w-4" />}
        <SelectValue placeholder={placeholder}>
        </SelectValue>
      </SelectTrigger>
      <SelectContent 
      className={`${contentClassName}`}>
        <SelectGroup>
          {options.map((option) => (
            <SelectItem key={option.value} value={option.value} >
              {option.label}
            </SelectItem>
          ))}
        </SelectGroup>
      </SelectContent>
    </Select>
  );
}

