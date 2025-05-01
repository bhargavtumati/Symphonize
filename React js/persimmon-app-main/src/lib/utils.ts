import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export const dateWithoutTimeZone = (date: string): any => {
  // Parse the input date string into a Date object
  const utcDate = new Date(date);

  // Adjust the date to the local timezone
  const localDate = new Date(utcDate.getTime() - utcDate.getTimezoneOffset() * 60000);

  // Format the local date in ISO format with milliseconds and 'Z'
  return localDate.toISOString().slice(0, -1) + 'Z';
};


