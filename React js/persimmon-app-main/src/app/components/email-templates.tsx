"use client"

import type React from "react"
import { useEffect, useState, useRef } from "react"
import { Button } from "@/components/ui/button"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Plus } from "lucide-react"
import type { Template } from "../types/model"
import { apiService } from "../api/service"
import InputWithIcons from "./custom-input"
import { cn } from "@/lib/utils"
import { getCurrentUserEmail } from "./AuthProvider"

interface EmailTemplatesProps {
  setSelectedTemplate: React.Dispatch<React.SetStateAction<Template | undefined>>
  apiResponseTemplateName: string
  sendToAllData: any
  setSendToAllData: React.Dispatch<React.SetStateAction<any>>
  setShowCustomInput: React.Dispatch<React.SetStateAction<boolean>>
  showCustomInput: boolean
  handleCustomTemplateConfirm: () => Promise<void>
  templates: Template[]
  setTemplates: React.Dispatch<React.SetStateAction<Template[]>>
  setNewTemplateName: React.Dispatch<React.SetStateAction<string>>
  newTemplateName: string
}

const EmailTemplates: React.FC<EmailTemplatesProps> = ({
  setSelectedTemplate,
  apiResponseTemplateName,
  sendToAllData,
  setShowCustomInput,
  showCustomInput,
  handleCustomTemplateConfirm,
  setTemplates,
  templates,
  setNewTemplateName,
  newTemplateName,
}) => {
  const [selectedTemplate, setLocalSelectedTemplate] = useState<string>("")
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const customInputRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const fetchTemplates = async () => {
      setIsLoading(true)
      try {
        const userEmail = (await getCurrentUserEmail()) as string;
        const CompanyDomain = userEmail.split("@")[1];
        const response = await apiService(`/template/?domain=${CompanyDomain}`, "GET", null)
        setTemplates(response.data.template_data.templates)
      } catch (err) {
        setError("Error fetching templates. Please try again later.")
        console.error("Error fetching templates:", err)
      } finally {
        setIsLoading(false)
      }
    }

    fetchTemplates()
  }, [])

  useEffect(() => {
    if (apiResponseTemplateName && templates.length > 0) {
      const matchedTemplate = templates.find(
        (template) => template?.name?.toLowerCase() === apiResponseTemplateName.toLowerCase(),
      )
      if (matchedTemplate) {
        setLocalSelectedTemplate(matchedTemplate.name || "")
        setSelectedTemplate(matchedTemplate)
      }else{
        const matchingIndex = templates.findIndex(template => template.name === "Shortlisted");
        setLocalSelectedTemplate("Shortlisted")
        setSelectedTemplate(templates[matchingIndex])
      }
    }
  }, [apiResponseTemplateName, setSelectedTemplate, templates])

  const handleTemplateSelection = (template: Template) => {
    setLocalSelectedTemplate(template.name || "")
    setSelectedTemplate(template)
  }

  const handleAddCustomTemplate = () => {
    setShowCustomInput(true)
  }

  const handleCustomTemplateCancel = () => {
    setNewTemplateName("")
    setShowCustomInput(false)
  }

  return (
    <div className="flex h-full flex-col mt-12 pr-2 relative">
      <div className="px-4 font-bold text-base">Email Templates</div>
      <ScrollArea className="flex-1">
        <div className="pl-4">
          {templates.map((template) => (
            <Button
              key={template.uuid}
              variant={selectedTemplate === template.name ? "secondary" : "none"}
              className={cn(
                "w-full justify-start text-left text-slate-600 font-normal text-sm",
                selectedTemplate !== template.name && "hover:bg-slate-50"
              )}
              onClick={() => handleTemplateSelection(template)}
            >
              {template.name}
            </Button>
          ))}
        </div>
      </ScrollArea>
      <div className={`pl-4 pr-2 mt-12 sticky bottom-0 bg-white transition-colors`}>
        {showCustomInput && (
          <div ref={customInputRef} className="bg-white py-2">
            <InputWithIcons
              value={newTemplateName}
              onChange={(e) => setNewTemplateName(e.target.value)}
              onCheckClick={handleCustomTemplateConfirm}
              onXClick={handleCustomTemplateCancel}
            />
          </div>
        )}
        <Button
          variant="outline"
          className="w-48 bg-[#F3F3F3] border-[#DBDBDB] text-xs font-normal justify-start text-slate-700 flex justify-center"
          size="sm"
          onClick={handleAddCustomTemplate}
        >
          <Plus className="h-4 w-4" />
          Custom Template
        </Button>
      </div>
    </div>
  )
}

export default EmailTemplates

