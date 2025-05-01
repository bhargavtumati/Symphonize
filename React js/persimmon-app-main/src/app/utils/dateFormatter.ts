import { format, parseISO } from "date-fns";

export const formatDate = (
  dateInput?: string | number,
  dateFormat: string | string ="dd/MM/yyyy"
): string => {
  if (!dateInput) {
    return "Invalid Date";
  }

  let date: Date;

  if (typeof dateInput === "string") {
    // Check if the string is a valid ISO 8601 date
    if (isNaN(Date.parse(dateInput))) {
      return "Invalid Date";
    }
    date = parseISO(dateInput);
  } else {
    // Assume it's a Unix timestamp in seconds
    date = new Date(dateInput * 1000);
  }

  if (isNaN(date.getTime())) {
    return "Invalid Date";
  }

  return format(date, dateFormat);
};

export const formatISODate = (isoString?: string): string => {
  if (!isoString) {
    return "Invalid Date";
  }
  const date = new Date(isoString);
  if (isNaN(date.getTime())) {
    return "Invalid Date";
  }

  return format(date, "dd/MMM/yyyy");
};



