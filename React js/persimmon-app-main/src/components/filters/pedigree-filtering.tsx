import { applicantsPreferedData, companies, filtertype, industries, qualifications } from "@/app/types/model";
import { useEffect } from "react";
import { IPedigreeFC } from "@/components/filters/models";
import { Checkbox } from "../ui/checkbox";
import SelectPedigreeFilters from "./pedigree-items";
import institutions from "@/app/(secure)/dashboard/view-job-page/all-applicants/filtering/colleges.json"
import { useHandleEntriesChange } from "./pedigree-changes";

export const FilterByPedigree: React.FC<IPedigreeFC> = ({ educationEntries, setEducationEntries, setCompanyEntries, companyEntries, isEducationChecked, setIsEducationChecked, isCompanyChecked, setIsCompanyChecked, setErrorMessage }) => {
    const { handleEntriesChange } = useHandleEntriesChange(setErrorMessage);

    const handleEducationChange = (index: number, field: string, value: string) => {
        handleEntriesChange(index, field, value, educationEntries, setEducationEntries, "education");
    };
    const handleCompanyChange = (index: number, field: string, value: string) => {
        handleEntriesChange(index, field, value, companyEntries, setCompanyEntries, "company");
    };
    const addEducation = () => {
        if (educationEntries.length >= 5) return;
        setEducationEntries([
            ...educationEntries,
            {
                filterType: "",
                qualification: "",
                institution: "",
                errorMessage: "",
            },
        ]);
    };

    const addCompany = () => {
        if (companyEntries.length >= 5) return;
        setCompanyEntries([
            ...companyEntries,
            {
                filterType: "",
                industry: "",
                company: "",
                errorMessage: "",
            },
        ]);
    };
    useEffect(() => {
        // Handle education entries
        if (isEducationChecked) {
            const educationData = educationEntries
                .filter((entry) => entry.qualification && entry.institution)
                .map((entry) => ({
                    name: "education",
                    specifications: [
                        {
                            spec: entry.filterType,
                            qualification: entry.qualification,
                            institution_name: entry.institution,
                        },
                    ],
                }));

            // Add or merge `education` data into `pedigree`
            applicantsPreferedData.filters.pedigree = [
                ...applicantsPreferedData.filters.pedigree.filter((entry: any) => entry.name !== "education"),
                ...educationData,
            ];
        } else {
            // Remove `education` objects if unchecked
            applicantsPreferedData.filters.pedigree = applicantsPreferedData.filters.pedigree.filter(
                (entry: any) => entry.name !== "education"
            );
        }

        // Handle company entries
        if (isCompanyChecked) {
            const companyData = companyEntries
                .filter((entry) => entry.company && entry.industry)
                .map((entry) => ({
                    name: "company",
                    specifications: [
                        {
                            spec: entry.filterType,
                            qualification: entry.company,
                            institution_name: entry.industry,
                        },
                    ],
                }));

            // Add or merge `company` data into `pedigree`
            applicantsPreferedData.filters.pedigree = [
                ...applicantsPreferedData.filters.pedigree.filter((entry: any) => entry.name !== "company"),
                ...companyData,
            ];
        } else {
            // Remove `company` objects if unchecked
            applicantsPreferedData.filters.pedigree = applicantsPreferedData.filters.pedigree.filter(
                (entry: any) => entry.name !== "company"
            );
        }
    }, [isEducationChecked, isCompanyChecked, educationEntries, companyEntries]);


    return (
        <div className="py-11 px-6">
            <div className="space-y-4">
                <h2 className="text-lg font-semibold">Pedigree</h2>

                {/* Education Section */}
                <div className="space-y-4">
                    <div className="flex items-center space-x-2">
                        <Checkbox
                            checked={isEducationChecked}
                            onCheckedChange={(e) => setIsEducationChecked(e === true)}
                        />
                        <h3 className="text-base font-medium">Education</h3>
                    </div>

                    {educationEntries.map((entry, index) => (
                        <div key={index} className="space-y-2 px-6">
                            <SelectPedigreeFilters
                                key={index}
                                entry={entry}
                                index={index}
                                handleChange={handleEducationChange}
                                filterTypeOptions={filtertype}
                                qualificationOptions={qualifications}
                                institutionOptions={institutions}
                                industryOptions={[]}
                                companyOptions={[]}
                                isCompanyForm={false} // Education form
                            />

                            {entry.errorMessage && (
                                <p className="text-sm text-red-500">{entry.errorMessage}</p>
                            )}
                        </div>
                    ))}

                    <button
                        className="text-base font-normal text-primary hover:font-semibold "
                        onClick={addEducation}
                        disabled={educationEntries.length >= 5}
                        type="button"
                    >
                        + Add Education
                    </button>
                </div>

                {/* Company Section */}
                <div className="space-y-4">
                    <div className="flex items-center space-x-2">
                        <Checkbox
                            checked={isCompanyChecked}
                            onCheckedChange={(e) => setIsCompanyChecked(e === true)}
                        />
                        <h3 className="text-base font-medium">Company</h3>
                    </div>

                    {companyEntries.map((entry, index) => (
                        <div key={index} className="space-y-2 px-6">
                            <SelectPedigreeFilters
                                key={index}
                                entry={entry}
                                index={index}
                                handleChange={handleCompanyChange}
                                filterTypeOptions={filtertype}
                                qualificationOptions={[]}
                                institutionOptions={[]}
                                industryOptions={industries}
                                companyOptions={companies}
                                isCompanyForm={true} // Company form
                            />

                            {entry.errorMessage && (
                                <p className="text-sm text-red-500">{entry.errorMessage}</p>
                            )}
                        </div>
                    ))}

                    <button
                        className="text-base font-normal text-primary hover:font-semibold "
                        onClick={addCompany}
                        disabled={companyEntries.length >= 5}
                    >
                        + Add Company
                    </button>
                </div>
            </div>
        </div>
    );
};