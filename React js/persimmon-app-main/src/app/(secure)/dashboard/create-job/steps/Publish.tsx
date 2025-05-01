import Image from "next/image";
import React, { useState } from "react";
interface Step1RecruiterDetailsProps {
  data: publishdetails;
  onChange: (fieldName: string, value: any) => void; // Updated type to pass both field name and value
  errors: { [key: string]: string };
}

interface Domain {
  id: string;
  name: string;
  description: string;
  logo: string;
  isChecked: boolean;
}

interface publishdetails {
  PublishOnCareerPage: boolean;
  PublishOnOtherDomains: boolean;
  PublishedDomainNames: string[]; // Updated to be a list of strings
}

const Step5Publish: React.FC<Step1RecruiterDetailsProps> = ({
  data,
  onChange,
  errors,
}) => {
  const [domains, setDomains] = useState<Domain[]>([
    {
      id: "indeed",
      name: "Indeed",
      description: "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
      logo: "https://upload.wikimedia.org/wikipedia/commons/f/fc/Indeed_logo.svg",
      isChecked: false,
    },
    {
      id: "naukri",
      name: "Naukri",
      description: "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
      logo: "https://upload.wikimedia.org/wikipedia/commons/9/9b/Naukri_Logo.png",
      isChecked: false,
    },
    {
      id: "linkedin",
      name: "LinkedIn",
      description: "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
      logo: "https://upload.wikimedia.org/wikipedia/commons/c/ca/LinkedIn_logo_initials.png",
      isChecked: false,
    },
  ]);

  const handleToggle = (id: string) => {
    const updatedDomains = domains.map((domain) =>
      domain.id === id ? { ...domain, isChecked: !domain.isChecked } : domain
    );

    setDomains(updatedDomains);

    // Get the selected domain names
    const selectedDomainNames = updatedDomains
      .filter((domain) => domain.isChecked)
      .map((domain) => domain.name);

    // Send selected domain names back to parent
    onChange("PublishedDomainNames", selectedDomainNames);
  };

  return (
    <div>
      <div className="p-4 bg-white">
        <h2 className="text-xl font-semibold">Publish</h2>

        {/* Career page */}
        <div className="mt-4">
          <label className="inline-flex items-center">
            <input
              type="checkbox"
              name="PublishOnCareerPage"
              className="form-checkbox bg-primary w-4 h-4"
              checked={data.PublishOnCareerPage}
              onChange={(e) => onChange(e.target.name, e.target.checked)}
            />
            <span className="ml-2 text-gray-700">
              Publish on career page
            </span>
          </label>
        </div>

        {/* Other Domains */}
        <div className="mt-4">
          <label className="inline-flex items-center">
            <input
              type="checkbox"
              name="PublishOnOtherDomains"
              className="form-checkbox bg-primary w-4 h-4"
              checked={data.PublishOnOtherDomains}
              onChange={(e) => onChange(e.target.name, e.target.checked)}
            />
            <span className="ml-2 text-gray-700">Publish on other domains</span>
          </label>
          <div className="pt-4">
            <div className="flex space-x-2 p-12 bg-[#F6F6F6] w-[250px] h-[233px] rounded-lg items-center">
              <span><Image src="/images/circle-plus.png" width={24} height={24} alt="" /></span>
              <span className="text-[#64748B]">Add Domain</span>
            </div>
          </div>
        </div>

      </div>
      {errors.fullName && <p className="text-red-500">{errors.fullName}</p>}
    </div>
  );
};

export default Step5Publish;
