import { JobCardProps } from "@/app/types";
import { Card } from "@/components/ui/card";

export const JobPerformanceCard: React.FC<JobCardProps> = ({ count }) => {
  return (
    <Card className="bg-white px-6 py-4 xl:h-[152px] rounded-lg  border-none ">
      <h2 className="text-lg font-medium">Job Performance</h2>
      <div className="flex justify-between mt-4 flex-wrap	">
        <div className="text-center">
          <p className="text-xl font-semibold">{count.all_applicants}</p>
          <p className="text-sm text-slate-500">Applicants</p>
        </div>
        <div className="text-center">
          <p className="text-xl font-semibold">{count.shortlisted}</p>
          <p className="text-sm text-slate-500">Shortlisted</p>
        </div>
        <div className="text-center">
          <p className="text-xl font-semibold">{count.selected}</p>
          <p className="text-sm text-slate-500">Selected</p>
        </div>
        <div className="text-center">
          <p className="text-xl font-semibold">{count.rejected}</p>
          <p className="text-sm text-slate-500">Rejected</p>
        </div>
      </div>
    </Card>
  );
};