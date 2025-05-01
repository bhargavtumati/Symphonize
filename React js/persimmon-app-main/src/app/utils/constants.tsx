export const SESSION_STORAGE = {
  userName: "userEmail",
};

export const SORTING_COLUMN_NAMES = {
  jobId: "code",
  jobTitle: "title",
  client: "client_name",
  location: "location",
  applicants: "applicant_count",
  postedOn: "posted_on",
  targetDate: "target_date",
  status: "status",
};

export const DEFAULT_SORTING_ORDER = {
  jobId: 0,
  jobTitle: 0,
  client: 0,
  location: 0,
  applicants: 0,
  postedOn: 0,
  targetDate: 0,
  status: 0,
};

export const SORTING_STEPS = 3;

export const JOB_COLUMNS = [
  { label: "Job ID", sortKey: "jobId" },
  { label: "Job Title", sortKey: "jobTitle" },
  { label: "Client", sortKey: "client" },
  { label: "Location", sortKey: "location" },
  { label: "Applicants", sortKey: "applicants" },
  { label: "Posted on", sortKey: "postedOn" },
  { label: "Target Date", sortKey: "targetDate" },
  { label: "Status", sortKey: "status" },
];

export const FILTER_OPTIONS = [
  { label: "Job ID", value: "code" },
  { label: "Job Title", value: "title" },
  { label: "Client", value: "client_name" },
  { label: "Location", value: "location" },
  { label: "Posted on", value: "posted_on" },
  { label: "Target Date", value: "target_date" },
];

export const COMPANY_TYPES = [
  { value: "SERVICE_BASED", label: "Service Based" },
  { value: "PRODUCT_BASED", label: "Product Based" },
];
export const EMPLOYEES_RANGE = [
  { value: "1-10", label: "1-10" },
  { value: "11-50", label: "11-50" },
  { value: "51-200", label: "51-200" },
  { value: "201-500", label: "201-500" },
  { value: "501-1000", label: "501-1000" },
  { value: "1001-5000", label: "1001-5000" },
  { value: "5001-10000", label: "5001-10000" },
  { value: "10001+", label: "10001+" },
];
export const JOB_TYPE = [
  { value: "FULL_TIME", label: "Full-time" },
  { value: "PART_TIME", label: "Part-time" },
  { value: "FREELANCE", label: "Freelance" },
  { value: "CONTRACT", label: "Contract" },
  { value: "INTERNSHIP", label: "Internship" },
];
export const WORK_TYPE = [
  { value: "ON_SITE", label: "On-site" },
  { value: "HYBRID", label: "Hybrid" },
  { value: "REMOTE", label: "Remote" },
];
export const TEAM_SIZE = [
  { value: "1-5", label: "1-5" },
  { value: "6-10", label: "6-10" },
  { value: "11-20", label: "11-20" },
  { value: "21-50", label: "21-50" },
  { value: "51-100", label: "51-100" },
  { value: "101-200", label: "101-200" },
  { value: "201+", label: "201+" },
];

export const INITIAL_COLORS = [
  "#F97316", // Orange
  "#0EA5E9", // Sky Blue
  "#22C55E", // Green
  "#EF4444", // Red
  "#A855F7", // Purple
];

export const INITIAL_FONTS = [
  "Roboto",
  "Open Sans",
  "Lato",
  "Montserrat",
  "Poppins",
  "Nunito",
  "Nunito Sans",
  "Inter",
  "Oswald",
  "Raleway",
  "Merriweather",
  "Playfair Display",
  "DM Sans",
  "Jost",
  "Karla",
  "Libre Franklin",
  "Crimson Pro",
  "Work Sans",
  "Heebo",
  "Source Sans Pro",
  "PT Sans",
  "PT Serif",
  "Manrope",
  "Archivo",
  "Spectral",
  "Fira Sans",
  "Bitter",
  "Zilla Slab",
  "Libre Baskerville",
  "Exo 2",
];


export const variables = [
  { id: "1", name: "CompanyName" },
  { id: "2", name: "JobTitle" },
  { id: "3", name: "JobType" },
  { id: "4", name: "WorkplaceType" },
  { id: "5", name: "JobLocation" },
  { id: "6", name: "MinExperience" },
  { id: "7", name: "MaxExperience" },
  { id: "8", name: "MinSalary" },
  { id: "9", name: "MaxSalary" },
  { id: "10", name: "Industry" },
  { id: "11", name: "CompanyType" },
  { id: "12", name: "CompanySize" },
  { id: "13", name: "RecruiterName" },
  { id: "14", name: "Designation" },
  { id: "15", name: "CompanyWebsite" },
  { id: "16", name: "RecruiterContactNumber" },
];

export enum SkeletonType {
  Flat = "flat",
  Circle = "circle",
  Card = "Card",
  Description = "Description",
  ShareJob = "sharejob",
  Publish = "publish",
  ApplicantCard = "applicantcard",
  Table = "table",
  Ribbon = "ribbon",
}
export const TIME_ZONES = [
  "Africa/Algiers",
  "Africa/Bangui",
  "Africa/Cairo",
  "Africa/Casablanca",
  "Africa/Djibouti",
  "Africa/Harare",
  "Africa/Johannesburg",
  "Africa/Khartoum",
  "Africa/Mogadishu",
  "Africa/Nairobi",
  "Africa/Nouakchott",
  "Africa/Tripoli",
  "Africa/Tunis",
  "America/Anchorage",
  "America/Araguaina",
  "America/Argentina/Buenos_Aires",
  "America/Bogota",
  "America/Caracas",
  "America/Chicago",
  "America/Costa_Rica",
  "America/Denver",
  "America/Edmonton",
  "America/El_Salvador",
  "America/Godthab",
  "America/Guatemala",
  "America/Halifax",
  "America/Indianapolis",
  "America/Lima",
  "America/Los_Angeles",
  "America/Managua",
  "America/Mazatlan",
  "America/Mexico_City",
  "America/Montevideo",
  "America/Montreal",
  "America/New_York",
  "America/Panama",
  "America/Phoenix",
  "America/Puerto_Rico",
  "America/Regina",
  "America/Santiago",
  "America/Sao_Paulo",
  "America/St_Johns",
  "America/Tegucigalpa",
  "America/Tijuana",
  "America/Vancouver",
  "America/Winnipeg",
  "Asia/Aden",
  "Asia/Almaty",
  "Asia/Amman",
  "Asia/Baghdad",
  "Asia/Bahrain",
  "Asia/Baku",
  "Asia/Bangkok",
  "Asia/Beirut",
  "Asia/Calcutta",
  "Asia/Dacca",
  "Asia/Damascus",
  "Asia/Dhaka",
  "Asia/Dubai",
  "Asia/Hong_Kong",
  "Asia/Tokyo",
  "Europe/London",
  "Europe/Berlin",
  "Europe/Paris",
  "Europe/Madrid",
  "Europe/Moscow",
  "UTC",
]