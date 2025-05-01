import { SkeletonType } from "@/app/utils/constants"
import { Skeleton } from "@/components/ui/skeleton"
import { TableBody, TableCell, TableRow } from "@/components/ui/table"

interface SkeletonProps {
  className?: string
  type: SkeletonType
  rows?: number
  cellCount?: number
  columns?: number
}

export default function SkeletonComponent({ type, className, rows = 1, columns = 1, cellCount = 1 }: SkeletonProps) {
  const renderSkeletons = (count: number, skeletonClass: string) => {
    return [...Array(count)].map((_, index) => <Skeleton key={index} className={skeletonClass} />)
  }

  const renderGrid = (rowCount: number, columnCount: number, itemClass: string) => {
    return [...Array(rowCount)].map((_, rowIndex) => (
      <div key={rowIndex} className={`grid grid-cols-${columnCount} gap-4`}>
        {renderSkeletons(columnCount, itemClass)}
      </div>
    ))
  }

  switch (type) {
    case SkeletonType.Flat:
      return <Skeleton className={`${className || ""}`} />

    case SkeletonType.Circle:
      return <Skeleton className={`rounded-full ${className || ""}`} />

    case SkeletonType.Card:
      return (
        <Skeleton className="w-full bg-white px-6 py-4 space-y-2 rounded-lg border-none">
          <Skeleton className="h-12 w-full mb-4" />
          {renderGrid(rows, columns, "h-6 w-full")}
        </Skeleton>
      )

    case SkeletonType.Description:
      return (
        <Skeleton className="bg-white rounded-lg px-6 space-y-2 text-gray-800 border-none h-auto">
          <Skeleton className="h-6 w-36 mb-4" />
          {renderSkeletons(rows * columns, "h-4 w-full")}
        </Skeleton>
      )

    case SkeletonType.ShareJob:
      return (
        <Skeleton className="bg-white px-6 py-4 rounded-lg mt-4 xl:h-[206px] flex flex-col justify-between border-none">
          <Skeleton className="h-7 w-28" />
          <div className="flex justify-around mt-4 flex-wrap">
            {renderSkeletons(rows * columns, "h-12 w-12 rounded-full")}
          </div>
          <Skeleton className="w-full h-8 mt-4" />
        </Skeleton>
      )

    case SkeletonType.Publish:
      return (
        <Skeleton className="bg-white px-6 py-8 rounded-lg mt-4 h-fit border-none">
          <div className="flex justify-between items-center mb-14">
            <Skeleton className="h-7 w-32" />
            <Skeleton className="h-9 w-9 rounded-md" />
          </div>
          <div className="space-y-2 mt-0">{renderGrid(rows, columns, "h-5 w-24")}</div>
        </Skeleton>
      )

    case SkeletonType.ApplicantCard:
      return (
        <Skeleton className="rounded-lg shadow-sm border border-gray-100 w-full bg-white">
          <div className="p-8">
            <Skeleton className="h-4 w-52 mb-2" />
            <Skeleton className="mb-3 h-4 w-60" />
            <div className="flex flex-wrap gap-2">{renderSkeletons(rows * columns, "rounded-full h-4 w-28")}</div>
          </div>
          <div className="flex items-center justify-between bg-gray-200 mt-6 h-16 items-center p-4">
            <div className="flex items-center gap-3 max-w-[70%]">
              <Skeleton className="h-[32px] w-[32px] rounded-full" />
              <div>
                <Skeleton className="h-3 w-[455px] mb-3" />
                <Skeleton className="h-3 w-48 mb-3" />
              </div>
            </div>
            <Skeleton className="h-7 w-28 px-4 py-2 rounded-md" />
          </div>
        </Skeleton>
      )

    case SkeletonType.Table:
      return (
        <TableBody>
          {[...Array(rows)].map((_, rowIndex) => (
            <TableRow key={rowIndex} className="bg-white">
              {[...Array(cellCount)].map((_, cellIndex) => (
                <TableCell key={cellIndex} className="border-b border-gray-300 p-4">
                  <Skeleton className="h-5 w-28" />
                </TableCell>
              ))}
            </TableRow>
          ))}
        </TableBody>
      )

    case SkeletonType.Ribbon:
      return (
        <Skeleton className="flex h-12 items-center justify-between rounded-md border border-[#E2E8F0] px-4 bg-white">
          <div className="flex items-center gap-4">
            <div className="flex h-full items-center gap-3">{renderSkeletons(columns, "h-6 w-36")}</div>
          </div>
        </Skeleton>
      )

    default:
      return null
  }
}

