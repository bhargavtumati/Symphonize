import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import React, { useEffect, useState, useRef } from "react";
import industryTypes from "../../../../multi-form/industry-type.json";
import AILearnings from "../AILearnings";
import { Card } from "@/components/ui/card";
import { apiService } from '../../../../api/service';
import {
  validateCompanyName,
  validateWebsite,
  validateEmployees,
  validateIndustry,
  validateCompanyLinkedIn,
  validateCompanyType,
} from "../../../../utils/validations"; // Adjust the path based on your project structure
import { getCurrentUserEmail } from "../../../../components/AuthProvider";
import { Info } from 'lucide-react';
import TooltipComponent from "@/app/components/tooltip-component";
import { useSearchParams } from "next/navigation";
import { CustomSelect } from "@/components/filters/custom-select";
import { COMPANY_TYPES, EMPLOYEES_RANGE } from "@/app/utils/constants";

interface CompanyDetails {
  companyName: string;
  website: string;
  employees: string;
  industry: string;
  companytype: string;
  companylinkedIn: string;
  is_posting_client: boolean;
  isValidData: boolean
}
interface CompanyDetailsError {
  companyName: string;
  website: string;
  employees: string;
  industry: string;
  companyType: string;
  companylinkedIn: string;
}

interface StepProps {
  data: CompanyDetails;
  onChange: (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>
  ) => void;
  errors: Partial<CompanyDetails>;
  onIndustrySelect: (industry: string) => void;
  setErrors: React.Dispatch<React.SetStateAction<Partial<CompanyDetailsError>>>;
  onCompanyDetails: (updatedDetails: Partial<CompanyDetails>) => void;
  onBack: () => void;
  onNext: () => void;
}


const Step3CompanyDetails: React.FC<StepProps> = ({
  data,
  onChange,
  errors,
  onIndustrySelect,
  onCompanyDetails,
  setErrors,
  onBack,
  onNext,
}) => {
  //const immutableData = useRef(data);
  const [companyData, setCompanyData] = useState(data);
  const [searchQuery, setSearchQuery] = useState(data.industry);
  const [filteredIndustries, setFilteredIndustries] = useState<string[]>([]);
  const [showDropdown, setShowDropdown] = useState(false);
  const [isPostingClient, setIsPostingClient] = useState(data.is_posting_client);
  const [showSearchList, setShowSearchList] = useState(true)
  const [isSubmitted, setIsSubmitted] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);
  const searchParams = useSearchParams();
  const handleToggle = () => {
    setIsPostingClient((prevState) => !prevState);; // Toggle the value
  };
  const handleSelectChange = (field: keyof CompanyDetails) => (value: string) => {
    const syntheticEvent = {
      target: {
        name: field,
        value: value,
      },
    } as React.ChangeEvent<HTMLSelectElement>

    onChange(syntheticEvent)
  }
  const handleClickOutside = (e: any) => {
    // Close dropdown if clicking outside of it
    if (dropdownRef.current && !dropdownRef.current.contains(e.target)) {
      setShowSearchList(false);
      setShowDropdown(false);
    }
  };

  useEffect(() => {
    const newErrors: Partial<CompanyDetails> = {};
    newErrors.companyName = validateCompanyName(data.companyName);
    newErrors.website = validateWebsite(data.website);
    newErrors.employees = validateEmployees(data.employees);
    newErrors.industry = validateIndustry(data.industry);
    newErrors.industry = validateIndustry(searchQuery,filteredIndustries);
    newErrors.companylinkedIn = validateCompanyLinkedIn(data.companylinkedIn);
    newErrors.companytype = validateCompanyType(data.companytype);
    setErrors(newErrors);
  }, [data, setErrors, searchQuery,filteredIndustries]);

  useEffect(() => {
    if (searchQuery) {
      setFilteredIndustries(
        industryTypes.filter((industry: any) =>
          industry.toLowerCase().startsWith(searchQuery.toLowerCase())
        )
      );
      if (industryTypes.includes(searchQuery)) {
        setShowSearchList(false)
      }
      else {
        setShowSearchList(true)
      }
      setShowDropdown(true);
    } else {
      setFilteredIndustries([]);
      setShowDropdown(false);
    }
  }, [searchQuery]);

  const handleSelectIndustry = (industry: string) => {
    onIndustrySelect(industry);
    setSearchQuery(industry);
    setFilteredIndustries([]);
    setShowDropdown(false);
  };

  useEffect(() => {
    if (!isPostingClient) {
      // Fetch data when the toggle is off
      const fetchData = async () => {

        const userEmail = (await getCurrentUserEmail()) as string;
        const domain = userEmail.split("@")[1];

        const response = await apiService(`/company?domain=${domain}`, 'GET', null)
        if (!response) {
          throw new Error("Network response was not ok");
        }
        const responseData = response;
        const updatedData: Partial<CompanyDetails> = {
          companyName: responseData.name,
          website: responseData.website,
          industry: responseData.industry_type,
          companytype: responseData.type,
          employees: responseData.number_of_employees,
          companylinkedIn: responseData.linkedin,
          is_posting_client: false,
          isValidData: false,
        };
        onCompanyDetails(updatedData);
      };

      fetchData();
    } else {
      const actionType = searchParams.get("action");
      if (actionType !== "Edit") {
        if (!data.isValidData) {
          const updatedData: Partial<CompanyDetails> = {
            companyName: "",
            website: "",
            industry: "",
            companytype: "",
            employees: "",
            companylinkedIn: "",
            is_posting_client: true,
            isValidData: true,
          };
          onCompanyDetails(updatedData);
          setSearchQuery("")
        }
        else {
          const updatedData: Partial<CompanyDetails> = {
            companyName: data.companyName || "",
            website: data.website || "",
            industry: data.industry || "",
            companytype: data.companytype || "",
            employees: data.employees || "",
            companylinkedIn: data.companylinkedIn || "",
            is_posting_client: true,
          };
          onCompanyDetails(updatedData);
        }
      }
      else {
        if (isPostingClient) {
          const updatedData: Partial<CompanyDetails> = {
            companyName: companyData.companyName || "",
            website: companyData.website || "",
            industry: companyData.industry || "",
            companytype: companyData.companytype || "",
            employees: companyData.employees || "",
            companylinkedIn: companyData.companylinkedIn || "",
            is_posting_client: true,
          };
          onCompanyDetails(updatedData);
        }
      }
    }
  }, [isPostingClient]);

  useEffect(() => {
    // Add mousedown event listener to close the dropdown on any click
    if (showSearchList || showDropdown) {
      document.addEventListener('mousedown', handleClickOutside);
    } else {
      document.removeEventListener('mousedown', handleClickOutside);
    }
    // Cleanup the event listener on unmount or when dropdown is closed
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [showSearchList, showDropdown]);



  return (
    <div className="flex flex-col md:flex-row gap-4 mt-4">
      <Card className="w-full md:w-[70%] border-none p-4">
        <div className="p-5 ...">
          <div className="justify-between flex">
            <h3 className="text-xl font-semibold mb-4">Company Details</h3>
            <div className="flex items-center space-x-2">
              <Switch id="airplane-mode" checked={isPostingClient} onClick={handleToggle} />
              <Label htmlFor="airplane-mode">Posting for Client</Label>
              <TooltipComponent
                icon={<Info className="w-[18px] h-4 text-yellow-500" />}
                message="Client's information is used solely for matchmaking logic, not for posting"
                tag="p"
                className="w-[220px] absolute flex top-full text-gray-700 font-medium rounded-lg"
              />
            </div>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 flex-1">
            {/* Company Name */}
            <div>
              <label className="block text-sm font-medium text-gray-700">Company Name</label>
              <input
                type="text"
                name="companyName"
                placeholder="ABC Company"
                value={data.companyName}
                onChange={onChange}
                disabled={!isPostingClient}
                onFocus={() => setShowDropdown(false)}
                className={`mt-1 block w-full px-3 py-2 border rounded-md shadow-sm sm:text-sm ${!isPostingClient ? 'bg-gray-200 border-gray-300 cursor-not-allowed opacity-70' : 'border-gray-300 focus:outline-none focus:ring focus:ring-blue-500'}`}
              />
              {isSubmitted && errors.companyName && (
                <p className="text-red-500 text-xs mt-1">{errors.companyName}</p>
              )}
            </div>

            {/* Website */}
            <div>
              <label className="block text-sm font-medium text-gray-700">Website</label>
              <input
                type="text"
                name="website"
                placeholder="abccompany.com"
                value={data.website}
                onChange={onChange}
                disabled={!isPostingClient}
                onFocus={() => setShowDropdown(false)}
                className={`mt-1 block w-full px-3 py-2 border rounded-md shadow-sm sm:text-sm ${!isPostingClient ? 'bg-gray-200 border-gray-300 cursor-not-allowed opacity-70' : 'border-gray-300 focus:outline-none focus:ring focus:ring-blue-500'}`}
              />
              {isSubmitted && errors.website && (
                <p className="text-red-500 text-xs mt-1">{errors.website}</p>
              )}
            </div>

            {/* Industry */}
            <div className="relative" ref={dropdownRef}>
              <label className="block text-sm font-medium text-gray-700">Industry Type</label>
              <input
                type="text"
                name="industry"
                placeholder="IT & Software"
                autoComplete="off" 
                value={isPostingClient ? searchQuery : data.industry}
                onChange={(e) => setSearchQuery(e.target.value)}
                disabled={!isPostingClient}
                onFocus={() => {
                  if (searchQuery) setShowDropdown(true);
                }}
                className={`mt-1 block w-full px-3 py-2 border rounded-md shadow-sm sm:text-sm ${!isPostingClient ? 'bg-gray-200 border-gray-300 cursor-not-allowed opacity-70' : 'border-gray-300 focus:outline-none focus:ring focus:ring-blue-500'}`}
              />
              {showSearchList && showDropdown && filteredIndustries.length > 0 && (
                <ul className="absolute bg-white border rounded-md mt-1 w-full max-h-52 overflow-auto z-10">
                  {filteredIndustries.map((industry) => (
                    <li
                      key={industry}
                      onClick={() => handleSelectIndustry(industry)}
                      className={`px-4 py-2 cursor-pointer hover:bg-gray-200 ${data.industry === industry ? "bg-gray-100" : ""
                        }`}
                    >
                      {industry}
                    </li>
                  ))}
                </ul>
              )}
              {(((data.industry|| filteredIndustries.length === 0 || !searchQuery) && isPostingClient) && isSubmitted && errors.industry) && (
                <p className="text-red-500 text-xs mt-1">{errors.industry}</p>
              )}
            </div>

            {/* Company Type */}
            <div>
              <label className="block text-sm font-medium text-gray-700">Company Type</label>
              <CustomSelect
                options={COMPANY_TYPES}
                placeholder="Select"
                value={data.companytype}
                onValueChange={handleSelectChange("companytype")}
                disabled={!isPostingClient}
                onFocus={() => setShowDropdown(false)}
                contentClassName={`w-full`}
                triggerClassName={`h-9.5 mt-[3px]
                  ${!isPostingClient ? 'bg-gray-200 border-gray-300 opacity-50 cursor-not-allowed' : 'border-gray-300 focus:outline-none focus:ring focus:ring-blue-500'}
                  ${!data.companytype ? 'text-slate-400' : 'text-black'} `}
              />
              {isSubmitted && errors.companytype && (
                <p className="text-red-500 text-xs mt-1">{errors.companytype}</p>
              )}
            </div>

            {/* Number of Employees */}
            <div>
              <label className="block text-sm font-medium text-gray-700">Company Size</label>
              <CustomSelect
                options={EMPLOYEES_RANGE}
                placeholder="Select"
                value={data.employees}
                onValueChange={handleSelectChange("employees")}
                disabled={!isPostingClient}
                onFocus={() => setShowDropdown(false)}
                contentClassName={"max-h-[120px] w-full"}
                triggerClassName={`h-9.5 mt-[3px]
                  ${!isPostingClient ? 'bg-gray-200 border-gray-300 opacity-70  cursor-not-allowed' : 'border-gray-300 focus:outline-none focus:ring focus:ring-blue-500'} 
                  ${!data.employees ? 'text-slate-400' : 'text-black'} `}
              />
              {isSubmitted && errors.employees && (
                <p className="text-red-500 text-xs mt-1">{errors.employees}</p>
              )}
            </div>

            {/* LinkedIn */}
            <div>
              <label className="block text-sm font-medium text-gray-700">Company LinkedIn</label>
              <input
                type="text"
                name="companylinkedIn"
                placeholder="https://www.linkedin.com/company/companyname/"
                value={data.companylinkedIn}
                disabled={!isPostingClient}
                onFocus={() => setShowDropdown(false)}
                onChange={onChange}
                className={`mt-1 block w-full px-3 py-2 border rounded-md shadow-sm sm:text-sm ${!isPostingClient ? 'bg-gray-200 border-gray-300 cursor-not-allowed opacity-70' : 'border-gray-300 focus:outline-none focus:ring focus:ring-blue-500'}`}
              />
              {isSubmitted && errors.companylinkedIn && (
                <p className="text-red-500 text-xs mt-1">{errors.companylinkedIn}</p>
              )}
            </div>
          </div>
        </div>
        <div className="flex justify-end space-x-4 py-8 pr-8 ">
          <button
            type="button"
            onClick={onBack}
            className="bg-white border border-[1px] border-gray-300 px-4 py-2 rounded-md w-[105px] h-[40px]"
          >
            Back
          </button>
          <button
            type="button"
            onClick={() => {
              const hasError = Object.values(errors).some(
                (error) => error !== undefined && error !== ""
              );
              setIsSubmitted(true);

              if (!hasError || !isPostingClient) {
                onNext();
              }
            }}
            className="bg-blue-600 text-white px-4 py-2 rounded-md  w-[105px] h-[40px]"
          >
            Next
          </button>
        </div>
      </Card>
      {/* <AILearnings /> */}
    </div>
  );
};

export default Step3CompanyDetails;
