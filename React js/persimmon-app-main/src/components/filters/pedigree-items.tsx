import { SelectPaddingFiltersProps } from "@/app/types/model";
import DropDown from "./dropdown";
import VirtualizedDropdown from "./VirtualizedDropdown";


const SelectPedigreeFilters: React.FC<SelectPaddingFiltersProps> = ({
  entry,
  index,
  handleChange,
  filterTypeOptions,
  qualificationOptions,
  institutionOptions,
  industryOptions,
  companyOptions,
  isCompanyForm = false,
}) => {
  return (
    <div className="flex flex-wrap items-center gap-[10px]">
      {/* Filter Dropdown */}
      <div className="w-[175px]">
      <DropDown
        value={entry.filterType}
        handleChange={(index, key, value) => handleChange(index, "filterType", value||"")}
        index={index}
        placeHolder="Select"
        options={filterTypeOptions}
        type="select"  // Set to 'select' for simple dropdown
      />
      </div>

      {isCompanyForm ? (
        <>
          {/* Industry Dropdown */}
          <div className="w-[381px]">
          <DropDown
            value={entry.industry}
            handleChange={(index, key, value) => handleChange(index, "industry", value||"")}
            index={index}
            placeHolder="Select Industry"
            options={industryOptions}
            type="select"
          />
          </div>

          {/* Company Dropdown */}
          <div className="w-[381px]">
          <DropDown
            value={entry.company}
            handleChange={(index, key, value) => handleChange(index, "company", value||"")}
            index={index}
            placeHolder="Companies"
            options={companyOptions}
            type="select"
          />
          </div>
        </>
      ) : (
        <>
          {/* Qualification Dropdown */}
          <div className="w-[381px]">
          <DropDown
            value={entry.qualification}
            handleChange={(index, key, value) => handleChange(index, "qualification", value||"")}
            index={index}
            placeHolder="Qualification"
            options={qualificationOptions}
            type="select"
          />
          </div>

          {/* Institution Dropdown */}
          <div className="w-[381px]">
            <VirtualizedDropdown
              value={entry.institution}
              handleChange={handleChange}
              index={index}
              placeholder="Institution Name"
              options={institutionOptions}
            />
          </div>
        </>
      )}
    </div>
  );
};

export default SelectPedigreeFilters;