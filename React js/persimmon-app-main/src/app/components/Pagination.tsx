import React from 'react';
import {
  Pagination,
  PaginationContent,
  PaginationEllipsis,
  PaginationItem,
  PaginationLink,
  PaginationNext,
  PaginationPrevious,
} from "@/components/ui/pagination";

interface PaginationProps {
  currentPage: number;
  totalPages: number;
  onPageChange: (page: number) => void;
}

const PaginationComponent: React.FC<PaginationProps> = ({
  currentPage,
  totalPages,
  onPageChange,
}) => {
  return (
    <div className="mb-11 flex">
      <Pagination>
        <PaginationContent>
          <PaginationItem>
            <PaginationPrevious
              onClick={() => {
                if (currentPage !== 1) {
                  onPageChange(Math.max(1, currentPage - 1));
                }
              }}
              className={
                totalPages <= 0 || currentPage === 1
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
                    onClick={() => onPageChange(page)}
                    isActive={page === currentPage}
                  >
                    {page}
                  </PaginationLink>
                </PaginationItem>
              );
            }
            return null;
          })}

          {currentPage < totalPages - 1 && (
            <>
              {currentPage < totalPages - 2 && <PaginationEllipsis />}
              <PaginationItem>
                <PaginationLink onClick={() => onPageChange(totalPages)}>
                  {totalPages}
                </PaginationLink>
              </PaginationItem>
            </>
          )}

          <PaginationItem>
            <PaginationNext
              onClick={() => {
                if (currentPage !== totalPages) {
                  onPageChange(currentPage + 1);
                } else {
                  onPageChange(totalPages);
                }
              }}
              className={
                totalPages <= 0 || currentPage === totalPages
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
  );
};

export default PaginationComponent;

