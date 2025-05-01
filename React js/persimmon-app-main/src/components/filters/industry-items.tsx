import { Input } from '@/components/ui/input';
import { Checkbox } from "@/components/ui/checkbox";
import PreferenceSelect from './preference-select';
import DoubleSliderComponent from "./double-slider";
import DropDown from "@/components/filters/dropdown"

type Industry = {
  name: string;
  checked: boolean;
  isEditing: boolean;
  pref: string;
  min: number;
  max: number;
  errorMessage: string;
};

type IndustryItemProps = {
  industry: Industry;
  index: number;
  handleCheckboxChange: (index: number, isChecked: boolean) => void;
  handleIndustryChange: (index: number, value: string) => void;
  handleDoubleClick: (index: number) => void;
  handleBlur: (index: number) => void;
  handlePreferenceChange: (index: number, value: string) => void;
  handleMinInputChange: (index: number, event: React.ChangeEvent<HTMLInputElement>) => void;
  handleMaxInputChange: (index: number, event: React.ChangeEvent<HTMLInputElement>) => void;
  handleValueChange: (index: number, newRange: [number, number]) => void;
  handleSearchChange: (event: React.ChangeEvent<HTMLInputElement>) => void;
  searchTerm: string;
  filteredIndustries: string[] | undefined;
  getPosition: (value: number, range: number) => number;
  experienceRange: number;
  setIndustries: React.Dispatch<React.SetStateAction<Industry[]>>;
};

const IndustryItem: React.FC<IndustryItemProps> = ({
  industry,
  index,
  handleCheckboxChange,
  handleIndustryChange,
  handleDoubleClick,
  handleBlur,
  handlePreferenceChange,
  handleMinInputChange,
  handleMaxInputChange,
  handleValueChange,
  handleSearchChange,
  searchTerm,
  filteredIndustries,
}) => {
  return (
    <div className="flex flex-wrap items-center gap-4 p-4">
      {/* Checkbox and Label */}
      <div className="flex flex-wrap items-center space-x-2 min-w-[155px]">
        <Checkbox
          checked={industry.checked || false} // Default to false if not set
          onCheckedChange={(isChecked) => handleCheckboxChange(index, isChecked === true)}
        />
        {industry.isEditing ? (
          <div className='w-[155px]'>
            <DropDown
            searchTerm={searchTerm}
            handleSearchChange={handleSearchChange}
            filter={filteredIndustries}
            handleChange={(index, _, value) => handleIndustryChange(index, value!)}
            index={index}
            placeHolder="Industry Type"
          />
            </div>) : (
          <span
            className="text-sm cursor-pointer truncate w-[200px]"
            onDoubleClick={() => handleDoubleClick(index)}
            tabIndex={0}
            onBlur={() => handleBlur(index)}
          >
            {industry.name}
          </span>
        )}
      </div>

      {/* Select Dropdown */}
      <PreferenceSelect
        key={index}
        value={industry.pref}
        onChange={(value) => handlePreferenceChange(index, value)}
      />
      {/* Min Input */}
      <Input
        className="w-20 h-10 flex-shrink-0"
        type="number"
        placeholder="Min"
        value={industry.min}
        onChange={(e) => handleMinInputChange(index, e)}
      />

      {/* DoubleSlider */}
      <div className='flex flex-wrap w-[450px]'>
      <DoubleSliderComponent
        value={[industry.min, industry.max]}
        min={1}
        max={50}
        step={1}
        onValueChange={(newRange: any) => handleValueChange(index, newRange)}
        getPosition={(value: number, min: number, max: number) => ((value - min) / (max - min)) * 100}
        minValueLabel={1}
        maxValueLabel={50}
      />
      </div>


      {/* Max Input */}
      <Input
        className="w-20 h-10 flex-shrink-0"
        type="number"
        placeholder="Max"
        value={industry.max}
        onChange={(e) => handleMaxInputChange(index, e)}
      />
    </div>
  );
};

export default IndustryItem;