import React from "react";
import { ErrorMessages } from "./models";

export const useHandleEntriesChange = (
  setErrorMessage: React.Dispatch<React.SetStateAction<ErrorMessages>>
) => {
  const handleEntriesChange = (
    index: number,
    field: string,
    value: string,
    entries: any[],
    setEntries: React.Dispatch<React.SetStateAction<any[]>>,
    entriesType: "education" | "company"
  ) => {
    const checkFields =
      entriesType === "education"
        ? ["qualification", "institution"]
        : ["industry", "company"];
    const errorKey = entriesType === "education" ? "education" : "industry";

    setEntries((prev) => {
      const newEntries = [...prev];
      newEntries[index] = {
        ...newEntries[index],
        [field]: value,
        errorMessage: "",
      };

      const isDuplicate = newEntries.some((entry, entryIndex) => {
        // Skip comparison if any required field is empty
        if (!entry[checkFields[0]] || !entry[checkFields[1]]) {
          return false;
        }
        // Check for duplicates
        return newEntries.some(
          (e, i) =>
            i !== entryIndex &&
            e[checkFields[0]] === entry[checkFields[0]] &&
            e[checkFields[1]] === entry[checkFields[1]]
        );
      });

      if (isDuplicate) {
        newEntries[index].errorMessage = "Filter already exists";
        setErrorMessage((prev) => ({
          ...prev,
          [errorKey]: "Filter already exists",
        }));
      } else {
        setErrorMessage((prev) => ({ ...prev, [errorKey]: "" }));
      }

      return newEntries;
    });
  };

  return { handleEntriesChange };
};
