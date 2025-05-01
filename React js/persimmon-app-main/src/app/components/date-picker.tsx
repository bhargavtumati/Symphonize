"use client";

import * as React from "react";
import { CalendarIcon } from "@radix-ui/react-icons";
import { format } from "date-fns";

import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Calendar } from "@/components/ui/calendar";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";

type DateType = {
  date: Date | undefined;
  setDate: React.Dispatch<React.SetStateAction<Date | undefined>>;
  targetFunc: (name: string, value: Date | undefined) => void;
};

export function DatePicker({ date, setDate, targetFunc }: DateType) {
  const [isOpen, setIsOpen] = React.useState(false);

  // Get today's date
  const today = new Date();
  today.setHours(0, 0, 0, 0); // Ensure time is set to start of day

  return (
    <Popover open={isOpen} onOpenChange={setIsOpen}>
      <PopoverTrigger asChild>
        <Button
          variant={"outline"}
          className={cn(
            "w-full justify-start text-left font-normal h-10",
            !date && "text-muted-foreground"
          )}
        >
          <CalendarIcon />
          {date ? (
            <span className="ml-1">{format(date, "PPP")}</span>
          ) : (
            <span className="ml-1 text-slate-400">Select Date</span>
          )}
        </Button>
      </PopoverTrigger>
      <PopoverContent className="w-auto p-0" align="start">
        <Calendar
          mode="single"
          selected={date}
          onSelect={(value) => {
            targetFunc("target_date", value && new Date(value.toUTCString()));
            setDate(value);
            setIsOpen(false); // Close the popover
          }}
          // Disable past dates
          disabled={(date) => date < today}
          initialFocus
        />
      </PopoverContent>
    </Popover>
  );
}
