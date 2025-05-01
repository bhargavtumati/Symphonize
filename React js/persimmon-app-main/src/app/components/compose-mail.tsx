import { Button } from "@/components/ui/button"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import LabeledInput from "./labeled-Input"
import RichTextEditor from "./timymce-editor"
import { useEffect, useMemo, useState } from "react"
import { apiService } from "../api/service"
import type { JobCardProps, PreferenceApiCandidateRespo, RecruiterResponse, Template } from "../types/model"
import { cn } from "@/lib/utils"
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "@/components/ui/dropdown-menu"
import { ChevronDown } from "lucide-react"
import { formatText, normalizeString } from "../utils/helper"

interface ComposeMailProps {
  selectedTemplate: Template | undefined
  onEditorInit: (editor: any) => void
  sendToAllData: any
  setSendToAllData: React.Dispatch<React.SetStateAction<any>>
  setShowCustomInput: React.Dispatch<React.SetStateAction<boolean>>
  showCustomInput: boolean
  selectedCandidatesDetails: PreferenceApiCandidateRespo[]
  jobDetails: JobCardProps | null
  handleCustomTemplateConfirm: () => Promise<void>
  allSameStage: boolean
  setIsDifferentStages: React.Dispatch<React.SetStateAction<boolean>>
  handleSendToAllSubmit: () => Promise<void>
  setAttachedFiles: React.Dispatch<React.SetStateAction<File[]>>
  setIsDialogOpen: React.Dispatch<React.SetStateAction<boolean>>
  setIsMailSent: React.Dispatch<React.SetStateAction<boolean>>
  attachedFiles: File[]
  threeHrsFromNow: Date
  recruiterData: RecruiterResponse | undefined
}


const ComposeMail: React.FC<ComposeMailProps> = ({
  selectedTemplate,
  onEditorInit,
  sendToAllData,
  setSendToAllData,
  setShowCustomInput,
  showCustomInput,
  jobDetails,
  handleCustomTemplateConfirm,
  allSameStage,
  setIsDifferentStages,
  handleSendToAllSubmit,
  setAttachedFiles,
  setIsDialogOpen,
  setIsMailSent,
  attachedFiles,
  recruiterData
}) => {
  const [isBodyChanged, setIsBodyChanged] = useState(false);
  const [isSubjectChanged, setIsSubjectChanged] = useState(false);

  useEffect(() => {
    setSendToAllData((prevData: any) => ({
      ...prevData,
      body: selectedTemplate?.body || "",
      subject: selectedTemplate?.subject || "", // Updates body with new template
    }))
    setIsBodyChanged(false)
    setIsSubjectChanged(false)
  }, [selectedTemplate])

  const useKeyNotPresent = (key: string, body: string) => {
    return useMemo(() => {
      return !body.includes(key) // Equivalent to isStringNotPresent
    }, [body, key])
  }
  const [sendTestMailData, setSendTestMailData] = useState({
    from_email: "careers@tekworks.ai",
    to_email: "",
    subject: "",
    body: "",
    candidate_name: "",
    job_title: formatText(jobDetails?.job?.title || ""),
    job_location: formatText(jobDetails?.job?.location || ""),
    company_name: formatText(jobDetails?.company?.name || ""),
    job_type: formatText(jobDetails?.job?.type || ""),
    title: formatText(jobDetails?.job?.title || ""),
    workplace_type: formatText(jobDetails?.job?.workplace_type || ""),
    min_experience: jobDetails?.job?.min_experience || "",
    max_experience: jobDetails?.job?.max_experience || "",
    min_salary: jobDetails?.job?.min_salary || "",
    max_salary: jobDetails?.job?.max_salary || "",
    industry: formatText(jobDetails?.company?.industry_type || ""),
    company_type: formatText(jobDetails?.company?.type || ""),
    company_size: formatText(jobDetails?.company?.number_of_employees || ""),
    company_website: formatText(jobDetails?.company?.website || ""),
    recruiter_contact_number: formatText(recruiterData?.recruiter?.whatsapp_number || ""),
    recruiter_name: formatText(recruiterData?.recruiter?.full_name || ""),
    recruiter_designation: formatText(recruiterData?.recruiter?.designation || ""),
  })



  const handleSendToAllChange = (field: string, value: string | string[]) => {
    setSendToAllData((prev: any) => ({ ...prev, [field]: value }))
    if (field === "subject") {
      setIsSubjectChanged(value !== selectedTemplate?.subject)
    }
  }

  const handleSendTestMailChange = (field: string, value: string | string[]) => {
    setSendTestMailData((prev) => ({ ...prev, [field]: value }))
  }

  const handleEditorChange = (updatedValue: string) => {
    const strippedUpdateValue = normalizeString(updatedValue);
    const strippedSelectedBody = normalizeString(selectedTemplate?.body || "");

    setSendToAllData((prev: any) => ({ ...prev, body: updatedValue }));
    setIsBodyChanged(strippedUpdateValue !== strippedSelectedBody);
  };

  const handleFileAttach = (file: File[]) => {
    setAttachedFiles((prev) => [...prev, ...file]);
  };

  const handleSaveAsNew = () => {
    setShowCustomInput(true)
  }

  const handleIsDifferentStages = () => {
    setIsDifferentStages(true);
  }


  const handleSendTestMailSubmit = async () => {
    const formData = new FormData()
    // Ensure the body template exists
    const bodyTemplate = sendToAllData.body || ""

    // Define key mapping between placeholders and actual object keys
    const keyMapping: Record<string, keyof typeof sendTestMailData> = {
      CandidateName: "candidate_name",
      JobTitle: "job_title",
      JobLocation: "job_location",
      RecruiterName: "recruiter_name",
      CompanyName: "company_name",
      JobType: "job_type",
      Title: "title",
      WorkplaceType: "workplace_type",
      MinExperience: "min_experience",
      MaxExperience: "max_experience",
      MinSalary: "min_salary",
      MaxSalary: "max_salary",
      Industry: "industry",
      CompanyType: "company_type",
      CompanySize: "company_size",
      CompanyWebsite: "company_website",
      RecruiterContactNumber: "recruiter_contact_number",

    }

    // Replace placeholders with values from sendTestMailData
    let replacedSubject = sendToAllData.subject.replace(/{{(\w+)}}/g, (_: any, key: string) => {
      const mappedKey = keyMapping[key]; // Get mapped key
      return mappedKey && sendTestMailData[mappedKey] ? sendTestMailData[mappedKey] : "";
    });

    let replacedBody = bodyTemplate.replace(/{{(\w+)}}/g, (_: any, key: string) => {
      const mappedKey = keyMapping[key]; // Get mapped key
      return mappedKey && sendTestMailData[mappedKey] ? sendTestMailData[mappedKey] : "";
    });

    // Remove attached file names from the editor body
    attachedFiles.forEach(file => {
      const fileName = file.name;

      // Escape special characters in filename to prevent regex issues
      const escapedFileName = fileName.replace(/[-\/\\^$*+?.()|[\]{}]/g, "\\$&");

      // Remove entire <a> tag if it contains the file name
      const anchorPattern = new RegExp(`<a[^>]*>\\s*${escapedFileName}\\s*<\\/a>`, "gi");
      replacedBody = replacedBody.replace(anchorPattern, "");

      // Remove the file name if it exists outside <a> tags
      const textPattern = new RegExp(`\\b${escapedFileName}\\b`, "gi");
      replacedBody = replacedBody.replace(textPattern, "");
    });



    Object.entries(sendTestMailData).forEach(([key, value]) => {
      formData.append(
        key,
        key === "body" ? replacedBody : key === "subject" ? replacedSubject : value
      );
    });
    attachedFiles.forEach((file) => {
      formData.append(`files`, file);
    });


    try {
      const response = await apiService("/email/test-email", "POST", formData, true)
      setIsMailSent(true)
      if (!response.ok) {
        throw new Error(`Error: ${response.status} ${response.statusText}`)
      }
    } catch (error) {
      console.error("Failed to send data:", error)
    }
    setIsDialogOpen(false)
  }

  return (
    <div className="flex justify-between items-center pb-2">
      <Tabs defaultValue="send_to_all" className="flex-1">
        <div className="flex">
          <h2 className="text-base font-bold mt-4">Compose Mail</h2>
          <div className="w-[225px] rounded-md bg-[#E4EEF9] mt-4 text-muted-foreground ml-auto">
            <TabsList className="h-8">
              <TabsTrigger value="send_to_all" className="w-[107px] font-semibold text-xs">
                Sent to all
              </TabsTrigger>
              <TabsTrigger value="send_test_mail" className="w-[107px] font-semibold text-xs">
                Send Test Mail
              </TabsTrigger>
            </TabsList>
          </div>
        </div>
        <TabsContent value="send_to_all" className="mt-0 space-y-4">
          <div className="space-y-4 mt-4">
            <div className="grid gap-4">
              <LabeledInput
                label="From"
                type="email"
                placeholder=""
                badgeClass="absolute h-6 w-[70px] justify-center left-2 top-1/2 -translate-y-1/2 rounded-sm border-none bg-slate-100 px-2 py-1 text-[14px] font-normal text-black"
                inputClass="rounded-md border-[1px] border-[#CBD5E1] "
                containerClass="relative w-full"
                tabtype="send_to_all"
                value={sendToAllData.from_email}
                onChange={(value) => handleSendToAllChange("from_email", value)}
                name="from"
              />
              <LabeledInput
                label="To"
                type="email"
                placeholder=""
                badgeClass="absolute h-6 w-[70px] justify-center left-2 top-1/2 -translate-y-1/2 rounded-sm border-none bg-slate-100 px-2 py-1 text-[14px] font-normal text-black"
                inputClass="rounded-md border-[1px] border-[#CBD5E1]"
                containerClass="relative w-full"
                tabtype="send_to_all"
                value={sendToAllData.to_email}
                onChange={(value) => handleSendToAllChange("to_email", value)}
                name="to"
              />
              <LabeledInput
                label="Subject"
                type="text"
                placeholder="Add a subject"
                badgeClass="absolute h-6 w-[70px] justify-center left-2 mt-2 rounded-sm border-none bg-slate-100 px-2 text-[14px] font-normal text-black"
                inputClass="rounded-md border-[1px] border-[#CBD5E1] pl-24 h-[40px]"
                containerClass="relative w-full"
                tabtype="send_to_all"
                value={(isBodyChanged || isSubjectChanged) ? sendToAllData.subject : showCustomInput ? "" : sendToAllData.subject}
                onChange={(value) => handleSendToAllChange("subject", value)}
                name="subject"
              />
            </div>
            <div className="editor">
              <RichTextEditor
                value={(isBodyChanged || isSubjectChanged) ? sendToAllData.body : showCustomInput ? "" : sendToAllData.body}
                onChange={handleEditorChange}
                onFileAttach={handleFileAttach}
                onEditorInit={onEditorInit}
                placeholder="Type / to insert files and more"
                attachedFiles={attachedFiles}
                setAttachedFiles={setAttachedFiles}
              />
            </div>
          </div>

          <div className={cn("flex", (isBodyChanged || isSubjectChanged) ? "justify-between" : "justify-end")}>
            {(isBodyChanged || isSubjectChanged) && (selectedTemplate?.default ?
              <Button variant="outline" onClick={handleSaveAsNew} className="gap-2">Save as New</Button> :
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="outline" className="gap-2 w-32 h-10 flex justify-between items-center">
                    <span>Save</span>
                    <span className="border-l border-gray-200 h-10 ml-6"></span>
                    <ChevronDown className="h-4 w-4" />
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent>
                  <DropdownMenuItem onClick={handleCustomTemplateConfirm}>Save</DropdownMenuItem>
                  <DropdownMenuItem onClick={handleSaveAsNew}>Save as</DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            )}
            <Button onClick={allSameStage ? handleSendToAllSubmit : handleIsDifferentStages}>Send Email</Button>
          </div>

        </TabsContent>
        <TabsContent value="send_test_mail" className="mt-0">
          <div className="grid gap-4 mt-8">
            <LabeledInput
              label="From"
              type="text"
              placeholder=""
              value={sendTestMailData.from_email}
              onChange={(value) => handleSendTestMailChange("from_email", value)}
              name="from"
              isLocked={true}
            />
            <LabeledInput
              label="To"
              type="text"
              placeholder="Enter Email here"
              value={sendTestMailData.to_email}
              onChange={(value) => handleSendTestMailChange("to_email", value)}
              name="to"
            />
            <LabeledInput
              label="Candidate Name"
              type="text"
              placeholder="Enter Name"
              value={sendTestMailData.candidate_name}
              onChange={(value) => handleSendTestMailChange("candidate_name", value)}
              name="candidateName"
            />
            <LabeledInput
              label="Job Title"
              type="text"
              placeholder=""
              value={sendTestMailData.job_title}
              onChange={(value) => handleSendTestMailChange("job_title", value)}
              name="JobTitle"
              keyNotPresent={useKeyNotPresent("{{JobTitle}}", sendToAllData.body)}
              isLocked={true}
            />
            <LabeledInput
              label="Job Location"
              type="text"
              placeholder=""
              value={sendTestMailData.job_location}
              onChange={(value) => handleSendTestMailChange("job_location", value)}
              name="JobLocation"
              keyNotPresent={useKeyNotPresent("{{JobLocation}}", sendToAllData.body)}
              isLocked={true}
            />

            <LabeledInput
              label="Company Name"
              type="text"
              placeholder="Enter Company Name"
              value={sendTestMailData.company_name}
              onChange={(value) => handleSendTestMailChange("company_name", value)}
              name="CompanyName"
              keyNotPresent={useKeyNotPresent("{{CompanyName}}", sendToAllData.body)}
              isLocked={true}
            />
            <LabeledInput
              label="Title"
              type="text"
              placeholder=""
              value={sendTestMailData.title}
              onChange={(value) => handleSendTestMailChange("title", value)}
              name="Title"
              keyNotPresent={useKeyNotPresent("{{Title}}", sendToAllData.body)}
              isLocked={true}
            />

            <LabeledInput
              label="Workplace Type"
              type="text"
              placeholder=""
              value={sendTestMailData.workplace_type}
              onChange={(value) => handleSendTestMailChange("workplace_type", value)}
              name="WorkplaceType"
              keyNotPresent={useKeyNotPresent("{{WorkplaceType}}", sendToAllData.body)}
              isLocked={true}
            />
            <LabeledInput
              label="Min Experience"
              type="number"
              placeholder=""
              value={sendTestMailData.min_experience}
              onChange={(value) => handleSendTestMailChange("min_experience", value)}
              name="MinExperience"
              keyNotPresent={useKeyNotPresent("{{MinExperience}}", sendToAllData.body)}
              isLocked={true}
            />

            <LabeledInput
              label="Max Experience"
              type="number"
              placeholder=""
              value={sendTestMailData.max_experience}
              onChange={(value) => handleSendTestMailChange("max_experience", value)}
              name="MaxExperience"
              keyNotPresent={useKeyNotPresent("{{MaxExperience}}", sendToAllData.body)}
              isLocked={true}
            />

            <LabeledInput
              label="Min Salary"
              type="number"
              placeholder=""
              value={sendTestMailData.min_salary}
              onChange={(value) => handleSendTestMailChange("min_salary", value)}
              name="MinSalary"
              keyNotPresent={useKeyNotPresent("{{MinSalary}}", sendToAllData.body)}
              isLocked={true}
            />

            <LabeledInput
              label="Max Salary"
              type="number"
              placeholder=""
              value={sendTestMailData.max_salary}
              onChange={(value) => handleSendTestMailChange("max_salary", value)}
              name="MaxSalary"
              keyNotPresent={useKeyNotPresent("{{MaxSalary}}", sendToAllData.body)}
              isLocked={true}
            />

            <LabeledInput
              label="Industry"
              type="text"
              placeholder=""
              value={sendTestMailData.industry}
              onChange={(value) => handleSendTestMailChange("industry", value)}
              name="Industry"
              keyNotPresent={useKeyNotPresent("{{Industry}}", sendToAllData.body)}
              isLocked={true}
            />

            <LabeledInput
              label="Company Type"
              type="text"
              placeholder=""
              value={sendTestMailData.company_type}
              onChange={(value) => handleSendTestMailChange("company_type", value)}
              name="CompanyType"
              keyNotPresent={useKeyNotPresent("{{CompanyType}}", sendToAllData.body)}
              isLocked={true}
            />

            <LabeledInput
              label="Company Size"
              type="text"
              placeholder=""
              value={sendTestMailData.company_size}
              onChange={(value) => handleSendTestMailChange("company_size", value)}
              name="CompanySize"
              keyNotPresent={useKeyNotPresent("{{CompanySize}}", sendToAllData.body)}
              isLocked={true}
            />
            <LabeledInput
              label="Company Website"
              type="text"
              placeholder=""
              value={sendTestMailData.company_website}
              onChange={(value) => handleSendTestMailChange("company_website", value)}
              name="CompanyWebsite"
              keyNotPresent={useKeyNotPresent("{{CompanyWebsite}}", sendToAllData.body)}
              isLocked={true}
            />
            <LabeledInput
              label="Recruiter Name"
              type="text"
              placeholder="Enter Recruiter Name"
              value={sendTestMailData.recruiter_name}
              onChange={(value) => handleSendTestMailChange("recruiter_name", value)}
              name="RecruiterName"
              keyNotPresent={useKeyNotPresent("{{RecruiterName}}", sendToAllData.body)}
              isLocked={true}
            />
            <LabeledInput
              label="Recruiter Designation"
              type="text"
              placeholder="Enter Designation"
              value={sendTestMailData.recruiter_designation}
              onChange={(value) => handleSendTestMailChange("recruiter_designation", value)}
              name="RecruiterDesignation"
              keyNotPresent={useKeyNotPresent("{{RecruiterDesignation}}", sendToAllData.body)}
              isLocked={true}
            />
            <LabeledInput
              label="Recruiter Contact Number"
              type="text"
              placeholder="Enter Recruiter Contact Number"
              value={sendTestMailData.recruiter_contact_number}
              onChange={(value) => handleSendTestMailChange("recruiter_contact_number", value)}
              name="RecruiterContactNumber"
              keyNotPresent={useKeyNotPresent("{{RecruiterContactNumber}}", sendToAllData.body)}
              isLocked={true}
            />
          </div>
          <div className="flex justify-end mt-6">
            <Button onClick={handleSendTestMailSubmit} disabled={!Boolean(sendTestMailData.to_email && sendTestMailData.candidate_name)}>Send Test Email</Button>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  )
}
export default ComposeMail

