"use client";
import React, { useEffect, useState } from "react";
import { apiService } from "../../../api/service";
import { auth } from "@/app/components/firebaseConfig";
import { JobCardProps, } from "@/app/types";
import SkeletonComponent from "@/app/components/skeleton/card-skeleton";
import { SkeletonType } from "@/app/utils/constants";
import { ShareJobCard } from "@/app/components/view-job/ShareJobCard";
import { JobCard } from "@/app/components/view-job/JobCard";
import { PageHeader } from "@/app/components/view-job/PageHeader";
import { JobDescription } from "@/app/components/view-job/Job-description-card";
import { AiClarifyingQuestions } from "@/app/components/view-job/ai-clarifying-questions";
import { CompanyDetails } from "@/app/components/view-job/company-details";
import { PublishedOnCard } from "@/app/components/view-job/published-on-card";
import { JobPerformanceCard } from "@/app/components/view-job/job-performance-card";

const ViewJobPage = () => {
  const [jobId, setJobId] = useState<string>();
  const [jobData, setJobData] = useState<JobCardProps | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const jobInformation = {
    jobTitle: jobData?.job.title || "",
    organizationName: jobData?.company.name || "",
    jobType: jobData?.job.type || "",
    jobLocation: jobData?.job.location || "",
    workExperience: `${jobData?.job.min_experience} - ${jobData?.job.max_experience} years` || "",
    jobCode: jobData?.job.code || "",
  };
  const [views, setViews] = useState({
    careerPageView: false,
    persimmonView: false,
    Indeed: false,
    linkedInView: false,
    monsterJobsView: false,
    hiristIconView: false,
    googleView: false,
  });

  const updateView = (label: string, value: boolean) => {
    setViews((prev) => ({
      ...prev,
      [label]: !value, // Use label directly as key
    }));
  };

  useEffect(() => {
    const searchParams = new URLSearchParams(window.location.search);
    const jobIdFromParams = searchParams.get("jobId");
    if (jobIdFromParams) {
      setJobId(jobIdFromParams);
    }
  }, []);

  useEffect(() => {
    if (!jobId) return; // Wait until jobId is available

    const unsubscribe = auth.onAuthStateChanged(async (user) => {
      if (user) {
        try {
          const idToken = await user.getIdToken();
          if (idToken) {
            const response = await apiService(`/jobs/${jobId}`, "GET", null); // Use jobId for API call
            //const JobPerformanceCard = await apiService(`/applicants?job_id=${jobId}&page=${1}`, 'GET', null);
            if (!response) throw new Error("Failed to fetch job details");
            setJobData(response);
            if (!JobPerformanceCard)
              throw new Error("Faild to fetch applicantd details");
            //setJobApplicants(JobPerformanceCard);
          }
        } catch (error: any) {
          setError(error.message);
        } finally {
          setLoading(false);
        }
      } else {
        setLoading(false);
      }
    });

    return () => unsubscribe();
  }, [jobId]); // Dependency on jobId
  return (
    <div className="w-full max-w-[1440px] mx-auto px-8 pt-1">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 h-full">
        <div className="col-span-1 md:col-span-3 h-4 pt-4 pb-10">
          { <PageHeader code={jobData?.job?.code} status={jobData?.job.status} isLoading={loading} />}
        </div>
        <div className="col-span-1 md:col-span-2 h-full pb-6 space-y-4">
          {loading ? (
            //  <SkeletonComponent type="Card" className="h-[276px]" />
            <SkeletonComponent type={SkeletonType.Card} rows={2} columns={3} />
          ) : (
            jobData?.job && (
              <JobCard
                  job={jobData?.job}
                  company={jobData?.company}
                  count={jobData?.count}/>
            )
          )}
          {loading ? (
            <SkeletonComponent type={SkeletonType.Description} rows={16} columns={1} />
          ) : (
            jobData?.job && (
              <JobDescription
                  job={jobData?.job}
                  company={jobData?.company}
                  count={jobData?.count}/>
            )
          )}
          {loading ? (
            <SkeletonComponent type={SkeletonType.Card} className="h-[196px]" rows={2} />
          ) : (
            jobData?.job && (
              <AiClarifyingQuestions
                  job={jobData?.job}
                  company={jobData?.company}
                  count={jobData?.count}/>
            )
          )}
          {loading ? (
            <SkeletonComponent type={SkeletonType.Card} className="h-[228px]" rows={2} />
          ) : (
            jobData?.company && (
              <CompanyDetails
                  job={jobData?.job}
                  company={jobData?.company}
                  count={jobData?.count}/>
            )
          )}
        </div>
        <div className="col-span-1  gap-y-0 mb-4">
          {loading ? (
            <SkeletonComponent type={SkeletonType.Card} className="h-[172px]" rows={1} columns={4} />
          ) : (
            jobData && (
              <JobPerformanceCard
                  job={jobData?.job}
                  company={jobData?.company}
                  count={jobData?.count}/>
            )
          )}
          {loading ? (
            <SkeletonComponent type={SkeletonType.ShareJob} className="h-[172px]" rows={1} columns={5} />
          ) : (
            <ShareJobCard
              jobTitle={jobInformation.jobTitle}
              organizationName={jobInformation.organizationName}
              jobType={jobInformation.jobType}
              jobLocation={jobInformation.jobLocation}
              workExperience={jobInformation.workExperience}
              jobCode={jobInformation.jobCode}
              disable={jobData?.job.status==="CLOSED"}
            />
          )}
          {loading ? (
            <SkeletonComponent type={SkeletonType.Publish} className="h-[568px]" rows={7} columns={1} />
          ) : (
            <PublishedOnCard views={views} setViews={updateView} />
          )}
        </div>
      </div>
    </div>
  );
};

export default ViewJobPage;
