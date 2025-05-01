"use client"

import type React from "react"
import { useEffect, useState } from "react"
import { Search, Loader2 } from "lucide-react"
import { JobCard } from "@/app/components/careers/job-card"
import { apiService } from "@/app/api/service"
import type { JobDetails } from "@/app/connection/[company]/model"
import { useParams } from "next/navigation"
import type { CustomizationSettings } from "@/app/types/customization"
import Header from "@/app/components/careers/header-demo"

const CareerPage: React.FC = () => {
  const params = useParams()
  const domain = params.company as string
  const [settings, setSettings] = useState<CustomizationSettings | null>(null)
  const [jobDetails, setJobDetails] = useState<JobDetails>({ jobs: [] })
  const [searchQuery, setSearchQuery] = useState<string>("")
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (domain) {
      try {
        ;(async () => {
          const allJobDetails = await apiService(`/jobs/domain/${domain}`, "GET", null)
          if (allJobDetails) {
            setJobDetails(allJobDetails)
            setLoading(false)
          }
        })()
      } catch (error) {
        console.error("Error fetching jobs:", error)
      } finally {
        setLoading(false)
      }
    }
  }, [domain])

  useEffect(() => {
    if (domain) {
      try {
        ;(async () => {
          const stylesByCompany = await apiService(`/careerpage/extract-settings/domain/${domain}`, "GET", null)
          console.log("styles", stylesByCompany)
          if (stylesByCompany && stylesByCompany.data) {
            setSettings({
              heading: stylesByCompany.data.heading || "Join Us",
              fontStyle: stylesByCompany.data.font_style || "sans-serif",
              coverImage: `data:image/jpeg;base64,${stylesByCompany.data.image_data}`,
              description: stylesByCompany.data.description || "",
              primaryColor: stylesByCompany.data.color_selected || "#655555",
              allPrimaryColors: stylesByCompany.data.primary_colors || [],
              darkMode: stylesByCompany.data.enable_dark_mode || false,
              showCover: stylesByCompany.data.enable_cover_photo,
              icon: stylesByCompany.data.logo_data || null,
              iconLink: stylesByCompany.data.website_url || "",
              headerColor: stylesByCompany.data.selected_header_color || "#655555",
              headerColors: stylesByCompany.data.header_colors || [],
              careerPageUrl: stylesByCompany.data.career_page_url || null,
            })
          }
        })()
      } catch (error) {
        console.error("Error fetching styles:", error)
      } finally {
        setLoading(false)
      }
    }
  }, [domain])

  const filteredJobs = jobDetails.jobs.filter(
    (job) =>
      job.title.toLowerCase().startsWith(searchQuery.toLowerCase()) ||
      job.location.toLowerCase().startsWith(searchQuery.toLowerCase()),
  )

  if (!settings || loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Loader2 className="h-[30px] w-12 animate-spin" />
      </div>
    )
  }

  return (
    <div
      className={`min-h-screen ${
        settings.darkMode ? "dark bg-career_bg_color_dark_mode text-white" : "bg-white text-black"
      }`}
      style={{ fontFamily: settings.fontStyle }}
    >
      <Header settings={settings} careerPage={true} />
      <div className="pt-20">
        {settings.showCover && (
          <div
            className="relative h-48 md:h-56 lg:h-64 text-white flex items-center justify-center bg-cover bg-center"
            style={{
              backgroundImage: `url('${settings.coverImage}')`,
            }}
          >
            <div className="text-center space-y-4 w-full max-w-md px-4">
              <h1 className="text-xl md:text-2xl lg:text-3xl font-bold">{settings.heading}</h1>
              <p className="text-[10px] md:text-xs lg:text-sm">{settings.description}</p>
              <div className="relative w-full flex justify-center">
                <div className="relative w-full max-w-xs md:max-w-sm">
                  <input
                    type="text"
                    placeholder="Search jobs by title or location..."
                    className={`px-4 py-2 rounded-lg focus:outline-none w-full ${
                      settings.darkMode ? "bg-gray-700 text-white" : "bg-white text-black"
                    }`}
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                  />
                  <Search
                    className={`absolute right-3 top-1/2 transform -translate-y-1/2 ${
                      settings.darkMode ? "text-gray-300" : "text-gray-500"
                    } h-5 w-5`}
                  />
                </div>
              </div>
            </div>
          </div>
        )}
        <div className="overflow-y-auto">
          {filteredJobs.length > 0 ? (
            <div className="py-8 md:py-10 lg:py-12 grid grid-cols-1 md:grid-cols-1 lg:grid-cols-2 gap-4 md:gap-6 lg:gap-8 px-4 sm:px-6 md:px-8 lg:px-12 xl:px-16">
              {filteredJobs.map((job, index) => (
                <JobCard
                  key={index}
                  {...job}
                  preview={false}
                  domain={domain}
                  darkMode={settings?.darkMode}
                  primaryColor={settings.primaryColor}
                />
              ))}
            </div>
          ) : (
            <div
              className={`col-span-1 flex items-center justify-center py-12 ${
                settings.darkMode ? "bg-career_bg_color_dark_mode" : "bg-gray-100"
              }`}
            >
              <div
                className={`card ${settings.darkMode ? "bg-gray-700" : "bg-white"} shadow-md rounded-lg p-6 max-w-xl mx-4`}
              >
                <h2
                  className={`text-xl md:text-2xl font-bold text-center mb-4 ${settings.darkMode ? "text-white" : "text-black"}`}
                >
                  Exciting Opportunities Ahead!
                </h2>
                <p className={settings.darkMode ? "text-gray-300" : "text-gray-600"}>
                  We don&apos;t have any active job openings right now, but we&apos;re always planning for the future.
                  Stay connected with us and be the first to know about upcoming roles.
                </p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default CareerPage

