
"use client";

import React, { useState } from 'react';
import { ArrowLeft, Info } from 'lucide-react';
import { Button } from "@/components/ui/button";
import { DndProvider } from "react-dnd";
import { HTML5Backend } from "react-dnd-html5-backend";
import StagesList from "./StagebleList";

interface CustomizeStagesPopupProps {
  stages: Array<{ uuid: string; name: string }>;
  onStagesUpdate: (stages: Array<{ uuid: string; name: string }>) => void;
  onSaveChanges: () => void;
  onDiscardChanges: () => void;
  disableButton: boolean;
  setDisableButton: (disableButton: boolean) => void
}

const CustomizeStagesPopup: React.FC<CustomizeStagesPopupProps> = ({
  stages,
  onStagesUpdate,
  onSaveChanges,
  onDiscardChanges,
  disableButton,
  setDisableButton
}) => {
  const [hasValidationError, setHasValidationError] = useState(false);

  const handleValidationErrorChange = (error: string | null) => {
    setHasValidationError(!!error);
  };

  return (
    <div className="fixed right-0 top-12 h-full bg-white shadow-lg border-l-2 border-[#E2E8F0] z-40 overflow-auto popup pb-14">
      <div className="px-6 py-8">
        <div className="flex justify-between gap-2">
          <div className="flex">
            <ArrowLeft
              className="h-6 w-6 mt-[2px] cursor-pointer"
              onClick={onDiscardChanges}
            />
            <h1 className="text-[20px] text-[#000000]">
              Customize Application Stages
              <p className="text-[12px] text-[#64748B]">
               Drag the stages to move up or down
              </p>
            </h1>
          </div>
        </div>
      </div>
      <div>
        <div>
          <DndProvider backend={HTML5Backend}>
            <div className="container">
              <StagesList
                initialStages={stages}
                onStagesUpdate={onStagesUpdate}
                onValidationErrorChange={handleValidationErrorChange}
                setDisableButton={setDisableButton}
              />
            </div>
          </DndProvider>
        </div>

        <div className="mt-4 px-6 ">
          <div className="flex justify-end space-x-2">
            <button
              className={`border px-4 py-2 rounded-md text-[14px] font-medium ${disableButton ? 'bg-gray-300 text-gray-500 cursor-not-allowed' : ''}`}
              onClick={onDiscardChanges}
              disabled={disableButton}
            >
              Discard
            </button>
            <Button
              onClick={onSaveChanges}
              className={`bg-primary text-white hover:bg-primary ${disableButton ? "opacity-50 cursor-not-allowed" : ""}`}
              disabled={hasValidationError || disableButton}
            >
              Save Changes
            </Button>
          </div>

          <p className="text-[12px] text-[#64748B] py-3 flex items-center space-x-2">
            <Info className="w-[16px] h-[16px]" />{" "}
            <span>This customization applies to this job only.</span>
          </p>
        </div>
      </div>
    </div>

  );
};

export default CustomizeStagesPopup;


