"use client";
import { applicantsPreferedData } from "@/app/types/model";
// Function to apply filters and make API call
export const applyFilters = async (jobId: string, router: any, jobCode: string) => {
    sessionStorage.setItem('preferenceData', JSON.stringify(applicantsPreferedData));
    router.push(`/dashboard/view-job-page/all-applicants?jobId=${jobId}&jobCode=${jobCode}`);
};