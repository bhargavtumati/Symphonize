"use client"
import { ArrowLeft, CalendarClock, Loader2 } from "lucide-react"
import { useRouter } from "next/navigation"
import { ApplicantProfile } from "@/app/components/applicant-profile"
import { Button } from "@/components/ui/button"
import { auth } from "@/app/components/firebaseConfig"
import { apiService } from "@/app/api/service"
import { useEffect, useState } from "react"
import { toast } from "@/components/hooks/use-toast"
import { usePathname } from "next/navigation"
import type { Applicant } from "@/app/types/applicants"
import { Select, SelectContent, SelectGroup, SelectItem, SelectValue, SelectTrigger } from "@/components/ui/select"
import { ScheduleInterviewDialog } from "@/app/components/schedule-interview-dailog"
import { useSearchParams } from "next/navigation"

export default function ApplicantPage() {
  const [stages, setStages] = useState<{ uuid: string; name: string }[]>([])
  //const [selectedValue, setSelectedValue] = useState<string>(""); // Default selected value
  const [loading, setLoading] = useState<boolean>(true)
  const [applicantData, setApplicant] = useState<Applicant | undefined>()
  const [jobId, setJobId] = useState<number | undefined>()
  const [verifyingEmailService, setVerifyingEmailService] = useState(false)
  const pathname = usePathname()
  const segments = pathname.split("/")
  const [originalStages, setOriginalStages] = useState<{ uuid: string; name: string }[]>([])
  const id = segments[segments.length - 1] // Extract the last segment
  const router = useRouter()
  const searchParams = useSearchParams()
  const status = searchParams.get("status")

  const [emailServiceStatus, setEmailServiceStatus] = useState(null)
  const [indidualEmailServiceStatus, setIndidualEmailServiceStatus] = useState(null)

  const getApplicant = () => {
    const unsubscribe = auth.onAuthStateChanged(async (user) => {
      setLoading(true)
      if (user) {
        try {
          const applicantDatails = await apiService(`/applicants/${id}`, "GET", null)
          if (!applicantDatails) throw new Error("Failed to fetch applicant details")
          setApplicant(applicantDatails.data)
          setJobId(applicantDatails.data.job_id)
          setLoading(false)
        } catch (error: any) {
          console.log(error.message)
          toast({
            variant: "destructive",
            title: "Error fetching applicant",
            description: error.message || "An unexpected error occurred",
          })
          setLoading(false)
        }
      }
    })
    return () => unsubscribe()
  }

  useEffect(() => {
    getApplicant()
  }, [])

  useEffect(() => {
    if (!jobId) return
    setLoading(true)
    const unsubscribe = auth.onAuthStateChanged(async (user) => {
      if (user) {
        try {
          const idToken = await user.getIdToken()
          if (idToken) {
            const response = await apiService(`/stages?job_id=${jobId}`, "GET", null) // Use jobId for API call
            if (!response) throw new Error("Failed to fetch job details")
            setOriginalStages(JSON.parse(JSON.stringify(response.stages)))
            setLoading(false)
          }
        } catch (error: any) {
          toast({
            variant: "destructive",
            title: "Error fetching applicants",
            description: error.message || "An unexpected error occurred",
          })
          setLoading(false)
        }
      } else {
        toast({
          variant: "destructive",
          title: "Authentication required",
          description: "",
        })
        setLoading(false)
      }
    })

    return () => unsubscribe()
  }, [jobId])

  const handleMoveTo = async (stageId: string) => {
    setLoading(true)
    const payload = {
      applicant_uuids: [id],
      stage_uuid: stageId,
    }

    try {
      const result = await apiService(`/applicants?job_id=${jobId}`, "PATCH", payload)
      console.log(result)
      getApplicant()
      setLoading(false)
      toast({
        variant: "default",
        title: "Stage updated successfully",
        description: "",
      })
    } catch (error: any) {
      console.log("error for this", error)
      setLoading(false)
      toast({
        variant: "destructive",
        title: "",
        description: error.message || "unexpected error occurred",
      })
    }
  }

  const onAllApplicants = (jobId: number | undefined) => {
    const jobCode = searchParams.get("jobCode")
    router.push(`/dashboard/view-job-page/all-applicants?jobId=${jobId}&jobCode=${jobCode}`)
  }

  const verifyEmailService = async () => {
    setVerifyingEmailService(true)
    console.log('this is the back test')
    try {
      const verifiedValue = await apiService(`/integration/email/verify-from-address`, "GET", null)
      if (!verifiedValue) {
        toast({
          variant: "destructive",
          title: "Email service not verified",
          description: "Please verify your email service before scheduling an interview",
        })
      }
      if (verifiedValue.message === "Email Integration details not found") {
        setEmailServiceStatus(verifiedValue.data)
        return { emailServiceStatus: verifiedValue.data, indidualEmailServiceStatus: true }
      } else if (
        verifiedValue.message ===
        "Your email not found within any integrated email service, please contact your administrator"
      ) {
        setIndidualEmailServiceStatus(verifiedValue.data)
        return { emailServiceStatus: true, indidualEmailServiceStatus: verifiedValue.data }
      } else {
        setEmailServiceStatus(verifiedValue.data)
        setIndidualEmailServiceStatus(verifiedValue.data)
      }
      return { emailServiceStatus: true, indidualEmailServiceStatus: true }
    } catch (error) {
      console.error("Error verifying email service:", error)
      toast({
        variant: "destructive",
        title: "Error",
        description: "Failed to verify email service",
      })
      return null
    } finally {
      setVerifyingEmailService(false)
    }
  }

  return (
    <div className="container py-4 max-w-7xl">
      <div className="flex justify-between items-center gap-4 mb-4">
        <div className="flex items-center" onClick={() => onAllApplicants(applicantData?.job_id)}>
          <Button variant="ghost" size="icon">
            <ArrowLeft className="h-5 w-5 text-slate-500" />
          </Button>

          <h1 className="text-[16px] text-slate-500 leading-6">Applicants</h1>
        </div>
        <div className="flex space-x-4">
          <div
            className={`flex items-center justify-around text-black text-[12px] font-medium space-x-4 ${status === "Closed" ? "cursor-not-allowed" : "cursor-pointer"}`}
          >
            <ScheduleInterviewDialog
              applicantData={applicantData}
              onScheduleClick={verifyEmailService}
              verifyingEmailService={verifyingEmailService}
            >
              <Button
                backgroundColor="#fff"
                className="text-black border border-slate-200"
                disabled={status === "Closed"}
              >
                {verifyingEmailService ? (
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                ) : (
                  <CalendarClock strokeWidth={2} className="mr-2 h-4 w-4" />
                )}
                Schedule Interview
              </Button>
            </ScheduleInterviewDialog>
          </div>

          <div className="flex items-center justify-around text-black text-[12px] font-medium">
            <Select
              value={
                originalStages.some((stage) => stage.uuid === applicantData?.stage_uuid)
                  ? applicantData?.stage_uuid
                  : undefined
              }
              onValueChange={handleMoveTo}
              disabled={status === "Closed"}
            >
              <SelectTrigger className="w-full whitespace-nowrap space-x-2">
                <SelectValue placeholder="Move To" />
              </SelectTrigger>
              <SelectContent>
                <SelectGroup>
                  {originalStages.map((stage) => (
                    <SelectItem key={stage.uuid} value={stage.uuid}>
                      {stage.name}
                    </SelectItem>
                  ))}
                </SelectGroup>
              </SelectContent>
            </Select>
          </div>
        </div>
      </div>
      <ApplicantProfile applicantData={applicantData} isLoading={loading} />
    </div>
  )
}

