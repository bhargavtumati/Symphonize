import type React from "react"
import { Card } from "@/components/ui/card" // Adjust this import based on your file structure
import type { JobKeyDetails } from "../../../../types/model"
import { IndianRupee, Briefcase, MapPin } from "lucide-react"
interface JobDescription {
  description: string
}

interface CompanyDetails {
  companyName: string
  website: string
  employees: string
  industry: string
  companytype: string
  companylinkedIn: string
}

interface AIDetails {
  aiInput: { [key: string]: string }
}

interface PreviewProps {
  jobKeyDetails: JobKeyDetails
  jobDescription: JobDescription
  companyDetails: CompanyDetails
  aiDetails: AIDetails
  questions: string[]
  onBack: () => void
  onNext: () => void
}

const Preview: React.FC<PreviewProps> = ({
  jobKeyDetails,
  jobDescription,
  companyDetails,
  aiDetails,
  questions,
  onBack,
  onNext,
}) => {
  console.log(aiDetails, questions)
  console.log('questions',questions)
  console.log('jobDescription',jobDescription)
  const formatString = (str: string) => {
    return str
      .toLowerCase()
      .replace(/_/g, " ")
      .replace(/\b\w/g, (char) => char.toUpperCase())
  }

  return (
    <div className="p-6 space-y-6">
      {/* Job Key Details Section */}
      <h2 className="text-2xl font-bold mb-4">Preview</h2>
      <div className="flex flex-row gap-4">
        <div className="flex flex-col  gap-4 md:w-[70%] border-none">
          <Card className="bg-white p-8 rounded-lg ">
            <div>
              <p className="text-xl font-bold mb-4 text-[#1E293B]">{jobKeyDetails.jobTitle}</p>
            </div>
            <div className="grid grid-cols-4 gap-8 ">
              <div >
                <p className="text-[#64748B] text-sm">Salary:</p>
                <div className="flex font-medium text-base leading-6 gap-[4px] ">
                  <IndianRupee className="w-5 h-5 text-slate-700 font-thin" />
                  <p className="text=[#334155] text-base">
                    {jobKeyDetails.minsalary} LPA - {jobKeyDetails.maxsalary} LPA
                  </p>
                </div>
              </div>
              <div>
                <p className="text-[#64748B] text-sm">Experience:</p>
                <div className="flex font-medium text-base leading-6  gap-[4px]">
                  <Briefcase className="w-5 h-5 text-slate-700" />
                  <p className="text-[#334155] text-base">
                    {jobKeyDetails.workminexp} - {jobKeyDetails.workmaxexp} Years
                  </p>
                </div>
              </div>
              <div>
                <p className="text-[#64748B] text-sm">Location:</p>
                <div className="flex font-medium text-base leading-6  gap-[4px]">
                  <MapPin className="w-5 h-5 text-slate-700" />
                  <p className="text-[#334155] text-base">{jobKeyDetails.jobLocation}</p>
                </div>
              </div>
              <div></div>
              <div>
                <p className="text-[#64748B] text-sm">Job Type:</p>
                <p className="font-medium text-base leading-6 text=[#334155]" >
                  {formatString(jobKeyDetails.jobType)}
                </p>
              </div>
              <div>
                <p className="text-[#64748B] text-sm">Work Place Type:</p>
                <p className="font-medium text-base leading-6  text=[#334155]">
                  {formatString(jobKeyDetails.workplacetype)}
                </p>
              </div>
              <div>
                <p className="text-[#64748B] text-sm">Project Team Size:</p>
                <p className="font-medium text-base leading-6  text=[#334155]">
                  {jobKeyDetails.teamsize}
                </p>
              </div>
              <div>
                <p className="text-[#64748B] text-sm">Target Date :</p>
                <p className="font-medium text-base leading-6  text-[#334155]">
                  {jobKeyDetails.target_date
                    ? new Date(jobKeyDetails.target_date)
                        .toLocaleDateString("en-GB", {
                          day: "2-digit",
                          month: "short",
                          year: "numeric",
                        })
                        .replace(/(\w{3})(?=\s)/, "$1,")
                    : ""}
                </p>
              </div>
            </div>
          </Card>

          {/* Job Description Section */}
          <Card className="bg-white p-8">
            <h2 className="text-lg text-slate-800 font-semibold mb-4">Job Description</h2>
            <div className="prose max-w-none" dangerouslySetInnerHTML={{ __html: jobDescription.description }} />
          </Card>

          {/* AI Input Section */}
          <Card className="bg-white p-8">
            <h2 className="text-lg text-slate-800 font-semibold mb-4">AI Clarification Questions</h2>
            {Object.keys(aiDetails.aiInput).length > 0 ? (
              Object.entries(aiDetails.aiInput).map(([question, answer], index) => (
                <div key={index} className="mb-4">
                  <p className="text-base leading-6 text-slate-600">
                    {index + 1}. {question}
                  </p>
                  <p className="font-medium text-base text-slate-600 leading-6 ml-4 pt-2">{answer || "No answer provided"}</p>
                </div>
              ))
            ) :
              (<p className="text-base text-slate-600 leading-6 font-medium">No questions available</p>)}

          </Card>

          {/* Company Details Section */}
          <Card className="bg-white p-8">
            <h2 className="text-lg text-slate-800 font-semibold mb-2">Company Details</h2>
            <div>
              <p className="text-slate-600 font-bold text-xl mb-1">{companyDetails.companyName}</p>
              <p className="mb-1">Industry: {companyDetails.industry}</p>
              <p className="mb-1">Company Type: {formatString(companyDetails.companytype)}</p>
              <p className="mb-1">Company Size: {companyDetails.employees}</p>
            </div>
          </Card>
        </div>

        {/* <AILearnings /> */}
      </div>

      <div className="flex justify-end space-x-4 mt-4 mx-8 pr-8">
        <button
          type="button"
          onClick={onBack}
          className="bg-white border border-[1px] border-gray-300 py-2 rounded-md w-[105px] h-[40px]"
        >
          Back
        </button>
        <button
          type="button"
          onClick={onNext} // Validate before proceeding
          className="bg-blue-600 text-white py-2 rounded-md  w-[105px] h-[40px]"
        >
          Next
        </button>
      </div>
    </div>
  )
}

export default Preview

