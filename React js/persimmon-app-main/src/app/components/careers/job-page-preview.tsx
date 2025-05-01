"use client"
import { jobDescription } from "@/app/components/careers/config"
import { Button } from "@/components/ui/button"
import { BookOpenText, MapPin, Briefcase, Building, IndianRupee } from "lucide-react"
import { useRef } from "react"
import { JobsTab } from "@/app/components/careers/config"
import { Card } from "@/components/ui/card"
import Header from "@/app/components/careers/header-demo"
import InfoItem from "./info-items"
import ApplyForm from "./apply-form"
import type { CustomizationSettings } from "@/app/types/customization"

interface JobPagePreviewProps {
  settings: CustomizationSettings
}

export function JobPagePreview({ settings }: JobPagePreviewProps) {
  const formRef = useRef<HTMLDivElement>(null)

  const scrollToForm = () => {
    formRef.current?.scrollIntoView({ behavior: "smooth", block: "start" })
  }

  const darkModeClasses = settings.darkMode ? "bg-[#0F172A] text-white" : "bg-white text-black"

  const cardClasses = settings.darkMode ? "bg-slate-800 text-slate-200" : "bg-[#f8fafc] text-black"

  return (
    <div className={`rounded-lg w-full ${darkModeClasses} overflow-hidden`} style={{ fontFamily: settings.fontStyle }}>
      <Header settings={settings} careerPage={false} />
      <div className={`p-4 sm:p-6 ${cardClasses}`}>
        <div className={`flex flex-col sm:flex-row justify-between items-start gap-4 mb-4`}>
          <div className="w-full">
            <div className={`text-sm ${settings.darkMode ? "text-slate-200" : "text-muted-foreground"} mb-2`}>
              Job Id: SYM2567
            </div>
            <h1 className="text-xl sm:text-2xl font-semibold mb-4 sm:mb-6">Software Engineer</h1>
            <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-4 sm:gap-6 lg:gap-12 items-start	">
              <InfoItem
                icon={<IndianRupee className="h-4 w-4 sm:h-5 sm:w-5" />}
                heading="Salary"
                message="5 LPA - 10 LPA"
                settings={settings}
              />
              <InfoItem
                icon={<BookOpenText className="h-4 w-4 sm:h-5 sm:w-5" />}
                heading="Experience"
                message="2 - 3 Years"
                settings={settings}
              />
              <InfoItem
                icon={<MapPin className="h-4 w-4 sm:h-5 sm:w-5" />}
                heading="Location"
                message="Vijayawada"
                settings={settings}
              />
              <InfoItem
                icon={<Briefcase className="h-4 w-4 sm:h-5 sm:w-5" />}
                heading="Job Type"
                message="Full Time"
                settings={settings}
              />
              <InfoItem
                icon={<Building className="h-4 w-4 sm:h-5 sm:w-5" />}
                heading="Work Place Type"
                message="On-Site"
                settings={settings}
              />
            </div>
          </div>
          <Button
            className="w-full sm:w-auto mt-4 sm:mt-0"
            style={{ backgroundColor: settings.primaryColor }}
            onClick={scrollToForm}
          >
            Apply Now
          </Button>
        </div>
      </div>

      <div className={`p-4 sm:p-6 sm:px-8 lg:px-12 ${darkModeClasses}`}>
        <div className="grid grid-cols-1 lg:grid-cols-[1fr,300px] gap-6">
          <div className="space-y-6">
            <Card className={`border-none p-4 ${cardClasses} overflow-hidden`}>
              <div
                className="text-sm leading-7 overflow-auto"
                dangerouslySetInnerHTML={{ __html: jobDescription.description }}
              ></div>
            </Card>

            <div ref={formRef} className="mt-6">
              <ApplyForm settings={settings} />
            </div>
          </div>

          <div>
            <Card className={`border-none ${cardClasses} overflow-hidden`}>
              <h3 className="font-semibold mb-4 border-b w-full p-4">All Jobs</h3>
              <div className="space-y-3 max-h-[400px] overflow-y-auto">
                {JobsTab.map((job, index) => (
                  <div
                    key={index}
                    className={`p-3 border-b hover:bg-opacity-80 ${settings.darkMode ? "hover:bg-slate-700" : "hover:bg-slate-100"}`}
                  >
                    <div className={`font-semibold mb-1 ${job.title === "Java Developer" ? "text-primary" : ""}`}>
                      {job.title}
                    </div>
                    <div
                      className={`text-[10px] ${settings.darkMode ? "text-slate-300" : "text-muted-foreground"} font-medium`}
                    >
                      2-3 Years | {job.location} | {job.type} | {job.workplace}
                    </div>
                  </div>
                ))}
              </div>
            </Card>
          </div>
        </div>
      </div>
    </div>
  )
}

