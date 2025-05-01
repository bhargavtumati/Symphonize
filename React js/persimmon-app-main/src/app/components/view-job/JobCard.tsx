import { apiService } from "@/app/api/service";
import { JobCardProps } from "@/app/types";
import { formatWorkplaceType } from "@/app/utils/helper";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { dateWithoutTimeZone } from "@/lib/utils";
import { format } from "date-fns";
import { startCase, toLower } from "lodash";
import { Briefcase, MapPin, MoreVertical, Users } from "lucide-react";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

export const JobCard: React.FC<JobCardProps> = ({ job }) => {
    const [showOptions, setShowOptions] = useState(false);
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [popupJobId, setPopupJobId] = useState<number | null>(job.id);
  
    const router = useRouter();
  
    const toggleOptions = () => {
      setShowOptions((prev) => !prev);
    };
    const handleScroll = () => {
      setShowOptions(false); // Close the popup on scroll
    };
    const handleClickOutside = (e: any) => {
      if (
        popupJobId &&
        !e.target.closest(".popup") &&
        !e.target.closest(".three-dots")
      ) {
        setShowOptions(false); // Close the popup if clicked outside
      }
    };
  
    useEffect(() => {
      const handleClick = (e: any) => handleClickOutside(e);
  
      document.body.addEventListener("click", handleClick);
  
      return () => {
        document.body.removeEventListener("click", handleClick);
      };
    }, [popupJobId]);
    const handleJobEvent = (job: any, actionType: string) => {
      setShowOptions((prev) => !prev);
      router.push(`create-job?action=${actionType}&jobId=${job.id}`);
    };
    const updateStatus = async () => {
      const payload = {
        status: "CLOSED",
      };
      const data = await apiService(`/jobs/${popupJobId}`, "PATCH", payload);
      if (!data) {
        throw new Error("there is a issues");
      }
      setIsModalOpen(false);
      setPopupJobId(null);
      window.location.reload();
    };
  
    const openModal = (job: any) => {
      setShowOptions((prev) => !prev);
      setIsModalOpen(true);
    };
    const closeModal = () => {
      setIsModalOpen(false);
    };
    const applicantsPage = (jobId: any, jobCode: string) => {
      router.push(
        `/dashboard/view-job-page/all-applicants?jobId=${jobId}&jobCode=${jobCode}`
      );
    };
    useEffect(() => {
      if (showOptions) {
        window.addEventListener("scroll", handleScroll);
      } else {
        window.removeEventListener("scroll", handleScroll);
      }
      return () => {
        window.removeEventListener("scroll", handleScroll);
      };
    }, [showOptions]);
  
    return (
      <Card className="w-full bg-white px-6 py-4  rounded-lg border-none">
        {/* Header */}
        <div className="flex justify-between items-start mb-4">
          <div>
            <h2 className="text-xl font-semibold">{job.title}</h2>
            <p className="text-xs text-gray-500">
              Target Date:{" "}
              {format(dateWithoutTimeZone(job.target_date), "dd MMM yyyy")}
            </p>
          </div>
  
          <div className="relative">
            <MoreVertical
              className="text-black-500 cursor-pointer"
              onClick={toggleOptions}
            />
  
            {showOptions && (
              <div className="absolute top-1/2 left-0 -translate-x-full -translate-y-1/2 bg-white border border-gray-300 shadow-lg rounded-lg w-32 z-50 mt-8 popup">
                <ul className="py-1">
                  {job.status==="CLOSED"?(
                    <li
                    className="px-2 py-2 text-gray-700 hover:bg-gray-100 cursor-pointer"
                    onClick={(e) => {
                      e.stopPropagation(); // Prevent row click
                      handleJobEvent(job, "Repost");
                    }}
                  >
                  Edit & Repost
                  </li>
                  
                  ):(
                    <>
                    <li
                    className="px-4 py-2 text-gray-700 hover:bg-gray-100 cursor-pointer"
                    onClick={(e) => {
                      e.stopPropagation(); // Prevent row click
                      handleJobEvent(job, "Edit");
                    }}
                  >
                    Edit
                  </li>
                  <li
                    className="px-4 py-2 text-gray-700 hover:bg-gray-100 cursor-pointer"
                    onClick={(e) => {
                      e.stopPropagation(); // Prevent row click
                      openModal(job.id);
                    }}
                  >
                    Close
                  </li>
                  </>
                )}
                 
                </ul>
              </div>
            )}
            {isModalOpen && (
              <div className="fixed inset-0 flex items-center justify-center z-50 bg-black bg-opacity-50 popup">
                <div className="bg-white rounded-lg p-8 min-w-[564px] min-h-[208px] shadow-lg">
                  <h2 className="text-xl font-semibold text-gray-800 mb-4">
                    Are You Sure You Want to Close the Job?
                  </h2>
                  <p className="text-gray-600 mb-6">
                    By closing the job, the job will be removed from the career
                    page and all job <br />
                    boards.
                  </p>
                  <div className="flex justify-end space-x-2">
                    <button
                      onClick={closeModal}
                      className="px-4 py-2 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200"
                    >
                      Cancel
                    </button>
                    <button
                      onClick={updateStatus}
                      className="px-4 py-2 text-white bg-red-600 rounded-lg hover:bg-red-700"
                    >
                      Close Job
                    </button>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
  
        {/* Content Grid */}
        <div className="grid grid-cols-3 gap-y-4 gap-x-6 text-gray-700">
          <div>
            <p className="text-xs font-medium text-gray-500">Salary</p>
            <p>
              ₹ {job.min_salary} LPA - {job.max_salary} LPA
            </p>
          </div>
          <div>
            <p className="text-xs font-medium text-gray-500">Experience</p>
            <p className="flex items-center">
              <Briefcase className="mr-1" /> {job.min_experience} -{" "}
              {job.max_experience} Years
            </p>
          </div>
          <div>
            <p className="text-xs font-medium text-gray-500">Location</p>
            <p className="flex items-center">
              <MapPin className="mr-1" /> {job.location}
            </p>
          </div>
          <div>
            <p className="text-xs font-medium text-gray-500">Job Type</p>
            <p className="text-black">
              {startCase(toLower(job.type.replace(/_/g, " ")))}
            </p>
          </div>
          <div>
            <p className="text-xs font-medium text-gray-500">Work Place Type</p>
            <p className="text-black">
              {formatWorkplaceType(job.workplace_type)}
            </p>
          </div>
          <div>
            <p className="text-xs font-medium text-gray-500">Project Team Size</p>
            <p className="flex items-center text-black">{job.team_size}</p>
          </div>
        </div>
  
        {/* Footer */}
        <div className="mt-6 flex justify-between items-center">
          <Button
            className="bg-primary text-white h-[40px] w-[166px] flex hover:bg-primary hover:text-white"
            onClick={() => applicantsPage(job.id, job.code)}
          >
            <Users className="w-[16px] h-[16px] mr-1" />
            <p className="h-[24px] w-[108px] mt-1 text-sm">View Applicants</p>
          </Button>
  
          <p className="text-xs text-gray-400 mt-6">
            Posted on{" "}
            {new Date(job.meta.audit.created_at * 1000).toLocaleDateString(
              "en-GB",
              {
                day: "2-digit",
                month: "short",
                year: "numeric",
              }
            )}
          </p>
        </div>
      </Card>
    );
  };