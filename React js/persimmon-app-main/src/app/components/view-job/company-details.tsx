import { JobCardProps } from "@/app/types";
import { formatWebsite } from "@/app/utils/helper";
import { Card } from "@/components/ui/card";
import { startCase, toLower } from "lodash";

export const CompanyDetails: React.FC<JobCardProps> = ({ company }) => {
    return (
      <Card className="bg-white px-6 py-4 border-none">
        <h2 className="text-lg font-medium mb-4">Company Details</h2>
        <ul className="list-none space-y-2">
          <li>Company Name: {company.name}</li>
          <li>Website: {formatWebsite(company.website)}</li>
          <li>Industry: {company.industry_type}</li>
          <li>
            Company Type: {startCase(toLower(company.type.replace("_", " ")))}
          </li>
          <li>Company Size: {company.number_of_employees}</li>
        </ul>
      </Card>
    );
  };