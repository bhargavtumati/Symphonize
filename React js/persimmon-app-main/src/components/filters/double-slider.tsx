import React, { useState } from "react";
import * as DoubleSlider from "@radix-ui/react-slider";

interface IDoubleSliderProps {
  value: number[];
  min: number;
  max: number;
  step: number;
  onValueChange: ((value: number[]) => void) | undefined;
  getPosition: (value: number, min: number, max: number) => number;
  minValueLabel?: number;
  maxValueLabel?: number;
}
const DoubleSliderComponent: React.FC<IDoubleSliderProps> = ({
  value,
  min,
  max,
  step,
  onValueChange,
  getPosition,
  minValueLabel = 1,
  maxValueLabel = 2,
}) => {
  const [hoveredThumb, setHoveredThumb] = useState<number | null>(null);
  return (
    <div className="flex-1 flex items-center relative">
      <DoubleSlider.Root
        className="relative flex items-center w-full h-5"
        value={value}
        min={min}
        max={max}
        step={step}
        onValueChange={onValueChange}
      >
        <DoubleSlider.Track className="relative bg-gray-300 rounded-full h-2 flex-1">
          <DoubleSlider.Range className="absolute bg-primary rounded-full h-full" />
        </DoubleSlider.Track>
        <DoubleSlider.Thumb
          className="block w-4 h-4 bg-white border-2 border-primary rounded-full"
          style={{ left: `${getPosition(value[0], min, max)}%` }}
          onMouseEnter={() => setHoveredThumb(0)}
          onMouseLeave={() => setHoveredThumb(null)}
        />
        {hoveredThumb === 0 && (
          <div
            style={{ left: `${getPosition(value[0], min, max)}%` }}
            className="absolute transform -translate-x-1/2 text-sm text-gray-600 mt-8"
          >
            {!isNaN(value[0]) ? value[0] : minValueLabel}
          </div>
        )}

        {/* Second Thumb */}
        <DoubleSlider.Thumb
          className="block w-4 h-4 bg-white border-2 border-primary rounded-full"
          style={{ left: `${getPosition(value[1], min, max)}%` }}
          onMouseEnter={() => setHoveredThumb(1)}
          onMouseLeave={() => setHoveredThumb(null)}
        />
        {hoveredThumb === 1 && (
          <div
            style={{ left: `${getPosition(value[1], min, max)}%` }}
            className="absolute transform -translate-x-1/2 text-sm text-gray-600 mt-8"
          >
            {!isNaN(value[1]) ? value[1] : maxValueLabel}
          </div>
        )}
      </DoubleSlider.Root>
    </div>
  );
};

export default DoubleSliderComponent;
