"use client"

import React, { useState } from "react"
import { Clock } from "lucide-react"
import { Input } from "@/components/ui/input"

interface TimePickerProps extends React.InputHTMLAttributes<HTMLInputElement> {
  placeholder?: string
}

export const TimePicker = React.forwardRef<HTMLInputElement, TimePickerProps>(
  ({ placeholder, onChange, ...props }, ref) => {
    const [showPlaceholder, setShowPlaceholder] = useState(!props.value)

    // Handle the time selection and close the popup
    const handleTimeChange = (e: React.ChangeEvent<HTMLInputElement>) => {
      // Call the original onChange if it exists
      if (onChange) {
        onChange(e)
      }

      // If a time is selected, blur the input to close the popup
      if (e.target.value) {
        e.target.blur()
      }
    }

    return (
      <div className="relative timepicker">
        <Input
          type="time"
          ref={ref}
          {...props}
          onChange={handleTimeChange}
          className={`pl-8 w-full ${showPlaceholder ? "text-transparent" : ""}`}
          onFocus={() => setShowPlaceholder(false)}
          onBlur={(e) => setShowPlaceholder(!e.target.value)}
          style={{ appearance: "textfield" }}
        />
        {showPlaceholder && (
          <span className="absolute left-8 top-1/2 transform -translate-y-1/2 text-slate-500 pointer-events-none">
            {placeholder}
          </span>
        )}
        <Clock
          strokeWidth={1.5}
          className="absolute left-2 top-1/2 transform -translate-y-1/2 h-4 w-4 text-slate-500 pointer-events-none"
        />
      </div>
    )
  },
)

TimePicker.displayName = "TimePicker"

