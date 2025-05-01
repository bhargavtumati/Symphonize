"use client";
import React, { useEffect, useState } from "react";
import CandidateCard from "../../../../components/candidate";
import FileUpload from "@/app/components/fileUpload";
import {
  PreferenceApiCandidateRespo,
  JobCardProps,
  Candidates,
} from "../../../../types/model";
import Image from "next/image";
import { auth } from "@/app/components/firebaseConfig";
import { apiService } from "@/app/api/service";
import {
  Search,
  Mail,
  Send,
  SlidersHorizontal,
  X,
  ArrowLeft,
  Loader2,
} from "lucide-react";
import { Card } from "@/components/ui/card";

import { useRouter } from "next/navigation";

import AlertDialogWrapper from "@/app/components/alertPopup";

import getApplicantPreferredData from "@/app/utils/applicants-filter-format";
import RibbonStages from "@/app/components/stages-ribbon";
import CustomizeStagesPopup from "@/app/components/CustomizeStagesPopup";
import PaginationComponent from "@/app/components/Pagination";
import { useToast } from "../../../../../components/hooks/use-toast";
import { UUID } from "crypto";
import { Input } from "@/components/ui/input";
import { CustomSelect } from "@/components/filters/custom-select";
import { dateWithoutTimeZone } from "@/lib/utils";
import { format } from "date-fns";
import SentEmail from "@/app/components/sent-email";
import SkeletonComponent from "@/app/components/skeleton/card-skeleton";
import { SkeletonType } from "@/app/utils/constants";

export default function AllApplicants() {
  const { toast } = useToast();
  const [applicants, setApplicants] = useState<
    PreferenceApiCandidateRespo[] | null
  >(null);
  const [applicantsData, setApplicantsData] = useState<Candidates[]>([]);
  const [jobDetails, setJobDetails] = useState<JobCardProps | null>(null);
  const [currentPage, setCurrentPage] = useState<number>(1);
  const [totalPages, setTotalPages] = useState<number>(1);
  const [totalApplicants, setTotalApplicantsCount] = useState<number>(0);
  const [loading, setLoading] = useState<boolean>(true);
  const initialCandidates: PreferenceApiCandidateRespo[] | null = applicants;
  const [candidates] = useState(initialCandidates);
  const [applicantsPreferences, setApplicantsPreferences] = useState<
    string | null
  >(null);
  const [stages, setStages] = useState<{ uuid: string; name: string }[]>([]);

  const [selectedTab, setSelectedTab] = useState("All Applicants");
  const [selectAll, setSelectAll] = useState<boolean>(false);
  const [jobId, setJobId] = useState<String>("");
  const [jobCode, setJobCode] = useState<String>("");
  const [isInputVisible, setIsInputVisible] = useState(false);
  const [searchApplicantValue, setSearchApplicantValue] = useState("");
  const [isPopupOpen, setIsPopupOpen] = useState(false);
  const [selectedCandidates, setSelectedCandidates] = useState<string[]>([]);
  const [selectedCandidatesDetails, setSelectedCandidatesDetails] = useState<PreferenceApiCandidateRespo[]>([]);
  const [onVerifyingEmailService, setVerifyingEmailService] = useState(false)
  const [originalStages, setOriginalStages] = useState<
    { uuid: string; name: string }[]
  >([]);

  const [stageCounts, setStageCounts] = useState<Record<string, number>>({});
  const [disableButton, setDisableButton] = useState<boolean>(true)
  const shareOptions = [
    { value: "job-id", label: "Job ID" },
    { value: "PART_TIME", label: "Job Title" },
    { value: "FREELANCE", label: "Client" },
    { value: "CONTRACT", label: "Location" },
  ];
  const [emailServiceStatus, setEmailServiceStatus] = useState(null)
  const [indidualEmailServiceStatus, setIndidualEmailServiceStatus] = useState(null)
  useEffect(() => {
    const preferenceData = sessionStorage.getItem("preferenceData");
    if (preferenceData) {
      const parsedData = JSON.parse(preferenceData);
      setApplicantsPreferences(parsedData);
    }
  }, []);

  const [modalState, setModalState] = useState<{
    type: "delete" | null;
    id?: string | undefined;
  }>({ type: null });

  const togglePopup = () => {
    setIsPopupOpen(!isPopupOpen);
  };

  const router = useRouter();

  useEffect(() => {
    const preferenceData = sessionStorage.getItem("preferenceData");
    if (preferenceData) {
      const parsedData = JSON.parse(preferenceData);
      setApplicantsPreferences(parsedData);
    } else {
    }
  }, []);

  useEffect(() => {
    const searchParams = new URLSearchParams(window.location.search);
    const jobIdFromParams = searchParams.get("jobId");
    if (jobIdFromParams) {
      setJobId(jobIdFromParams);
    }
  }, []);

  const openDiscardPopup = () => {
    setModalState({ type: "delete" });
  };

  const handleRowClick = () => {
    router.push(`/dashboard/view-job-page?jobId=${jobId}&jobCode=${jobCode}`);
  };

  useEffect(() => {

    const unsubscribe = auth.onAuthStateChanged(async (user) => {
      if (user) {
        await Promise.all([getStages(), getAllApplicants()]);
      }
    });

    return () => unsubscribe();
  }, [currentPage, jobId, searchApplicantValue]);

  const getAllApplicants = () => {
    setLoading(true);
    const unsubscribe = auth.onAuthStateChanged(async (user) => {
      if (user) {
        try {
          const jobData = await apiService(`/jobs/${jobId}`, "GET", null); // Use jobId for API call
          if (!jobData) throw new Error("Failed to fetch job details");
          setJobDetails(jobData);
          setJobCode(jobData.job.code);
          const applicantsPreferedData = getApplicantPreferredData(
            applicantsPreferences,
            jobData
          );
          const encodedJobCode = encodeURIComponent(jobData.job.code);
          const sortedApplicants = await apiService(
            `/applicants/filter?job_code=${encodedJobCode}&page=${currentPage}&name=${searchApplicantValue}`,
            "POST",
            applicantsPreferedData
          );
          if (sortedApplicants) {
            setLoading(false);
          }
          setTotalPages(sortedApplicants?.pagination?.total_pages);
          setTotalApplicantsCount(sortedApplicants?.pagination?.total_count)
          setApplicants(sortedApplicants?.solr_response?.response?.docs);
          setApplicantsData(sortedApplicants?.solr_response?.response?.docs);
        } catch (error: any) {
          toast({
            variant: "destructive",
            title: "Error fetching applicants",
            description: error.message || "An unexpected error occurred",
          });
        } finally {
          setLoading(false);
        }
      } else {
        setLoading(false);
      }
    });

    return () => unsubscribe();
  };

  const handleSelectAll = () => {
    setSelectAll(!selectAll);
    if (!selectAll && applicants) {
      setSelectedCandidates(
        applicants.map((candidate) => candidate.applicant_uuid)
      );
      setSelectedCandidatesDetails(
        applicants.map((candidate) => candidate)
      );
    } else {
      setSelectedCandidates([]);
      setSelectedCandidatesDetails([]);
    }
  };


  const toggleCandidateSelection = (candidateId: UUID, candidateDetails: any) => {
    setSelectedCandidates((prev) =>
      prev.includes(candidateId)
        ? prev.filter((id) => id !== candidateId)
        : [...prev, candidateId]
    );
    setSelectedCandidatesDetails(
      (prev) =>
        prev.includes(candidateDetails)
          ? prev.filter((candidate) => candidate !== candidateDetails)
          : [...prev, candidateDetails]
    );
  };

  const handleMoveSelected = async (stageId: any) => {
    setLoading(true)
    const flattenedCandidates = Array.from(new Set(selectedCandidates.flat()));
    const payload = {
      applicant_uuids: flattenedCandidates,
      stage_uuid: stageId,
    };

    try {
      const result = await apiService(
        `/applicants?job_id=${jobId}`,
        "PATCH",
        payload
      );
      if (!result) return new Error("Failed to fetch job details");
      setSelectedCandidates([]);
      setSelectAll(false);
      getStages();
      getAllApplicants();
    } catch (error: any) {
      toast({
        variant: "destructive",
        title: "Error on Moving applicants",
        description: error.message || "An unexpected error occurred",
      });
    } finally {
      setLoading(false)
    }

  };

  const getStages = () => {
    //if (!jobId) return; // Wait until jobId is available
    const unsubscribe = auth.onAuthStateChanged(async (user) => {
      setLoading(true);
      if (user) {
        try {
          const idToken = await user.getIdToken();
          if (idToken) {
            const response = await apiService(
              `/stages?job_id=${jobId}`,
              "GET",
              null
            ); // Use jobId for API call
            if (!response) throw new Error("Failed to fetch job details");
            setStages(response.stages);
            setOriginalStages(JSON.parse(JSON.stringify(response.stages)));
          }
        } catch (error: any) {
          toast({
            variant: "destructive",
            title: "Error fetching applicants",
            description: error.message || "An unexpected error occurred",
          });
        } finally {
          setLoading(false);
        }
      } else {
        setLoading(false);
      }
    });

    return () => unsubscribe();
  };

  useEffect(() => {
    if (applicantsData.length > 0 && stages?.length > 0) {
      const counts = stages.reduce((acc, stage) => {
        acc[stage.uuid] = applicantsData.filter((applicant: any) =>
          applicant.stage_uuid.includes(stage.uuid)
        ).length;
        return acc;
      }, {} as Record<string, number>);
      setStageCounts(counts);
    }
  }, [applicantsData, stages]);



  const navToFiltering = () => {
    router.push(
      `/dashboard/view-job-page/all-applicants/filtering?jobId=${jobId}&job_code=${jobCode}`
    );
  };
  const closeModal = () => {
    setModalState({ type: null });
  };

  const handleDiscardSingleEdit = () => {
    setStages(JSON.parse(JSON.stringify(originalStages)));
    setIsPopupOpen(false);
  };
  useEffect(() => {
    if (originalStages.length === stages.length &&
      originalStages.every((originalStage, index) => originalStage.name === stages[index].name)) {
      setDisableButton(true);
    }
  }, [stages, originalStages]);
  const handleSaveChanges = () => {
    const unsubscribe = auth.onAuthStateChanged(async (user) => {
      setLoading(true);
      if (user) {
        try {
          const idToken = await user.getIdToken();
          if (idToken) {
            const response = await apiService(
              `/stages?job_id=${jobId}`,
              "PATCH",
              { stages: stages }
            ); // Use jobId for API call
            if (!response) throw new Error("Failed to fetch job details");
            setOriginalStages(JSON.parse(JSON.stringify(stages)));
          }
        } catch (error: any) {
          toast({
            variant: "destructive",
            title: "Error fetching applicants",
            description: error.message || "An unexpected error occurred",
          });
          setIsPopupOpen(false);
        } finally {
          setLoading(false);
          setIsPopupOpen(false);
        }
      } else {
        setLoading(false);
      }
    });

    return () => unsubscribe();
  };

  const getDataBasedOnStage = (stage_uuid: string, stageName: string) => {
    const unsubscribe = auth.onAuthStateChanged(async (user) => {
      if (user) {
        try {
          const idToken = await user.getIdToken();
          if (idToken) {
            const applicantsPreferedData = getApplicantPreferredData(applicantsPreferences, jobDetails);
            let response;
            if (stage_uuid) {
              response = await apiService(
                `/applicants/filter?job_code=${jobCode}&page=${currentPage}&stage_uuid=${stage_uuid}`,
                "POST",
                applicantsPreferedData
              );
            } else {
              response = await apiService(
                `/applicants/filter?job_code=${jobCode}&page=${currentPage}`,
                "POST",
                applicantsPreferedData
              );
            }

            if (!response) throw new Error("Failed to fetch job details");

            getStages();
            setSelectedTab(stageName);
            setTotalPages(response?.pagination?.total_pages);
            setApplicants(response?.solr_response?.response?.docs);
          }
        } catch (error: any) {
          toast({
            variant: "destructive",
            title: "Error fetching applicants",
            description: error.message || "An unexpected error occurred",
          });
        } finally {
          setLoading(false);
        }
      } else {
        setLoading(false);
      }
    });

    return () => unsubscribe();
  };

  const moveOptions =
    originalStages?.map((stage) => ({
      value: stage.uuid,
      label: stage.name,
    })) || [];

  const handlePageChange = (page: number) => {
    setCurrentPage(page);
  };

  const toggleInput = () => {
    setSearchApplicantValue("");
    setIsInputVisible(!isInputVisible);
  };
  const handleSearchInputChange = (
    event: React.ChangeEvent<HTMLInputElement>
  ) => {
    setSearchApplicantValue(event.target.value);
  };

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
  const resetSelectedCandidates = (candidateIds: string[], candidateDetails: PreferenceApiCandidateRespo[]) => {
    setSelectedCandidates(candidateIds);
    setSelectedCandidatesDetails(candidateDetails);
    setSelectAll(false);
  };

  return (
    <div className="bg-slate-50 min-h-screen w-full py-4">
      <div className="flex justify-between">
        <div>
          <header
            className="flex items-center text-[#000000] text-[20px] font-semibold space-x-2	">
            <ArrowLeft className="w-[24px] h-[24px] text-[#000000] cursor-pointer" onClick={() => handleRowClick()} />{""}
            {loading ? (
              <SkeletonComponent type={SkeletonType.Flat} className="h-5 w-52" />
            ) : (
              <span>{jobDetails?.job?.title}</span>
            )}
          </header>
          <div className="text-[#475569] text-[14px] mb-4">
            {loading ? (
              <SkeletonComponent type={SkeletonType.Flat} className="w-56 h-5 mt-2" />
            ) : (
              <>
                {jobDetails?.company.name} • Target date:{" "}
                {jobDetails?.job.target_date
                  ? format(dateWithoutTimeZone(jobDetails?.job.target_date), "dd MMM yyyy")
                  : "Invalid Date"}
              </>
            )}
          </div>
        </div>
        <div>
          <div className="flex justify-between space-x-2 w-full">
            {isInputVisible ? (
              <div className="flex items-center animate-slide-in-left relative space-x-2">
                <input
                  type="text"
                  placeholder="Search by applicant name"
                  onChange={handleSearchInputChange}
                  className="min-w-[200px] min-h-[38px] p-2 rounded-full border border-gray-300 focus:outline-none mr-2"
                />
                <button onClick={toggleInput} className="absolute right-2">
                  <X className="w-4 h-4 text-gray-500 hover:text-black mr-[5px]" />
                </button>
              </div>
            ) : (
              <Card
                className="min-w-[39px] min-h-[38px] flex items-center justify-center cursor-pointer"
                onClick={toggleInput}
              >
                <Search className="w-4 h-4" />
              </Card>
            )}

            <FileUpload disabled={jobDetails?.job.status === "CLOSED"} isLoading={loading} />
          </div>
        </div>
      </div>
      <div className="flex justify-between mb-4">
        <div className="flex space-x-2">
          <SentEmail
            className="min-w-[112px] h-[38px] flex items-center justify-around border border-gray-300 bg-white text-black text-[12px] font-medium rounded-lg shadow-sm"
            icon={<Mail />}
            iconClassName="w-4 h-4 flex items-center justify-around"
            text="Send Email"
            selectedCandidates={selectedCandidates}
            onScheduleClick={verifyEmailService}
            onVerifyEmailService={onVerifyingEmailService}
            selectedCandidatesDetails={selectedCandidatesDetails}
            jobDetails={jobDetails}
            originalStages={originalStages}
            toggleCandidateSelection={resetSelectedCandidates}
          />
          <div className="flex items-center space-x-2">
            {/* Share Applicants Dropdown */}
            <div className="flex items-center justify-around bg-white text-black font-medium rounded-lg shadow-sm ">
              <CustomSelect
                options={shareOptions}
                placeholder="Share Applicants"
                contentClassName="w-auto"
                icon={Send}
                value=""
                disabled={jobDetails?.job.status === "CLOSED" || loading}
              />
            </div>
            <CustomSelect
              options={moveOptions}
              placeholder="Move To"
              onValueChange={handleMoveSelected}
              triggerClassName="h-10 pl-[10px] w-[220px]"
              value=""
              disabled={jobDetails?.job.status == "CLOSED" || loading}
            />
          </div>
        </div>
        <div className="flex space-x-2">
          <button className="min-w-[87px] min-h-[31px] flex items-center justify-around border border-gray-300 bg-white text-black text-[12px] font-medium rounded-lg shadow-sm p-2">
            <SlidersHorizontal className="w-4 h-4" />
            <span>Sort by</span>
          </button>
          <button
            className="min-w-[93px] min-h-[38px] flex items-center justify-around border border-gray-300 bg-white text-black text-[12px] font-medium rounded-lg shadow-sm p-2 gap-2"
            onClick={navToFiltering}
          >
            <SlidersHorizontal className="w-4 h-4" />
            <span>Preferences</span>
          </button>
        </div>
      </div>
      {loading ?
        (<SkeletonComponent type={SkeletonType.Ribbon} rows={1} columns={8} />)
        : (
          <>
            <div className="flex h-12 items-center justify-between rounded-md border border-[#E2E8F0] bg-white px-4">
              <div className="flex items-center gap-4 overflow-hidden">
                <Input
                  type="checkbox"
                  checked={selectAll}
                  onChange={handleSelectAll}
                  className=" h-3 w-3 rounded border-gray-300"
                />
                <RibbonStages
                  applicants={totalApplicants}
                  stages={originalStages}
                  jobDetails={jobDetails}
                  selectedTab={selectedTab}
                  stageCounts={stageCounts}
                  onStageClick={getDataBasedOnStage}
                />
              </div>

              <Image
                src="/images/filter.png"
                width={20}
                height={20}
                alt="Filter"
                className={`ml-2
                  ${jobDetails?.job.status === "CLOSED" ? " opacity-40 cursor-not-allowed" : "cursor-pointer"}`}
                onClick={() => {
                  if (jobDetails?.job.status !== "CLOSED") {
                    togglePopup();
                  }
                }}
              />
            </div>
          </>
        )}

      {isPopupOpen && (
        <CustomizeStagesPopup
          stages={stages}
          onStagesUpdate={setStages}
          onSaveChanges={handleSaveChanges}
          onDiscardChanges={() => openDiscardPopup()}
          setDisableButton={setDisableButton}
          disableButton={disableButton}
        />
      )}

      {/* Candidate Cards */}
      <div className="py-4">
        {applicants?.length !== 0 ? (
          <div className="space-y-4">
            {loading ? (
              [...Array(5)].map((_, index) => (
                <SkeletonComponent key={index} type={SkeletonType.ApplicantCard} />
              ))
            ) : (
              applicants?.map((candidate: any) => (
                <CandidateCard
                  key={candidate.applicant_uuid}
                  candidate={candidate}
                  isSelected={selectedCandidates.includes(candidate.applicant_uuid)}
                  toggleSelection={() =>
                    toggleCandidateSelection(candidate.applicant_uuid, candidate)
                  }
                  disable={jobDetails?.job.status === "CLOSED"}
                  stages={stages}
                  originalStages={originalStages}
                />
              ))
            )}
          </div>
        ) : (
          <div className="flex justify-center p-4">
            <h1>No applicants</h1>
          </div>
        )}
      </div>
      <AlertDialogWrapper
        isOpen={modalState.type === "delete"}
        onClose={closeModal}
        title="Are you sure you want to discard the changes?"
        description="By discarding, you’ll lose the changes"
        confirmText="Yes"
        cancelText="No"
        onConfirm={() => handleDiscardSingleEdit()}
      />
      <PaginationComponent
        currentPage={currentPage}
        totalPages={totalPages}
        onPageChange={handlePageChange}
      />
    </div>
  );
}
