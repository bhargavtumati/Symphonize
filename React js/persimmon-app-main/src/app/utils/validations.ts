// src/utils/validation.utils.ts

export const validateFullName = (fullName: string): string => {
  if (!fullName) return "Full Name is Required";
  const trimmedName = fullName.trim();
  if (!/^[a-zA-Z\s]+$/.test(trimmedName))
    return "Full name should only contain alphabets";
  if (/^\s|\s$/.test(fullName) || /\s{2,}/.test(fullName))
    return "Please check for improper spaces";
  if (trimmedName.length < 3)
    return "Full name should be at least 3 characters";
  if (trimmedName.length > 20)
    return "Full name cannot be more than 20 characters";
  if (!/^[A-Za-z]+\s[A-Za-z]+$/.test(trimmedName))
    return "Please enter your full name, in 'First name Last name' format";
  return "";
};

export const validateEmail = (email: string): string => {
  const allowedDomains = [
    "gmail.com",
    "outlook.com",
    "yahoo.com",
    "icloud.com",
    "protonmail.com",
    "proton.me",
    "gmx.com",
    "mail.ru",
    "yandex.com",
    "yandex.ru",
    "zoho.com",
    "aol.com",
    "mail.com",
    "consultant.com",
    "teacher.com",
  ]
  const [localPart, domain] = email.split("@")
  return /^[a-zA-Z0-9.%+]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/.test(email) && allowedDomains.includes(domain)? "" : "Enter a valid email ID"
}

export const validateWhatsAppNumber = (number: string): string => {
  if (!number) return "Whatsapp Number is Required";
  if (!/^[0-9]+$/.test(number))
    return "Whatsapp number can contain numeric values only";
  if (number.length !== 10)
    return "Please enter your valid 10 digit Whatsapp number";
  if (!/^[6-9]/.test(number)) return "Please enter a valid Whatsapp number";
  return "";
};

export const validateLinkedIn = (url: string): string => {
  if (!url) return "LinkedIn URL is Required";
  const linkedinRegex = /^https:\/\/(www\.)?linkedin\.com\/in\/[a-zA-Z0-9-_]+$/;
  if (!linkedinRegex.test(url)) return "Please enter valid LinkedIn URL";
  return "";
};


export const validateWebsite = (website: string): string => {
  const trimmedWebsite = website.trim();
  const urlWithoutProtocol = trimmedWebsite.replace(/^https?:\/\//i, "").replace(/^www\./i, "");
  const mainDomain = urlWithoutProtocol.replace(/\.(com|net|org|in)$/i, "");
  if (!trimmedWebsite) return "Website is Required";
  if (!/^(https?:\/\/www\.|www\.)/i.test(trimmedWebsite)) {
    return "URL must start with  https://www. or www.";
  }
  if (/\s/.test(trimmedWebsite)) {
    return "The URL cannot contain spaces";
  }
  if (mainDomain.length < 3) {
    return "Website should be at least 3 characters";
  }
  if (mainDomain.length > 100) {
    return "Website cannot be more than 100 characters";
  }
   if (!/\.(com|net|org|in)$/i.test(urlWithoutProtocol)) {
    return "Please enter a valid domain name";
  }
  const websiteRegex =
    /^(https?:\/\/)?([\w\d-]+\.)+[\w\d]{2,}(\/[\w\d-._~:?#[\]@!$&'()*+,;=]*)?$/i;
  if (!websiteRegex.test(trimmedWebsite)) {
    return "Please enter a valid URL";
  }
  return "";
};


export const validateEmployees = (employees: string): string => {
  if (!employees) return "Company Size is Required";
  return "";
};

export const validateIndustry = (industry: string, filteredIndustries?: string[]): string => {
  if (!industry) return "Industry Type  is Required";
  if (filteredIndustries?.length === 0 || !filteredIndustries?.includes(industry))   return "Please enter a valid Industry Type";
 
  return "";
};

export const validateDesignation = (designation: string): string => {
  if (!designation) return "Designation is Required";
  const trimmedDesignation = designation.trim();
  if (designation !== trimmedDesignation)
    return "Please check for improper spaces";
  if (!/^[a-zA-Z\s]+$/.test(trimmedDesignation))
    return "Designation should only contain alphabets";
  if (/\s{2,}/.test(trimmedDesignation))
    return "Please check for improper spaces";
  if (trimmedDesignation.length < 2)
    return "Designation should be at least 2 characters";
  if (trimmedDesignation.length > 20)
    return "Designation cannot be more than 20 characters";
  return "";
};

export const validateCompanyName = (companyName: string): string => {
  if (!companyName) return "Company Name is Required";

  const trimmedCompanyName = companyName.trim();

  if (companyName !== trimmedCompanyName)
    return "Please check for improper spaces";

  if (/\s{2,}/.test(trimmedCompanyName))
    return "Please check for improper spaces";

  if (trimmedCompanyName.length < 3)
    return "Company name should be at least 3 characters";

  if (trimmedCompanyName.length > 50)
    return "Company name cannot be more than 50 characters";

  // Only allow alphabets, numbers, spaces, and specific special characters (., -, &, ')
  if (!/^[a-zA-Z0-9\s\.\-&']+$/.test(trimmedCompanyName))
    return "Company name can only contain letters, numbers, spaces, and special characters (., -, &, ')";

  return "";
};


export const validateCompanyLinkedIn = (companyLinkedIn: string): string => {
  const trimmedLinkedIn = companyLinkedIn.trim();
  if (!trimmedLinkedIn) return "Company LinkedIn is Required";
  if (!/^https?:\/\//i.test(trimmedLinkedIn)) {
    return "URL must start with http:// or https://";
  }
  if (!/^https:\/\/(www\.)?linkedin\.com/i.test(trimmedLinkedIn)) {
    return "URL must be a LinkedIn link";
  }
  const linkedinRegex = /^https:\/\/(www\.)?linkedin\.com\/company\/([a-zA-Z0-9_-]{3,})\/$/;
  if (!linkedinRegex.test(trimmedLinkedIn)) {
    return "Please enter a valid Company LinkedIn URL";
  }
  return "";
};

export const validateCompanyType = (companytype: string): string => {
  const trimmedComanyType = companytype.trim()
  if (!companytype) return "Company Type is Required";
  if (trimmedComanyType !== companytype)
    return "please select company Type"
  return "";
};

export const validateJobTitle = (title: string): string => {
  if (!title) {
    return "Please provide the Job Title";
  }
  const specialCharPattern = /[^a-zA-Z0-9\s]/;
  if (specialCharPattern.test(title)) {
    return "Please enter letters or numbers only";
  }
  if (title.startsWith(" ") || title.endsWith(" ") || /\s{2,}/.test(title)) {
    return "Please check for any extra spaces.";
  }
  if (title.length < 3 || title.length > 50) {
    return "Job title must be between 3 and 50 characters.";
  }
  return "";
};

export const validateJobType = (type: string): string => {
  return type.trim() ? "" : "Please select the Job Type";
};

export const validateJobLocation = (location: string): string => {
  return location.trim() ? "" : "Please select the Job location";
};

export const validateWorkplaceType = (place: string): string => {
  return place.trim() ? "" : "Please select the Workplace Type";
};

export const validateTeamSize = (size: string): string => {
  return size.trim() ? "" : "Please select the Team size";
};

export const validateSalary = (salary: any): string => {
  const salaryStr = String(salary).trim();
  if (!salaryStr) {
    return "Please provide the salary";
  }
  const hasInvalidFullStops = /^[.]|[.]{2,}|[.]$/.test(salaryStr);
  if (hasInvalidFullStops) {
    return "Please enter a valid salary format";
  }

  // Allow only integers or numbers with a single decimal point
  const isValidDecimal = /^[0-9]+(\.[0-9])?$/.test(salaryStr);
  if (!isValidDecimal) {
    return "Enter only one digit after the decimal";
  }

  return "";
};


export const validateCompareSalaries = (
  minSalary: string | number,
  maxSalary: string | number
): string => {
  const minSalaryNum = parseFloat(minSalary.toString().trim());
  const maxSalaryNum = parseFloat(maxSalary.toString().trim());
  if (minSalaryNum  === maxSalaryNum) {
    return "Minimum salary cannot be equal than maximum salary";
  }
  if (minSalaryNum > maxSalaryNum) {
    return "Minimum salary cannot be greater to maximum salary";
  }
  return "";
};

export const validateWorkExp = (experience: any): string => {
  const experienceStr = String(experience).trim();

  if (!experienceStr) {
    return "Please provide the experience";
  }
  const isValidDecimal = /^[0-9]+(\.[0-9])?$/.test(experienceStr);
  if (!isValidDecimal) {
    return "Enter only one digit after the decimal";
  }
  return "";
};


export const validateCompareWorkExp = (
  minExp: string | number,
  maxExp: string | number
): string => {
  const minWorkExp = parseFloat(minExp.toString().trim());
  const maxWorkExp = parseFloat(maxExp.toString().trim());
  if (minWorkExp === maxWorkExp) {
    return "Minimum experience cannot be equal to maximum experience";
  }
  if (minWorkExp > maxWorkExp) {
    return "Minimum experience cannot be greater than maximum experience";
  }
  return "";
};

export const validateJobDescription = (description: string): string => {
  return description.trim().length >= 10
    ? ""
    : "Description must be at least 10 characters.";
};

// export const validateAIField = (aiInput: string): string => {
//   return aiInput.trim() ? "" : "This field is required.";
// };

export const validateTargetDate = (target_date: Date | undefined): string => {
  return target_date ? "" : "Please provide the target date."
}
export function validateResponsibility(newResponsibility:string, responsibilities:any) {
  // Check for invalid characters
  if (!/^[A-Za-z0-9\s.\-)\(\,]+$/.test(newResponsibility)) {
      return "Please enter valid characters (Alphanumeric, spaces, .-).";
  }

  // Check for extra spaces
  if (/^\s|\s{2,}|\s$/.test(newResponsibility)) {
      return "Please check for extra spaces.";
  }

  // Check for duplicate responsibility
  if (
      newResponsibility.trim() &&
      responsibilities.some((r:any) => r.text.toLowerCase() === newResponsibility.trim().toLowerCase())
  ) {
      return "Responsibility already exists.";
  }

  // No validation errors
  return "";
}

export const invalidInput = {
  "+": true, "-": true, "e": true
} as const;

export const minMaxFields = [
  "workminexp",
  "workmaxexp",
  "minsalary",
  "maxsalary"
]


export function validateStageName(name: string): string | null {
  // Check for minimum and maximum length
  if (name.length < 3 || name.length > 30) {
    return "Stage name must be between 3 and 30 characters long.";
  }

  // Check for valid characters (alphabets, numbers, space, and hyphen)
  if (!/^[a-zA-Z0-9\s-]+$/.test(name)) {
    return "No special characters are allowed except for Hyphen.";
  }

  // Check for invalid start/end characters and consecutive spaces/hyphens
  if (/^[\s-]|[\s-]$|[\s-]{2,}/.test(name)) {
    return "Please enter a valid name.";
  }

  // Check for valid format (only alphabets, numbers, spaces, and hyphens)
  if (!/^[a-zA-Z0-9]+(?:[-\s][a-zA-Z0-9]+)*$/.test(name)) {
    return "Stage names can only contain alphabets, numbers, spaces, and hyphens. Spaces and hyphens cannot be at the start or end, or appear consecutively.";
  }

  return null; // No validation errors
}

export function titleFormat(jobType: string | undefined) {
  return jobType
    ?.toLowerCase() // Ensure the text is in lowercase first
    .replace(/_/g, ' ') // Replace underscores with spaces
    .replace(/\b\w/g, (char) => char.toUpperCase()); // Capitalize the first letter of each word
}

