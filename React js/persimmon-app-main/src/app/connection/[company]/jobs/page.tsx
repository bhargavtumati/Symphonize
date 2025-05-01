"use client";
import type React from "react";
import { useState, useRef, useEffect, useCallback } from "react";
import {
  BookOpenText,
  MapPin,
  Briefcase,
  Building,
  Loader2,
  ArrowLeft,
  IndianRupee,
} from "lucide-react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import JobApplicationForm from "@/app/components/careers/job-application-form";
import { apiService } from "@/app/api/service";
import type { JobDetails, Job } from "@/app/connection/[company]/model";
import { useParams, useRouter } from "next/navigation";
import { titleFormat } from "@/app/utils/validations";
import InfoItem from "@/app/components/careers/info-items";
import ListOfJobsRetrieved from "@/app/components/careers/list-of-jobs";
import type { CustomizationSettings } from "@/app/types/customization";
import Image from "next/image";
import Header from "@/app/components/careers/header-demo";

const ListOfJobs: React.FC = () => {
  const formRef = useRef<HTMLDivElement>(null);
  const params = useParams();
  const router = useRouter();
  const domain = params.company;
  const [settings, setSettings] = useState<CustomizationSettings | null>(null);
  const [selectedJob, setSelectedJob] = useState<{
    job: Job | null;
    index: number | null;
  }>({
    job: null,
    index: null,
  });
  const [jobDetails, setJobDetails] = useState<JobDetails>({ jobs: [] });
  const [loading, setLoading] = useState(true);
  const [jobCode, setJobCode] = useState("");

  const fetchAllJobDetails = async () => {
    const trimmedDomain = domain.toString().trim();
    try {
      const allJobDetails = await apiService(
        `/jobs/domain/${trimmedDomain}`,
        "GET",
        null
      );
      if (allJobDetails) {
        setJobDetails(allJobDetails);
        if (!jobCode) {
          setSelectedJob({
            job: allJobDetails.jobs[0],
            index: 0,
          });
        }
      }
    } catch (error) {
      console.error("Error fetching all job details: ", error);
    }
  };

  const fetchSelectedJobDetails = async () => {
    try {
      const selectedJob = await apiService(
        `/jobs/code/${jobCode}`,
        "GET",
        null
      );
      setSelectedJob({
        job: selectedJob.job,
        index: -1,
      });
    } catch (error) {
      console.error("Error fetching selected job details: ", error);
    } finally {
      setLoading(false);
    }
  };
  
 const handleClick = useCallback(
    (e: React.MouseEvent<HTMLAnchorElement>) => {
      e.preventDefault()

      // Force navigation in the current window
      if (settings) {
        // Using window.location.replace to ensure it replaces the current history entry
        window.location.replace(settings.iconLink)
      }
    },
    [settings],
  )

  const fetchCompanyStyles = async () => {
    const trimmedDomain = domain.toString().trim();
    try {
      const stylesByCompany = await apiService(
        `/careerpage/extract-settings/domain/${trimmedDomain}`,
        "GET",
        null
      );
      if (stylesByCompany && stylesByCompany.data) {
        setSettings({
          heading: stylesByCompany.data.heading || "Join Us",
          fontStyle: stylesByCompany.data.font_style || "sans-serif",
          coverImage: `data:image/jpeg;base64,${stylesByCompany.data.image_data}`,
          description: stylesByCompany.data.description || "",
          primaryColor: stylesByCompany.data.color_selected || "#655555",
          allPrimaryColors: stylesByCompany.data.primary_colors || [],
          darkMode: stylesByCompany.data.enable_dark_mode || false,
          showCover: stylesByCompany.data.enable_cover_photo || true,
          icon: stylesByCompany.data.logo_data || null,
          iconLink: stylesByCompany.data.website_url || "",
          headerColor: stylesByCompany.data.selected_header_color || "#655555",
          headerColors: stylesByCompany.data.header_colors || [],
          careerPageUrl:stylesByCompany.data.career_page_url || null,
        });
      }
    } catch (error) {
      console.error("Error fetching company styles: ", error);
    }
  };

  useEffect(() => {
    const fetchAllData = async () => {
      setLoading(true);
      try {
        await fetchAllJobDetails();
        if (jobCode) {
          await fetchSelectedJobDetails();
        }
        await fetchCompanyStyles();
      } catch (error) {
        console.error("Error fetching data: ", error);
      } finally {
        setLoading(false);
      }
    };

    fetchAllData();
  }, [domain, jobCode]);

  useEffect(() => {
    const searchParams = new URLSearchParams(window.location.search);
    const jobCodeFromParams = searchParams.get("jobCode");
    if (jobCodeFromParams) {
      setJobCode(jobCodeFromParams);
    }
  }, []);

  const scrollToForm = () => {
    formRef.current?.scrollIntoView({ behavior: "smooth", block: "start" });
  };

  const navToJobs = () => {
    router.push(`/connection/${domain}`);
  };

  const handleJobClick = (job: Job, index: number) => {
    setSelectedJob({ job, index });
  };

  return loading ? (
    <div className="flex items-center justify-center min-h-screen">
      <Loader2 className="h-[30px] w-12 animate-spin" />
    </div>
  ) : (
    <div
      className={`${
        settings?.darkMode ? " dark bg-career_bg_color_dark_mode" : "bg-white"
      }`}
      style={{ fontFamily: settings?.fontStyle }}
    >
      <Header settings={settings} careerPage={true}/>
      <div
        className={`p-6 pt-20 ${settings?.darkMode ? "bg-slate-800" : "bg-white"}`}
      >
        <div className="flex justify-between items-start mb-4 pt-8">
          <div className={`${settings?.darkMode ? "text-slate-50" : ""}`}>
            <div className="text-sm mb-2">
              <ArrowLeft className="inline-block mr-2 cursor-pointer" onClick={navToJobs} />
              Job Id: {selectedJob?.job?.code}{" "}
            </div>
            <h1 className="text-2xl font-semibold mb-6">{selectedJob?.job?.title}</h1>
            <div className="grid lg:grid-cols-5 md:grid-cols-3 md:auto-rows-auto gap-6 md:gap-16">
              <InfoItem
                icon={<IndianRupee />}
                heading="Salary"
                message={`${selectedJob?.job?.min_salary} LPA - ${selectedJob?.job?.max_salary} LPA`}
                settings={settings}
              />
              <InfoItem
                icon={<BookOpenText />}
                heading="Experience"
                message={`${selectedJob?.job?.min_experience} - ${selectedJob?.job?.max_experience} Years`}
                settings={settings}
              />
              <InfoItem
                icon={<MapPin />}
                heading="Location"
                message={selectedJob?.job?.location}
                settings={settings}
              />
              <InfoItem
                icon={<Briefcase />}
                heading="Job Type"
                message={titleFormat(selectedJob?.job?.type)}
                settings={settings}
              />
              <InfoItem
                icon={<Building />}
                heading="Work Place Type"
                message={titleFormat(selectedJob?.job?.workplace_type)}
                settings={settings}
              />
            </div>
          </div>
          <Button
            backgroundColor={settings?.primaryColor}
            onClick={scrollToForm}
          >
            Apply Now
          </Button>
        </div>
      </div>

      <div className="p-6 px-12">
        <div className="grid md:grid-cols-[1fr,300px] gap-6">
          <div className="space-y-6 sticky-column">
            <Card
              className={`${
                settings?.darkMode
                  ? "bg-slate-800 text-slate-200"
                  : "bg-[#f8fafc]"
              } border-none p-4`}
              style={{ fontFamily: settings?.fontStyle }}
            >
              <h2>Job Description</h2>
              <div
                className="text-sm pt-2"
                dangerouslySetInnerHTML={{
                  __html: selectedJob?.job?.description || "",
                }}
              ></div>
            </Card>
            <JobApplicationForm formRef={formRef} settings={settings} selectedJob={selectedJob}/>
          </div>

          <div>
            <ListOfJobsRetrieved
              jobs={jobDetails.jobs}
              selectedJobIndex={selectedJob}
              handleJobClick={handleJobClick}
              settings={settings}
            />
          </div>
        </div>
      </div>
    </div>
  );
};

export default ListOfJobs;
