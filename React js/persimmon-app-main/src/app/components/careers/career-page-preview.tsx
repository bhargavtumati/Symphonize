"use client"

import { JobCard } from "@/app/components/careers/job-card"
import { Search } from "lucide-react"
import { Jobs } from "@/app/components/careers/config"
import Header from "@/app/components/careers/header-demo"
import type { CustomizationSettings } from "@/app/types/customization"
import { cn } from "@/lib/utils"

interface CareerPagePreviewProps {
  settings: CustomizationSettings
  domain: string
}
export function CareerPagePreview({
  settings,
  domain,
}: CareerPagePreviewProps) {
  return (
    <div
      className={cn("overflow-hidden w-full rounded-lg", settings.darkMode ? "dark" : "border")}
      style={{ fontFamily: settings.fontStyle }}
    >
      <Header settings={settings} careerPage={false}/>
      
      {settings.showCover && (
        <div
          className="relative h-48 text-white flex items-center justify-center bg-cover bg-center"
          style={{ backgroundImage: `url('${settings.coverImage}')` }}
        >
          <div className="text-center space-y-4 w-full max-w-[447px] px-4">
            <h1 className="text-xl sm:text-2xl font-bold">{settings.heading}</h1>
            <p className="text-[10px] sm:text-xs">{settings.description}</p>
            <div className="relative w-full max-w-xs mx-auto">
              <input
                type="search"
                placeholder="Search jobs..."
                className="px-4 py-2 rounded-lg text-black focus:outline-none w-full max-w-[288px] bg-white"
                disabled
              />
              <Search className="absolute right-4 sm:right-8 top-1/2 transform -translate-y-1/2 text-gray-500 h-4 w-4 sm:h-5 sm:w-5" />
            </div>
          </div>
        </div>
      )}

      <div className={settings.darkMode ? "bg-career_bg_color_dark_mode text-white" : ""}>
        <div className="py-6 grid grid-cols-1 sm:grid-cols-1 xl:grid-cols-2 gap-4 px-4 sm:px-8 lg:px-16">
          {Jobs.map((job, index) => (
            <JobCard
              key={index}
              {...job}
              preview={true}
              domain={domain}
              darkMode={settings.darkMode}
              primaryColor={settings.primaryColor}
            />
          ))}
        </div>
      </div>
    </div>
  )
}
