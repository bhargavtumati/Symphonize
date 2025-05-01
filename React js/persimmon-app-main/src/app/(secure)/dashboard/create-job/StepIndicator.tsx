import React from "react";
import Image from 'next/image';

interface StepIndicatorProps {
  currentStep: number;
  steps: string[];
}

const StepIndicator: React.FC<StepIndicatorProps> = ({
  currentStep,
  steps,
}) => {
  return (
    <div className="grid grid-cols-1 md:grid-cols-6 md:grid-cols-[1.3fr,1.3fr,1.5fr,1.8fr,1.3fr,0.5fr] bg-white mb-6 rounded-lg  md:gap-y-0 md:pl-4 md:py-4">
      {steps.map((stepName, index) => {
        const stepNumber = index + 1;
        return (
          <div
            key={stepNumber}
            className={`text-center flex flex-col md:flex-row items-center space-y-2 md:space-y-0 mr-[0.4em] ${stepName==="Publish"&& "mr-[1em]"}`}
          >
            <span
              className={`block w-8 h-8 md:w-8 md:h-8 rounded-full flex-shrink-0 flex items-center justify-center border ml-0 pl-0 mr-0 pr-0 ${
                currentStep === stepNumber
                  ? "border-blue-600 bg-white text-blue-600"
                  : currentStep > stepNumber
                  ? "border-green-600 bg-white"
                  : "border-gray-200 bg-white text-gray-500"
              }`}
            >
              {currentStep > stepNumber ? (
                <Image
                  src="/check.svg"
                  alt="Completed"
                  width={20}
                  height={20}
                />
              ) : (
                stepNumber
              )}
            </span>
            <span className={`text-xs md:text-sm px-[5px] ${currentStep === stepNumber ? "text-black" : "text-gray-500"
              }`}
            >
              {stepName}
            </span>
            {index < steps.length - 1 && (
              <hr className="hidden md:block h-0.6 my-5 min-w-[50px] flex-grow bg-gray-200" /> 
            )}
          </div>
        );
      })}
    </div>
  );
};

export default StepIndicator;
