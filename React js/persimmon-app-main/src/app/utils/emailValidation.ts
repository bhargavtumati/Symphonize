import { z } from "zod";

// List of restricted domains
const restrictedDomains = [
  "gmail.com",
  "yahoo.com",
  "outlook.com",
  "aol.com",
  "mail.com",
  "icloud.com",
  "zoho.com",
  "yandex.com",
  "protonmail.com",
  "tutanota.com",
];

// Reusable email validation schema
export const emailSchema = z
  .string()
  .nonempty({ message: "Email is required." }) // Ensures email is not empty
  .email({ message: "Please enter a valid email address." }) // Validates email format
  .refine((email:any) => {
    const domain = email.split("@")[1];
    return !restrictedDomains.includes(domain);
  }, {
    message: "Please enter a valid professional email address.", // Shows message if email domain is restricted
  });

