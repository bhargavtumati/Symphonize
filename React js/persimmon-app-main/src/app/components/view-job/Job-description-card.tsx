import { JobCardProps } from "@/app/types";
import { Card } from "@/components/ui/card";
import { startCase, toLower } from "lodash";

export const JobDescription: React.FC<JobCardProps> = ({ job }) => {
    return (
      <Card className="bg-white rounded-lg px-6 py-4 text-gray-800 border-none">
        <h2 className="text-lg font-medium mb-4">
          {startCase(toLower("Job description"))}
        </h2>
        <div className="text-gray-800">
          {job.description.split("\n").map((line, index) => (
            <div
              key={index}
              className={line.startsWith("*") ? "font-bold" : ""}
              dangerouslySetInnerHTML={{ __html: line.replace(/\*\*/g, "") }}
            />
          ))}
        </div>
      </Card>
    );
  };