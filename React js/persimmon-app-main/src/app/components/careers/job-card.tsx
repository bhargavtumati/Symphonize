"use client"
import { IndianRupee, Clock, MapPin, Calendar } from "lucide-react"
import type React from "react"

import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"

interface JobCardProps {
  title: string
  code: string
  min_salary: number
  max_salary: number
  min_experience: number
  max_experience: number
  location?: string
  primaryColor: string
  meta: audit
  preview: boolean
  darkMode?: boolean
  domain?: string | string[]
}
type audit = {
  audit: { created_at: number }
}

export const JobCard: React.FC<JobCardProps> = ({
  title,
  code,
  min_salary,
  max_salary,
  min_experience,
  max_experience,
  location,
  darkMode,
  primaryColor,
  meta,
  preview = false,
  domain,
}) => {
  const router = useRouter()

  const navToJobs = (job_code: string) => {
    router.push(`/connection/${domain}/jobs?jobCode=${encodeURIComponent(job_code)}`)
  }

  const formatToLocalDate = (timestamp: number) => {
    const date = new Date(timestamp * 1000)

    const options: Intl.DateTimeFormatOptions = {
      day: "2-digit",
      month: "short",
      year: "numeric",
    }

    return date.toLocaleDateString("en-GB", options)
  }

  return (
    <Button
    variant="none"
      className="flex justify-left bg-transparent p-0 m-0 text-left outline-none focus:outline-none w-full h-full"
      type="button"
      disabled={preview}
      onClick={() => navToJobs(code)}
    >
      <div
        className={`px-4 sm:px-6 md:px-8 py-5 sm:py-6 ${darkMode ? "bg-career_page_job_card" : "bg-white"} rounded-lg border shadow-sm w-full h-full flex flex-col`}
      >
        <h3 className="font-medium text-base sm:text-lg mb-3 sm:mb-4 line-clamp-2">{title}</h3>

        <div className="flex flex-col sm:flex-row justify-between gap-3 sm:gap-4 mb-3 sm:mb-4 flex-grow">
          <div className="flex flex-col">
            <span className="text-xs text-muted-foreground mb-1">Salary</span>
            <div className="flex items-center gap-1 text-xs sm:text-sm">
              <IndianRupee className="h-3 w-3 sm:h-4 sm:w-4 flex-shrink-0" />
              <span className="truncate">{`${min_salary} - ${max_salary}`}</span>
            </div>
          </div>

          <div className="flex flex-col">
            <span className="text-xs text-muted-foreground mb-1">Experience</span>
            <div className="flex items-center gap-1 text-xs sm:text-sm">
              <Clock className="h-3 w-3 sm:h-4 sm:w-4 flex-shrink-0" />
              <span>{`${min_experience} - ${max_experience}`}</span>
            </div>
          </div>

          <div className="flex flex-col">
            <span className="text-xs text-muted-foreground mb-1">Location</span>
            <div className="flex items-center gap-1 text-xs sm:text-sm">
              <MapPin className="h-3 w-3 sm:h-4 sm:w-4 flex-shrink-0" />
              <span className="truncate">{location}</span>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-1 text-xs text-muted-foreground mt-auto">
          <Calendar className="h-3 w-3 flex-shrink-0" />
          <span>Posted on {formatToLocalDate(meta?.audit?.created_at)}</span>
        </div>
      </div>
    </Button>
  )
}

