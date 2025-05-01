"use client"
import type React from "react"
import { useState, useEffect } from "react"
import StepIndicator from "./StepIndicator"
import Step1JobKeyDetails from "./steps/JobKeyDetails"
import Step2JobDescription from "./steps/JobDescription"
import Step3CompanyDetails from "./steps/CompanyDetails"
import Step4AI from "./steps/AIIntegration"
import Step5Publish from "./steps/Publish"
import Preview from "./steps/preview"
import { apiService } from "../../../api/service"
import { useRouter } from "next/navigation"
import { minMaxFields } from "../../../utils/validations"

import {
  validateJobTitle,
  validateJobType,
  validateJobLocation,
  validateWorkplaceType,
  validateTeamSize,
  validateJobDescription,
  validateSalary,
  validateWorkExp,
  validateCompareSalaries,
  validateCompareWorkExp,
  validateTargetDate,
} from "../../../utils/validations"
import { dateWithoutTimeZone } from "@/lib/utils"
import { Loader2 } from "lucide-react"
import { useToast } from "../../../../components/hooks/use-toast"

const MultiStepForm: React.FC = () => {
  const router = useRouter()
  const { toast } = useToast()
  const [currentStep, setCurrentStep] = useState(1)
  const totalSteps = 6

  // Form States
  const [publishdetails, setPublishDetails] = useState({
    postingclient: true,
    PublishOnCareerPage: true,
    PublishOnOtherDomains: false,
    PublishedDomainNames: [] as string[],
  })

  const [jobKeyDetails, setJobKeyDetails] = useState({
    jobTitle: "",
    jobType: "",
    jobLocation: "",
    workplacetype: "",
    teamsize: "",
    maxsalary: "",
    minsalary: "",
    workmaxexp: "",
    workminexp: "",
    target_date: undefined,
  })

  const [jobDescription, setJobDescription] = useState({
    description: "",
  })
  const [originalJobDescription, setOriginalJobDescription] = useState({
    description: "",
  })

  const [companyDetails, setCompanyDetails] = useState({
    companyName: "",
    website: "",
    employees: "",
    industry: "",
    companytype: "",
    companylinkedIn: "",
    is_posting_client: false,
    isValidData: false,
  })

  const [aiDetails, setAIDetails] = useState<{
    aiInput: { [key: string]: string }
    enhanced_description: {}
  }>({
    aiInput: {},
    enhanced_description: {},
  })

  const [questions, setQuestions] = useState<string[]>([])

  // Error States
  const [errors, setErrors] = useState<{ [key: string]: string }>({})
  const [isNextDisabled, setIsNextDisabled] = useState(true)
  const [isSubmitDisabled, setIsSubmitDisabled] = useState(true)
  const [jobId, setJobId] = useState<string | null>("")
  const [actionType, setActionType] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  
  useEffect(() => {
    const fetchJobData = async () => {
      const searchParams = new URLSearchParams(window.location.search)
      const id = searchParams.get("jobId")
      const actionType = searchParams.get("action")
      setActionType(actionType)
      setJobId(id)
      if (!id) return // Exit if no job ID is found

      try {
        const jobData = await apiService(`/jobs/${id}`, "GET", null)
        if (jobData) {
          setJobKeyDetails({
            jobTitle: jobData.job.title,
            jobType: jobData.job.type,
            jobLocation: jobData.job.location,
            workplacetype: jobData.job.workplace_type,
            teamsize: jobData.job.team_size,
            minsalary: jobData.job.min_salary,
            maxsalary: jobData.job.max_salary,
            workminexp: jobData.job.min_experience,
            workmaxexp: jobData.job.max_experience,
            target_date: dateWithoutTimeZone(jobData.job.target_date),
          })

          setJobDescription({ description: jobData.job.description })
          setOriginalJobDescription({ description: jobData.job.description })

          setCompanyDetails({
            companyName: jobData.company.name,
            website: jobData.company.website,
            employees: jobData.company.number_of_employees,
            industry: jobData.company.industry_type,
            companytype: jobData.company.type,
            companylinkedIn: jobData.company.linkedin,
            is_posting_client: actionType === "Repost" ? false : jobData.job.is_posted_for_client,
            isValidData: false,
          })

          setQuestions(jobData.job.ai_clarifying_questions.map((q: any) => q.question))
          setAIDetails({
            aiInput: jobData.job.ai_clarifying_questions.reduce((acc: any, q: any) => {
              acc[q.question] = q.answer
              return acc
            }, {}),
            enhanced_description: jobData.job.enhanced_description,
          })
          // setEnhancedDescriptionData(jobData.enhanced_description)
        }
      } catch (error) {
        console.error("Error fetching job data:", error)
      }
    }

    fetchJobData()
  }, [])

  // Validation Logic
  useEffect(() => {
    const validateStep = () => {
      const newErrors: { [key: string]: string } = {}

      if (currentStep === 1) {
        newErrors.jobTitle = validateJobTitle(jobKeyDetails.jobTitle)
        newErrors.jobType = validateJobType(jobKeyDetails.jobType)
        newErrors.jobLocation = validateJobLocation(jobKeyDetails.jobLocation)
        newErrors.workplacetype = validateWorkplaceType(jobKeyDetails.workplacetype)
        newErrors.salary = validateSalary(jobKeyDetails.minsalary)
        if (!newErrors.salary) {
          newErrors.salary = validateSalary(jobKeyDetails.maxsalary)
        }
        if (!newErrors.salary) {
          newErrors.salary = validateCompareSalaries(jobKeyDetails.minsalary, jobKeyDetails.maxsalary)
        }
        newErrors.target_date = validateTargetDate(jobKeyDetails.target_date)
        newErrors.teamsize = validateTeamSize(jobKeyDetails.teamsize)
        newErrors.workExp = validateWorkExp(jobKeyDetails.workminexp)
        if (!newErrors.workExp) {
          newErrors.workExp = validateWorkExp(jobKeyDetails.workmaxexp)
        }
        if (!newErrors.workExp) {
          newErrors.workExp = validateCompareWorkExp(jobKeyDetails.workminexp, jobKeyDetails.workmaxexp)
        }
      } else if (currentStep === 2) {
        newErrors.description = validateJobDescription(jobDescription.description)
      }

      setErrors(newErrors)
      const isValid = Object.values(newErrors).every((error) => !error)
      if (currentStep === 5) {
        setIsSubmitDisabled(false)
      } else {
        setIsNextDisabled(!isValid)
      }
    }

    validateStep()
  }, [currentStep, jobKeyDetails, jobDescription, aiDetails])

  // Navigation Handlers
  const handleNext = () => {
    if (currentStep < totalSteps) {
      window.scrollTo({
        top: 0,
        
      });
      setCurrentStep(currentStep + 1)
    }
  }

  const handleBack = () => {
    if (currentStep > 1) {
      window.scrollTo({
        top: 0,
      });
      setCurrentStep(currentStep - 1)
    }
  }

  const handlePublishDetailsChange = (fieldName: string, value: any) => {
    setPublishDetails((prevDetails) => ({
      ...prevDetails,
      [fieldName]: value,
    }))
  }

  const handleValueUpdate = (name: string, updatedValue: number) => {
    switch (name) {
      case "minsalary":
        if (updatedValue < 1) return 1
        if (updatedValue > 99) return 99
        return updatedValue
      case "maxsalary":
        if (updatedValue < 2) return 2
        if (updatedValue > 100) return 100
        return updatedValue
      case "workminexp":
        if (updatedValue < 1) return 1
        if (updatedValue > 49) return 49
        return updatedValue
      case "workmaxexp":
        if (updatedValue < 2) return 2
        if (updatedValue > 50) return 50
        return updatedValue
      default:
        return updatedValue
    }
  }

  // Handle Form Submission
  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()

    // Check if the publish button was clicked
    const submitter = (e.nativeEvent as SubmitEvent).submitter as HTMLButtonElement
    if (submitter.name === "publish") {
      // Prepare payload
      const payload = {
        title: jobKeyDetails.jobTitle,
        type: jobKeyDetails.jobType,
        workplace_type: jobKeyDetails.workplacetype,
        status: "ACTIVE",
        target_date: jobKeyDetails.target_date,
        location: jobKeyDetails.jobLocation,
        team_size: jobKeyDetails.teamsize,
        min_salary: jobKeyDetails.minsalary,
        max_salary: jobKeyDetails.maxsalary,
        min_experience: jobKeyDetails.workminexp,
        max_experience: jobKeyDetails.workmaxexp,
        description: jobDescription.description,
        enhanced_description: aiDetails.enhanced_description,
        is_posted_for_client: companyDetails.is_posting_client,
        company: {
          name: companyDetails.companyName,
          website: companyDetails.website,
          number_of_employees: companyDetails.employees,
          industry_type: companyDetails.industry,
          linkedin: companyDetails.companylinkedIn,
          type: companyDetails.companytype,
        },
        ai_clarifying_questions: Object.entries(aiDetails.aiInput).map(([question, answer]) => ({
          question,
          answer,
        })),
        publish_on_career_page: publishdetails.PublishOnCareerPage,
        publish_on_other_domains: publishdetails.PublishOnOtherDomains,
        publish_on_job_boards: publishdetails.PublishedDomainNames,
      }
      try {
        setIsLoading(true)
        let response
        if (!jobId) {
          response = await apiService("/jobs", "POST", payload)
          toast({
            variant: "default",
            title: "Success",
            description: "Job created successfully",
            duration: 5000,
          })
        } else {
          if (actionType === "Edit") {
            response = await apiService(`/jobs/${jobId}`, "PUT", payload)
            toast({
              variant: "default",
              title: "Success",
              description: "Job update successfully",
              duration: 5000,
            })
          } else {
            response = await apiService("/jobs", "POST", payload)
            toast({
              variant: "default",
              title: "Success",
              description: "Job created successfully",
              duration: 5000,
            })
          }
        }
        if (!response.status) {
          throw new Error("Network response was not ok")
        }
        
        router.push("/dashboard")
       
      } catch (error) {
        console.error("Error creating job:", error)
        toast({
          variant: "destructive",
          title: "Failed",
          description: "An error occurred while creating the job",
          duration: 5000,
        })
      } finally {
        setIsLoading(false)
      }
    }
  }

  // Render Current Step Component
  const renderStep = () => {
    switch (currentStep) {
      case 1:
        return (
          <Step1JobKeyDetails
            data={jobKeyDetails}
            onChange={(e) => {
              const { name, value } = e.target
              if (value === "") {
                setJobKeyDetails((prevDetails) => ({
                  ...prevDetails,
                  [name]: "",
                }))
                return
              }

              if (minMaxFields.includes(name)) {
                const numericValue = Number(value)
                const sanitizedValue = numericValue <= 0 ? 1 : numericValue

                setJobKeyDetails((prevDetails) => ({
                  ...prevDetails,
                  [name]: sanitizedValue,
                }))
                return
              }

              setJobKeyDetails((prevDetails) => ({
                ...prevDetails,
                [name]: value,
              }))
            }}
            handleTargetFunc={(name, value) =>
              setJobKeyDetails((prevDetails) => ({
                ...prevDetails,
                [name]: value,
              }))
            }
            onBlur={(e) => {
              const { name, value } = e.target
              const updatedValue = Number(value)
              if (value === "") {
                setJobKeyDetails((prevDetails) => ({
                  ...prevDetails,
                  [name]: "",
                }))
                return
              }
              // Apply validation on blur event
              setJobKeyDetails((prevDetails) => ({
                ...prevDetails,
                [name]: handleValueUpdate(name, updatedValue),
              }))
            }}
            errors={errors}
            onJobLocationSelect={(jobLocation) => {
              setJobKeyDetails((prevDetails) => ({
                ...prevDetails,
                jobLocation,
              }))
            }}
            onBack={handleBack}
            onNext={handleNext}
          />
        )
      case 2:
        return (
          <Step2JobDescription
            data={jobDescription}
            onChange={(value) =>
              setJobDescription({
                ...jobDescription,
                description: value,
              })
            }
            errors={errors}
            onBack={handleBack}
            onNext={handleNext}
          />
        )
      case 3:
        return (
          <Step3CompanyDetails
            data={companyDetails}
            onChange={(e) =>
              setCompanyDetails({
                ...companyDetails,
                [e.target.name]: e.target.value,
              })
            }
            errors={errors}
            onIndustrySelect={(industry) => setCompanyDetails({ ...companyDetails, industry })}
            onCompanyDetails={(updatedDetails) => setCompanyDetails({ ...companyDetails, ...updatedDetails })}
            setErrors={setErrors}
            onBack={handleBack}
            onNext={handleNext}
          />
        )
      case 4:
        return (
          <Step4AI
            data={aiDetails}
            questions={questions}
            onChange={(newData: any) => setAIDetails(newData)}
            errors={errors}
            onBack={handleBack}
            onNext={handleNext}
            jobDescription={jobDescription.description}
            originalJD={originalJobDescription.description}
          />
        )
      case 5:
        return (
          <Preview
            jobKeyDetails={jobKeyDetails}
            jobDescription={jobDescription}
            companyDetails={companyDetails}
            aiDetails={aiDetails}
            questions={questions}
            onBack={handleBack}
            onNext={handleNext}
          />
        )
      case 6:
        return <Step5Publish data={publishdetails} onChange={handlePublishDetailsChange} errors={{}} />
      default:
        return null
    }
  }

  const stepNames = [
    "Job Key Details",
    "Job Description",
    "Company Details",
    "AI Clarification Questions",
    "Preview",
    "Publish",
  ]

  return (
    <div className="flex items-center bg-gray-50 p-2 w-full">
      <div className=" rounded-lg p-4 w-full">
        {jobId ? (
          <h1 className="font-bold text-2xl pb-4">Edit Job</h1>
        ) : (
          <h1 className="font-semibold text-xl pb-4 Inter">Create Job</h1>
        )}

        <StepIndicator currentStep={currentStep} steps={stepNames} />

        <form onSubmit={(e) => handleSubmit(e)} className={currentStep === totalSteps ? "bg-white" : ""}>
          {renderStep()}
          <div>
            <div className={` mr-5 flex justify-end space-x-4 pb-6  ${currentStep !== totalSteps ? "mt-5" : ""}`}>
              {currentStep === totalSteps && (
                <button
                  type="button"
                  onClick={handleBack}
                  className="bg-white border border-[1px] border-gray-300 px-4 py-2 rounded-md w-[105px] h-[40px]"
                >
                  Back
                </button>
              )}
              {currentStep === totalSteps && (
                <button
                  type="submit"
                  name="publish"
                  disabled={isSubmitDisabled || isLoading}
                  className={`px-4 py-2 rounded-md w-[150px] h-[40px] flex items-center justify-center ${
                    isSubmitDisabled || isLoading ? "bg-gray-400 cursor-not-allowed" : "bg-blue-600 hover:bg-blue-700"
                  } text-white transition-colors duration-200`}
                >
                  {actionType === "Repost" ? "Publish as New" : "Publish"}
                </button>
              )}
            </div>
          </div>
        </form>
      </div>
      <div>
        {isLoading && (
          <div className="absolute loader top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 flex items-center justify-center">
            <Loader2 className="mr-2 h-[30px] w-12 animate-spin" />
          </div>
        )}
      </div>
    </div>
  )
}

export default MultiStepForm

