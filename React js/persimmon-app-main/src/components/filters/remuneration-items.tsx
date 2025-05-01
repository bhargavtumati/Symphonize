import { SalaryRangeFilterProps } from "@/app/types/model";
import { Checkbox } from "../ui/checkbox";
import { Input } from "../ui/input";
import DoubleSliderComponent from "./double-slider";



const SalaryRangeFilter: React.FC<SalaryRangeFilterProps> = ({
  remuneration,
  remunerationRange,
  checked,
  addToFilter,
  handleMinInputChange,
  handleMaxInputChange,
  handleValueChange,
  getPosition,
}) => {

  return (
    <div className="flex flex-wrap items-center gap-1 p-4 w-3/4">
      {/* Checkbox and Label */}
      <div className="flex items-center space-x-2 min-w-[100px]">
        <Checkbox onClick={addToFilter} checked={checked} />
        <span className="text-sm cursor-pointer truncate w-[100px]">
          Salary Range
        </span>
      </div>

      {/* Min Input */}
      <Input
        className="w-20 h-10 flex-shrink-0"
        type="number"
        placeholder="Min"
        value={remuneration.min_value}
        onChange={handleMinInputChange}
      />

      {/* DoubleSlider */}
      <DoubleSliderComponent
        value={[remuneration.min_value, remuneration.max_value]}
        min={1}
        max={remunerationRange}
        step={1}
        onValueChange={handleValueChange}
        getPosition={(value, min, max) => ((value - min) / (max - min)) * 100}
        minValueLabel={1}
        maxValueLabel={remunerationRange}
      />

      {/* Max Input */}
      <Input
        className="w-20 h-10 flex-shrink-0"
        type="number"
        placeholder="Max"
        value={remuneration.max_value}
        onChange={handleMaxInputChange}

      />
    </div>
  );
};

export default SalaryRangeFilter;