"use client";
import { useState, useEffect, useCallback } from "react";
import industryTypes from "./industry-type.json";
import { getCurrentUserEmail } from "../components/AuthProvider";
import { apiService } from "@/app/api/service";
import {
  validateFullName,
  validateWhatsAppNumber,
  validateDesignation,
  validateLinkedIn,
  validateCompanyName,
  validateWebsite,
  validateEmployees,
  validateIndustry,
  validateCompanyLinkedIn,
  validateCompanyType,
} from "../utils/validations";
import { useRouter } from "next/navigation";
import { CompanyDetails } from "../types/model";
import { RecruiterDetails } from "../types/model";
import { Check } from "lucide-react";
import { CustomSelect } from "@/components/filters/custom-select";
import { set } from "lodash";
import { EMPLOYEES_RANGE,COMPANY_TYPES } from "../utils/constants";

export default function MultiStepForm() {
  const [step, setStep] = useState(1);
  const [recruiterDetails, setRecruiterDetails] = useState<RecruiterDetails>({
    fullName: "",
    whatsappNumber: "",
    designation: "",
    linkedIn: "",
    email: "",
  });
  const router = useRouter();

  const [companyDetails, setCompanyDetails] = useState<CompanyDetails>({
    companyName: "",
    website: "",
    employees: "",
    industry: "",
    companyLinkedIn: "",
    companyType: "",
  });

  const [isNextDisabled, setIsNextDisabled] = useState(true);
  const [isSubmitDisabled, setIsSubmitDisabled] = useState(true);

  const [searchQuery, setSearchQuery] = useState("");
  const [filteredIndustries, setFilteredIndustries] = useState<string[]>([]);
  const [showDropdown, setShowDropdown] = useState(false);
  const [showSearchList, setShowSearchList] = useState(true);
  const [errorMessage, setErrorMessage] = useState("");

  const [touched, setTouched] = useState({
    fullName: false,
    whatsappNumber: false,
    designation: false,
    linkedIn: false,
    companyName: false,
    website: false,
    employees: false,
    industry: false,
    companyLinkedIn: false,
    email: false,
    companyType: false,
  });

  const [errors, setErrors] = useState({
    fullName: "",
    whatsappNumber: "",
    designation: "",
    linkedIn: "",
    companyName: "",
    website: "",
    employees: "",
    industry: "",
    companyLinkedIn: "",
    email: "",
    companyType: "",
  });

  const nextStep = () => setStep(step + 1);
  const prevStep = () => setStep(step - 1);

  const validateRecruiterDetails = useCallback(() => {
    const { fullName, whatsappNumber, designation, linkedIn } =
      recruiterDetails;
    const newErrors = {
      fullName: validateFullName(fullName),
      whatsappNumber: validateWhatsAppNumber(whatsappNumber),
      designation: validateDesignation(designation),
      linkedIn: validateLinkedIn(linkedIn),
    };

    setErrors((prevErrors) => ({ ...prevErrors, ...newErrors }));
    const allValid = Object.values(newErrors).every((error) => !error);
    setIsNextDisabled(!allValid);
  }, [recruiterDetails]);

  const validateCompanyDetails = useCallback(() => {
    const {
      companyName,
      website,
      employees,
      industry,
      companyLinkedIn,
      companyType,
    } = companyDetails;
    const newErrors = {
      companyName: validateCompanyName(companyName),
      website: validateWebsite(website),
      employees: validateEmployees(employees),
      industry: validateIndustry(industry, filteredIndustries),
      companyLinkedIn: validateCompanyLinkedIn(companyLinkedIn),
      companyType: validateCompanyType(companyType),
    };

   setErrors((prevErrors) => ({ ...prevErrors, ...newErrors }));
   const allValid = !Object.values(newErrors).some((error) => error);
   setIsSubmitDisabled(!allValid);
  }, [companyDetails, filteredIndustries]);

  useEffect(() => {
    validateRecruiterDetails();
  }, [recruiterDetails, validateRecruiterDetails]);

  useEffect(() => {
    validateCompanyDetails();
  }, [companyDetails, validateCompanyDetails]);

  const fetchCompanyDetails = useCallback(async () => {
    const userEmail = (await getCurrentUserEmail()) as string;
    const domain = userEmail.split("@")[1];
    try {
      const response = await apiService(
        `/company?domain=${domain}`,
        "GET",
        null
      );
      if (!response) {
        throw new Error("Failed to fetch company details");
      }
      const data = response;
      if (data) {
        setCompanyDetails({
          companyName: data.name || "",
          website: data.website || "",
          companyLinkedIn: data.linkedin || "",
          companyType: data.type || "",
          employees: data.number_of_employees || "",
          industry: data.industry_type || "",
        });
        setSearchQuery(data.industry_type || "");
      }
    } catch (error) {
      console.error("Error fetching company details:", error);
    }
  }, []);

  useEffect(() => {
    fetchCompanyDetails();
  }, [fetchCompanyDetails]);

  useEffect(() => {
    if (searchQuery) {
      const lowerSearchQuery = Object.values(industryTypes).flat();
      const filtered = industryTypes.filter((industry: string) =>
        industry.toLowerCase().startsWith( searchQuery.toLowerCase())
      );
      setFilteredIndustries(filtered);
       setShowSearchList(!industryTypes.includes(searchQuery));
      setShowDropdown(searchQuery !== "");
    } else {
      setFilteredIndustries([]);
      setShowDropdown(false);
    }

   
  }, [searchQuery, industryTypes]);
 
  const handleSelectIndustry = (industry: string) => {
    setCompanyDetails({ ...companyDetails, industry });
    setSearchQuery(industry);
    setFilteredIndustries([]);
    setShowDropdown(false);
  };

  const handleBlur = (field: string) => {
    setTouched((prevTouched) => ({ ...prevTouched, [field]: true }));
  
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const userEmail = (await getCurrentUserEmail()) as string;
    const payload = {
      full_name: recruiterDetails.fullName,
      whatsapp_number: recruiterDetails.whatsappNumber,
      designation: recruiterDetails.designation,
      linkedin_url: recruiterDetails.linkedIn,
      email_id: userEmail,
      company: {
        name: companyDetails.companyName,
        website: companyDetails.website,
        number_of_employees: companyDetails.employees,
        industry_type: companyDetails.industry,
        linkedin: companyDetails.companyLinkedIn,
        type: companyDetails.companyType,
      },
    };

    try {
      const result = await apiService(`/recruiter`, "POST", payload);
      setErrorMessage("");
      router.push("/dashboard");
    } catch (error: any) {
      const errorObj = await error;
      console.error("Error creating recruiter:", errorObj, errorObj.detail);
      const errMsg = errorObj?.detail
        ? errorObj.detail
        : "An error occurred. Please try again.";
      setErrorMessage(errMsg);
      setTimeout(() => {
        setErrorMessage("");
      }, 3000);
    }
  };

  return (
    <div className="flex justify-center items-center min-h-screen bg-white" onClick={()=>setShowDropdown(false)}>
      <div className="w-full lg:max-w-3xl md:max-w-2xl  bg-white border border-color[#E2E8F0] rounded-lg p-8 pb-1">
        {errorMessage && (
          <div className="fixed inset-0 flex items-center justify-center z-50">
            <div className="bg-white p-6 rounded-lg shadow-xl">
              <p className="text-red-500">{errorMessage}</p>
            </div>
          </div>
        )}
        <h2 className="text-2xl font-bold mb-3 text-[#050505]">
          Let&apos;s get Started
        </h2>
        <p className="text-gray-600 mb-6">
          Please provide the below details to begin
        </p>

        <div className="flex items-center justify-center mb-6">
          <div className="flex items-center justify-center">
            <div className="text-center">
              <span
                className={`block w-[26px] h-[26px] mx-auto  ${step === 1
                    ? "bg-[#0F8FC9] text-white"
                    : "bg-green-600 text-white"
                  } rounded-full flex items-center justify-center relative z-10 `}
              >
                {step > 1 ? <Check size={16} /> : "1"}
              </span>
            </div>

            <div className="w-40 h-[1px] bg-slate-300 top-[-14px]"></div>

            <div className="text-center">
              <span
                className={`block w-[26px] h-[26px] mx-auto  ${step === 2
                    ? "bg-[#0F8FC9] text-white"
                    : "bg-gray-200 text-black"
                  } rounded-full flex items-center justify-center relative z-10`}
              >
                2
              </span>
            </div>
          </div>
        </div>
        <div className="flex items-center justify-center mb-8 mt-[-15px]">
          <div className="flex items-center justify-center space-x-16">
            <div className="text-center">
              <span className="text-[#000000] text-sm font-medium">
                Recruiter Details
              </span>
            </div>

            <div className="text-center">
              <span className="text-[#000000] text-sm font-medium">
                Company Details
              </span>
            </div>
          </div>
        </div>
        {step === 1 && (
          <div >
            <form className="grid grid-cols-1 md:grid-cols-2 gap-6 ">
              <div>
                <label className="block text-sm font-semibold text-[#0F172A]">
                  Full name
                </label>
                <input
                  type="text"
                  placeholder="Enter your name"
                  value={recruiterDetails.fullName}
                  onBlur={() =>{ handleBlur("fullName")}}
                  onChange={(e) =>
                    setRecruiterDetails({
                      ...recruiterDetails,
                      fullName: e.target.value,
                    })
                  }
                  className="mt-1 block w-full px-3 py-2 border rounded-md  focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                />
                {touched.fullName && errors.fullName && (
                  <p className="text-red-500 text-xs mt-1">{errors.fullName}</p>
                )}
              </div>

              <div>
                <label className="block text-sm font-semibold text-[#0F172A]">
                  Whatsapp number
                </label>
                <input
                  type="text"
                  placeholder="Enter mobile number"
                  value={recruiterDetails.whatsappNumber}
                  onBlur={() => handleBlur("whatsappNumber")}
                  onChange={(e) =>
                    setRecruiterDetails({
                      ...recruiterDetails,
                      whatsappNumber: e.target.value,
                    })
                  }
                  className="mt-1 block w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                />
                {touched.whatsappNumber && errors.whatsappNumber && (
                  <p className="text-red-500 text-xs mt-1">
                    {errors.whatsappNumber}
                  </p>
                )}
              </div>

              <div>
                <label className="block text-sm font-semibold text-[#0F172A]">
                  Designation
                </label>
                <input
                  type="text"
                  placeholder="Enter your role"
                  value={recruiterDetails.designation}
                  onBlur={() => handleBlur("designation")}
                  onChange={(e) =>
                    setRecruiterDetails({
                      ...recruiterDetails,
                      designation: e.target.value,
                    })
                  }
                  className="mt-1 block w-full px-3 py-2 border rounded-md  focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                />
                {touched.designation && errors.designation && (
                  <p className="text-red-500 text-xs mt-1">
                    {errors.designation}
                  </p>
                )}
              </div>

              <div>
                <label className="block text-sm font-semibold text-[#0F172A]">
                  LinkedIn URL
                </label>
                <input
                  type="text"
                  placeholder="Enter your LinkedIn URL"
                  value={recruiterDetails.linkedIn}
                  onBlur={() => handleBlur("linkedIn")}
                  onChange={(e) =>
                    setRecruiterDetails({
                      ...recruiterDetails,
                      linkedIn: e.target.value,
                    })
                  }
                  className="mt-1 block w-full px-3 py-2 border rounded-md  focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                />
                {touched.linkedIn && errors.linkedIn && (
                  <p className="text-red-500 text-xs mt-1">{errors.linkedIn}</p>
                )}
              </div>
            </form>
            <div className="flex justify-end pt-32">
              <button
                onClick={nextStep}
                disabled={isNextDisabled}
                className={`mt-6 mb-6 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition duration-300 ${isNextDisabled ? "opacity-50 cursor-not-allowed" : ""
                  }`}
              >
                Continue
              </button>
            </div>
          </div>
        )}

        {step === 2 && (
          <div onClick={()=>setShowDropdown(false)}>
            <form className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-semibold text-[#0F172A]">
                  Company Name
                </label>
                <input
                  type="text"
                  placeholder="Enter your Company name"
                  value={companyDetails.companyName}
                  onFocus={()=>setShowDropdown(false)}
                  onBlur={() => handleBlur("companyName")}
                  onChange={(e) =>
                    setCompanyDetails({
                      ...companyDetails,
                      companyName: e.target.value,
                    })
                  }
                  className="mt-1 block w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                />
                {touched.companyName && errors.companyName && (
                  <p className="text-red-500 text-xs mt-1">
                    {errors.companyName}
                  </p>
                )}
              </div>

              <div>
                <label className="block text-sm font-semibold text-[#0F172A]">
                  Website
                </label>
                <input
                  type="url"
                  placeholder="Enter company URL"
                  value={companyDetails.website}
                  onFocus={()=>setShowDropdown(false)}
                  onBlur={() => handleBlur("website")}
                  onChange={(e) =>
                    setCompanyDetails({
                      ...companyDetails,
                      website: e.target.value,
                    })
                  }
                  className="mt-1 block w-full px-3 py-2 border rounded-md  focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                />
                {touched.website && errors.website && (
                  <p className="text-red-500 text-xs mt-1">{errors.website}</p>
                )}
              </div>

              <div onClick={() => { setShowDropdown(false)
   }
    }>
                <label className="block text-sm font-semibold text-[#0F172A] mb-1">
                  Company Size
                </label>
                <CustomSelect
                  options={EMPLOYEES_RANGE}
                  placeholder="No of Employees"
                  contentClassName="max-h-[200px]"
                  value={companyDetails.employees}
                  onFocus={()=>setShowDropdown(false)}
                  
                  onValueChange={(value) =>{
                  setShowDropdown(false)  

                    setCompanyDetails({
                      ...companyDetails,
                      employees: value,
                    })
                  }}
                  triggerClassName={ `h-9.5
                    ${!companyDetails.employees ? "text-gray-400" : "text-black"
                  }`}
                  
                />
                {touched.employees && errors.employees && (
                  <p className="text-red-500 text-xs mt-1">
                    {errors.employees}
                  </p>
                )}
              </div>

              <div className="relative">
                <label className="block text-sm font-semibold text-[#0F172A]">
                  Industry Type
                </label>
                <input
                  type="text"
                  name="industry"
                  placeholder="IT & Software"
                  value={searchQuery}

                  onBlur={() => {
                    handleBlur("industry");
                    if (!searchQuery) {
                      setCompanyDetails({ ...companyDetails, industry: "" });

                    }

                  }}
                  onChange={(e) => {
                    setSearchQuery(e.target.value);
                    setCompanyDetails({
                      ...companyDetails,
                      industry: e.target.value,
                    });
                  }}
                  onFocus={() => {
                    setShowDropdown(true);
                  }}
                  className="mt-1 block w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                />
                {showSearchList &&
                  showDropdown &&
                  filteredIndustries.length > 0 && (
                    <ul className="absolute bg-white border rounded-md mt-1 w-full max-h-52 overflow-auto z-10 ">
                      {filteredIndustries.map((industry) => (
                        <li
                          key={industry}
                          onClick={() => handleSelectIndustry(industry)}
                          className={`px-4 py-2 cursor-pointer hover:bg-gray-200`}
                        >
                          {industry}
                        </li>
                      ))}
                    </ul>
                  )}

                
                {touched.industry && errors.industry && (
                  <p className="text-red-500 text-xs mt-1">{errors.industry}</p>
                )}
              </div>

              <div>
                <label className="block text-sm font-semibold text-[#0F172A]">
                  Company LinkedIn
                </label>
                <input
                  type="text"
                  placeholder="https://www.linkedin.com/company/companyname/"
                  value={companyDetails.companyLinkedIn}
                  onBlur={() => handleBlur("companyLinkedIn")}
                  onFocus={()=>setShowDropdown(false)}
                  onChange={(e) =>
                    setCompanyDetails({
                      ...companyDetails,
                      companyLinkedIn: e.target.value,
                    })
                  }
                  className="mt-1 block w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                />
                {touched.companyLinkedIn && errors.companyLinkedIn && (
                  <p className="text-red-500 text-xs mt-1">
                    {errors.companyLinkedIn}
                  </p>
                )}
              </div>

              <div>
                <label className="block text-sm font-semibold text-[#0F172A] mb-1">
                  Company Type
                </label>
                <CustomSelect
                  options={COMPANY_TYPES}
                  placeholder="Select Company Type"
                  value={companyDetails.companyType}
                  onFocus={()=>setShowDropdown(false)}
                  onValueChange={(value) =>
                    setCompanyDetails({
                      ...companyDetails,
                      companyType: value,
                    })
                  }
                  triggerClassName={ `h-9.5
                    ${!companyDetails.employees ? "text-gray-400" : "text-black"
                  }`}
                />
                {touched.companyType && errors.companyType && (
                  <p className="text-red-500 text-xs mt-1">
                    {errors.companyType}
                  </p>
                )}
              </div>
            </form>

            <div className="flex mt-16 mb-5 justify-end space-x-2">
              <button
                onClick={prevStep}
                className="px-4 py-2 bg-white rounded-md border-2 transition duration-300"
              >
                Back
              </button>
              <button
                onClick={handleSubmit}
                disabled={isSubmitDisabled}
                className={`px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition duration-300 ${isSubmitDisabled ? "opacity-50 cursor-not-allowed" : ""
                  }`}
              >
                Submit
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
