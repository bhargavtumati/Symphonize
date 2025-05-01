import React, { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { auth } from "../../../components/firebaseConfig";
import { Eye, Loader2, Plus } from "lucide-react";
import {SkeletonType} from "@/app/utils/constants";
import { format } from "date-fns";
import Link from "next/link";
import Image from "next/image";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  Pagination,
  PaginationContent,
  PaginationEllipsis,
  PaginationItem,
  PaginationLink,
  PaginationNext,
  PaginationPrevious,
} from "@/components/ui/pagination";
import { apiService } from "../../../api/service";
import DropdownMenuComponent from "@/app/components/drop-down-menu-component";
import SortableColumn from "@/app/components/sorting-columns";
import {
  DEFAULT_SORTING_ORDER,
  JOB_COLUMNS,
  SORTING_STEPS,
  SORTING_COLUMN_NAMES,
  FILTER_OPTIONS,
} from "@/app/utils/constants";
import { dateWithoutTimeZone } from "@/lib/utils";

import SkeletonComponent from "@/app/components/skeleton/card-skeleton";
import { Skeleton } from "@/components/ui/skeleton";

const CreateJobPage: React.FC = () => {
  const [jobs, setJobs] = useState([]);
  const [isReadyToCreateJob, setIsReadyToCreateJob] = useState(false);
  const [loading, setLoading] = useState(true);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalCount, setTotalCount] = useState(null);
  const router = useRouter();
  const [popupJobId, setPopupJobId] = useState<number | null>(null);
  const [hoveredRow, setHoveredRow] = useState<number | null>(null);
  const [selectedFilter, setSelectedFilter] = useState("code");
  const [searchTerm, setSearchTerm] = useState("");
  const [jobId, setJobId] = useState("");
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [sortingOrder, setSortingOrder] = useState<{ [key: string]: number }>(
    DEFAULT_SORTING_ORDER
  );

  const [columnLabel, setColumnLabel] = useState("jobId");
  const columnMapping: Record<string, string> = SORTING_COLUMN_NAMES;
  const handleSortingClick = (selectedColumn: string) => {
    setColumnLabel(selectedColumn);
    setSortingOrder((prevOrder) => {
      const currentOrder = prevOrder[selectedColumn];
      let newOrder = currentOrder + 1;
      if (newOrder === SORTING_STEPS) newOrder = 0;
      return {
        ...prevOrder,
        [selectedColumn]: newOrder,
      };
    });
  };

  const togglePopup = (jobId: number | null) => {
    setPopupJobId(popupJobId === jobId ? null : jobId); // Toggle the popup for the selected job
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

  useEffect(() => {
    setLoading(true);
    const unsubscribe = auth.onAuthStateChanged(async (user) => {
      if (user) {
        try {
          let response;
          const ordering =
            sortingOrder[columnLabel] === 1
              ? "asc"
              : sortingOrder[columnLabel] === 2
              ? "desc"
              : "";
          const sortingColumn = columnMapping[columnLabel];
          if (searchTerm) {
            const timeZone = Intl.DateTimeFormat().resolvedOptions().timeZone; 
            console.log("time zone: ",timeZone)
            response = await apiService(
              `/jobs?page=${currentPage}&${selectedFilter.toLowerCase()}=${searchTerm}&time_zone=${timeZone}`,
              "GET",
              null
            );
          } else if (sortingOrder[columnLabel] === 0) {
            response = await apiService(
              `/jobs?page=${currentPage}`,
              "GET",
              null
            );
            if (Array.isArray(response.jobs) && response.jobs.length === 0) {
              setIsReadyToCreateJob(true);
            }
          } else {
            response = await apiService(
              `/jobs?page=${currentPage}&sort=${ordering}%2C${sortingColumn}`,
              "GET",
              null
            );
          }

          const data = response;
          if (Array.isArray(data.jobs) && data.jobs.length > 0) {
            setJobs(data.jobs);
            setTotalPages(data.pagination.total_pages);
            setTotalCount(data.pagination.total_count);
            setIsReadyToCreateJob(false);
          } else {
            setJobs([]);
            setTotalCount(null);
          }
        } catch (error) {
          console.error("Error fetching jobs:", error);
          setJobs([]);
        } finally {
          setLoading(false);
        }
      } else {
        console.error("User is not authenticated");
        setIsReadyToCreateJob(true);
        setLoading(false);
      }
    });

    return () => unsubscribe();
  }, [currentPage, searchTerm, sortingOrder, columnLabel]);

  const handlePageChange = (page: number) => {
    setCurrentPage(page);
  };

  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchTerm(e.target.value);
    setCurrentPage(1);
    setCurrentPage(1);
  };

  const handleFilterChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setSelectedFilter(e.target.value);
    setSearchTerm("");
  };
  const handleJobEvent = (job: any, actionType: string) => {
    router.push(`dashboard/create-job?action=${actionType}&jobId=${job.id}`);
  };

  const onAllApplicants = (jobId: number, jobCode: string) => {
    router.push(
      `/dashboard/view-job-page/all-applicants?jobId=${jobId}&jobCode=${jobCode}`
    );
  };

  const openModal = (job: any) => {
    setJobId(job.id);
    setIsModalOpen(true);
  };

  const closeModal = () => {
    setIsModalOpen(false);
  };

  const onCreateJobClick = () => {
    sessionStorage.removeItem("jobId");
    sessionStorage.removeItem("action");
    router.push("dashboard/create-job");
  };

  const handleRowClick = (jobId: any, jobCode: string) => {
    router.push(`/dashboard/view-job-page?jobId=${jobId}&jobCode=${jobCode}`);
  };
    return (
    <div className="w-full">
      {isReadyToCreateJob ? (
        <div className="flex items-center justify-center h-screen bg-gray-100">
          <div className="text-center">
            <h1 className="text-2xl font-semibold mb-2">Ready to hire?</h1>
            <p className="text-gray-500 mb-4">
              Post your first job and attract great talent!
            </p>
            <div className="flex justify-center">
              <button
                className="flex px-4 py-2 bg-primary text-white rounded"
                onClick={onCreateJobClick}
              >
                <Plus className="mr-2" />
                Create Job
              </button>
            </div>
          </div>
        </div>
      ) : (
        <div className=" p-6 bg-gray-50">
          <div className="flex justify-between items-center mb-4">
            <h1 className="text-xl font-semibold">Jobs</h1>

            <div className="flex items-center space-x-2">
              {/* Search field with dropdown */}
              <div className="relative flex items-center border rounded-md">
                <select
                  value={selectedFilter}
                  onChange={handleFilterChange}
                  className="bg-transparent text-black  pl-2 py-2 rounded-l-md bg-white border-none focus:outline-none"
                >
                  {FILTER_OPTIONS.map((option) => (
                    <option key={option.value} value={option.value}>
                      {option.label}
                    </option>
                  ))}
                </select>

                <input
                  type="text"
                  placeholder="Search"
                  value={searchTerm}
                  onChange={handleSearchChange}
                  className="pl-3 pr-10 py-2 w-90 rounded-r-md border-none focus:outline-none"
                />

                <div className="absolute right-3 top-1/2 transform -translate-y-1/2">
                  <Image
                    src="/images/searchIcon.png"
                    width={18}
                    height={18}
                    alt="Search"
                  />
                </div>
              </div>

              {/* Create Job Button */}
              <Button
                className="bg-primary text-white"
                onClick={onCreateJobClick}
              >
                <Plus className="w-6 h-6" />
                Create Job
              </Button>
            </div>
          </div>

          <Table className="min-w-full">
            <TableHeader>
              <TableRow className="bg-white">
                {/* Your table headers */}
                {JOB_COLUMNS.map((column, index) => (
                  <TableHead
                    key={index}
                    className="border-b border-gray-300 p-3 text-left"
                  >
                    <SortableColumn
                      label={column.label}
                      sortKey={column.sortKey}
                      sortingOrder={sortingOrder}
                      onSort={handleSortingClick}
                    />
                  </TableHead>
                ))}
                <TableHead className="border-b border-gray-300 p-3 text-left">
                  Actions
                </TableHead>
              </TableRow>
            </TableHeader>
            {loading ? (
              <SkeletonComponent type={SkeletonType.Table} rows={13} cellCount={9} />
            ) : (
              <TableBody>
                {jobs.length === 0 ? (
                  <TableRow>
                    <TableCell
                      colSpan={9}
                      className="text-center p-10 text-lg font-semibold"
                    >
                      No Jobs found
                    </TableCell>
                  </TableRow>
                ) : (
                  <>
                    {jobs.map((job: any, index) => {
                      const menuOptions = [
                        {
                          label:
                            job.status === "ACTIVE" ? "Edit" : "Edit & Repost",
                          action: () =>
                            job.status === "ACTIVE"
                              ? handleJobEvent(job, "Edit")
                              : handleJobEvent(job, "Repost"), // Pass the job object to handleJobEvent
                        },
                        ...(job.status !== "CLOSED"
                          ? [
                              {
                                label: "Close",
                                action: () => openModal(job.id),
                              },
                            ]
                          : []),
                      ];
                      return (
                        <TableRow
                          key={job.id}
                          className="bg-white cursor-pointer" // Add cursor-pointer here
                          onMouseEnter={() => setHoveredRow(index)}
                          onMouseLeave={() => setHoveredRow(null)}
                        >
                          <TableCell
                            className={`border-b border-gray-300 p-3 ${
                              job.status === "CLOSED"
                                ? "text-gray-500 opacity-40"
                                : ""
                            }`}
                            onClick={() => handleRowClick(job.id, job.code)}
                          >
                            {loading && <Skeleton className="h-6 w-28" />}
                            {job.code}
                          </TableCell>
                          <TableCell
                            className={`border-b border-gray-300 p-3 ${
                              job.status === "CLOSED"
                                ? "text-gray-500 opacity-40"
                                : ""
                            }`}
                            onClick={() => handleRowClick(job.id, job.code)}
                          >
                            <Link href="" className="text-primary">
                              {job.title}
                            </Link>
                          </TableCell>
                          <TableCell
                            className={`border-b border-gray-300 p-3 ${
                              job.status === "CLOSED"
                                ? "text-gray-500 opacity-40"
                                : ""
                            }`}
                            onClick={() => handleRowClick(job.id, job.code)}
                          >
                            {job.client_name}
                          </TableCell>
                          <TableCell
                            className={`border-b border-gray-300 p-3 ${
                              job.status === "CLOSED"
                                ? "text-gray-500 opacity-40"
                                : ""
                            }`}
                            onClick={() => handleRowClick(job.id, job.code)}
                          >
                            {job.location}
                          </TableCell>
                          <TableCell className="p-3 border-b border-gray-300">
                            <div className="flex items-center">
                              <span
                                className={`${
                                  job.status === "CLOSED"
                                    ? "text-gray-500 opacity-40"
                                    : ""
                                }`}
                              >
                                {job.applicants || 0}
                              </span>
                              <span>
                                {hoveredRow === index && (
                                  <Eye
                                    className="cursor-pointer text-blue-600 ml-4 w-[16px] h-[16px]"
                                    onClick={(e) =>
                                      onAllApplicants(job.id, job.code)
                                    }
                                  />
                                )}
                              </span>
                            </div>
                          </TableCell>
                          <TableCell
                            className={`border-b border-gray-300 p-3 ${
                              job.status === "CLOSED"
                                ? "text-gray-500 opacity-40"
                                : ""
                            }`}
                            onClick={() => handleRowClick(job.id, job.code)}
                          >
                            {format(
                              new Date(job.posted_on * 1000),
                              "dd MMM yyyy"
                            )}
                          </TableCell>
                          <TableCell
                            className={`border-b border-gray-300 p-3 ${
                              job.status === "CLOSED"
                                ? "text-gray-500 opacity-40"
                                : ""
                            }`}
                            onClick={() => handleRowClick(job.id, job.code)}
                          >
                            {format(
                              dateWithoutTimeZone(job.target_date),
                              "dd MMM yyyy"
                            )}
                          </TableCell>
                          <TableCell className="border-b border-gray-300 p-3 ">
                            {job.status === "ACTIVE" ? (
                              <span className="text-green-500 py-1 ">
                                Active
                              </span>
                            ) : (
                              <span
                                className={`text-gray-700 py-1 ${
                                  job.status === "CLOSED"
                                    ? "text-gray-500 opacity-40"
                                    : ""
                                }`}
                              >
                                Closed
                              </span>
                            )}
                          </TableCell>
                          <TableCell
                            className={`border-b border-gray-300 p-3 ${
                              job.status === "CLOSED" ? "text-gray-500" : ""
                            }`}
                          >
                            <div className="flex items-center">
                              <button
                                type="button"
                                onClick={() => togglePopup(job.id)}
                              >
                                <DropdownMenuComponent
                                  triggerLabel="..."
                                  menuOptions={menuOptions}
                                />
                              </button>
                            </div>
                          </TableCell>
                        </TableRow>
                      );
                    })}
                  </>
                )}
              </TableBody>
            )}
          </Table>

          {isModalOpen && (
            <div className="fixed inset-0 flex items-center justify-center z-50 bg-black bg-opacity-50 popup">
              <div className="bg-white rounded-lg p-6 w-96 shadow-lg w-[564px] h-[208px] p-[32px]">
                <button
                  className="absolute top-2 right-2 text-gray-600"
                  onClick={closeModal}
                >
                  &times;
                </button>
                <h2 className="text-[20px] font-semibold text-[#1E293B] mb-2">
                  Are You Sure You Want to Close the Job?
                </h2>
                <p className="text-[#64748B] text-[14px] mb-6">
                  By closing the job, the job will be removed from the career
                  page and all job boards.
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

          {/* Pagination Component */}
          <div className="flex  justify-between mt-4">
            <div className="text-[14px] text-[#475569]">
              {" "}
              No of Jobs : {totalCount ? totalCount : 0}
            </div>
            <Pagination className="w-auto justify-end mx-0">
              {/* Previous Button */}
              <PaginationContent>
                <PaginationItem>
                  <PaginationPrevious
                    onClick={() => {
                      if (currentPage !== 1) {
                        handlePageChange(Math.max(1, currentPage - 1));
                      }
                    }}
                    className={
                      currentPage === 1
                        ? "cursor-not-allowed opacity-50"
                        : "cursor-pointer"
                    }
                  >
                    Previous
                  </PaginationPrevious>
                </PaginationItem>

                {Array.from({ length: totalPages }, (_, index) => {
                  const page = index + 1;
                  if (page >= currentPage - 1 && page <= currentPage + 1) {
                    return (
                      <PaginationItem key={index}>
                        <PaginationLink
                          onClick={() => handlePageChange(page)}
                          isActive={page === currentPage}
                        >
                          {page}
                        </PaginationLink>
                      </PaginationItem>
                    );
                  }
                  return null;
                })}

                {/* Last Page */}
                {currentPage < totalPages - 1 && (
                  <>
                    {currentPage < totalPages - 2 && <PaginationEllipsis />}
                    <PaginationItem>
                      <PaginationLink
                        onClick={() => handlePageChange(totalPages)}
                      >
                        {totalPages}
                      </PaginationLink>
                    </PaginationItem>
                  </>
                )}

                {/* Next Button */}
                <PaginationItem>
                  <PaginationNext
                    onClick={() => {
                      if (currentPage !== totalPages) {
                        handlePageChange(currentPage + 1);
                      } else {
                        handlePageChange(totalPages);
                      }
                    }}
                    className={
                      currentPage === totalPages
                        ? "cursor-not-allowed opacity-50"
                        : "cursor-pointer"
                    }
                  >
                    Next
                  </PaginationNext>
                </PaginationItem>
              </PaginationContent>
            </Pagination>
          </div>
        </div>
      )}
    </div>
  );
};

export default CreateJobPage;
