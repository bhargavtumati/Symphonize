export const normalizeString = (str: string) => {
  return str
    .replace(/<[^>]*>/g, "") // Remove all HTML tags
    .replace(/&nbsp;/g, "") // Remove non-breaking spaces
    .replace(/\s+/g, "") // Remove all spaces (including between words)
    .trim(); // Trim leading and trailing spaces
};


export const formatWorkplaceType = (type: String) => {
  return type
    .replace(/_/g, "-") // Replace underscores with hyphens
    .toLowerCase() // Convert the entire string to lowercase
    .split("-") // Split the string into an array by hyphen
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1)) // Capitalize each word
    .join("-"); // Join the array back into a string with hyphens
};

export const formatWebsite = (url: string): string => {
  return url
    .replace(/^https?:\/\/(www\.)?/, "") // Remove "http://", "https://", and "www."
    .replace(/\/$/, ""); // Remove trailing slash if any
};


export const formatText = (text: string) => {
  // Check if the string consists only of numbers
  if (/^\d+$/.test(text)) {
    return text; // Return numeric strings unchanged
  }

  if (text === text.toUpperCase() && text.includes('_')) {
    return text
      .replace(/_/g, ' ')
      .toLowerCase()
      .replace(/\b\w/g, (char) => char.toUpperCase()); 
  }

  return text;
};


