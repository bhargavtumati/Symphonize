"use client";

import { useState, useEffect } from "react";
import { DndProvider } from "react-dnd";
import { HTML5Backend } from "react-dnd-html5-backend";
import DraggableStage from "./dragAndDrop";
import { Button } from "@/components/ui/button";
import Image from "next/image";
import AlertDialogWrapper from "./alertPopup";
import { cn } from "@/lib/utils";
import { validateStageName } from "../utils/validations"

interface Stage {
  uuid: string;
  name: string;
 isNew?:boolean;
}

export default function StagesList({
  initialStages,
  onStagesUpdate,
  onValidationErrorChange,
  setDisableButton,
}: {
  initialStages: Stage[];
  onStagesUpdate: (stages: Stage[]) => void;
  onValidationErrorChange: (error: string | null) => void;
  setDisableButton: (disableButton: boolean) => void
}) {
  const [stages, setStages] = useState(initialStages);
  const [editingIndex, setEditingIndex] = useState<number | null>(null);
  const [newStageName, setNewStageName] = useState("");
  const [isAddingNewStage, setIsAddingNewStage] = useState(false);
  const isMaxStagesReached = stages.length >= 18;
  const isAddStageDisabled = isAddingNewStage || isMaxStagesReached;
  const [validationError, setValidationError] = useState<string | null>(null);

  const [modalState, setModalState] = useState<{
    type: "delete" | null;
    id?: string | undefined;
  }>({ type: null });

  useEffect(() => {
    onStagesUpdate(stages);
  }, [stages, onStagesUpdate]);

  useEffect(() => {
    onValidationErrorChange(validationError);
  }, [validationError, onValidationErrorChange]);

  const moveStage = (dragIndex: number, hoverIndex: number) => {
    const draggedStage = stages[dragIndex];
    const newStages = [...stages];
    newStages.splice(dragIndex, 1);
    newStages.splice(hoverIndex, 0, draggedStage);
    setStages(newStages);
    setDisableButton(false);
  };

  const closeModal = () => {
    setModalState({ type: null });
  };

  const handleSaveEdit = (index: number) => {

  const error = validateStageName(newStageName);
    if (error) {
      setValidationError(error);
      return;
    }

    if (stages.some((s, i) => i !== index && s.name.toLowerCase() === newStageName.toLowerCase())) {
      setValidationError("Stage already exists");
      return;
    }
    
    const newStages = [...stages];
    newStages[index].name = newStageName;
    newStages[index].isNew=false;
    setStages(newStages);
    setEditingIndex(null);
    setNewStageName('');
    setDisableButton(false);
    setIsAddingNewStage(false);
    setValidationError(null);
  };

  const handleEdit = (index: number) => {
    setEditingIndex(index);
    setNewStageName(stages[index].name);
    setValidationError(null);
  };

  const handleOpenDeletePopup = (id: string,isNew?:boolean) => {
    const stage=stages.find((stage) => stage.uuid === id);
    if(stage?.isNew){   
      handleRemoveStage(id);
    }else{
    setModalState({ type: "delete", id });
    }

  };


  const handleRemoveStage = (id: string | undefined) => {
    const updatedStages = stages.filter((stage) => stage.uuid !== id); 
    setStages(updatedStages);
    setIsAddingNewStage(false);
    setValidationError(null);
    setDisableButton(false);
   
  };

  const handleDiscardSingleEdit = () => {
    setEditingIndex(null);
    setNewStageName("");
    setValidationError(null);
  };

  const handleAddNewStage = () => {
    if(isMaxStagesReached) return;
    const newStage: Stage = {
      uuid: crypto.randomUUID(),
      name: "Stage name-1",
      isNew:true,
    };  
    setStages([...stages, newStage]);
    setEditingIndex(stages.length);
    setNewStageName(newStage.name);
    setIsAddingNewStage(true); 
    setDisableButton(true);

  };

  return (
    <>
      <div className="w-full max-w-2xl mx-auto bg-white">
        <div className="px-6 py-0 pb-3.5">
          <div className="flex justify-end items-right space-x-2">
            <Button
              onClick={handleAddNewStage}
              variant="outline"
              className={cn(
                "mb-4 border-[#E2E8F0] hover:bg-blue-50",
                isAddStageDisabled ?  'bg-gray-300 text-gray-500 cursor-not-allowed' : "",
                "justify-content-end"
              )}
              disabled={isAddStageDisabled}
            >
              <span>
                <Image
                  src="/images/plus.png"
                  className="mr-2"
                  alt=""
                  width={16}
                  height={16}
                />
              </span>
              <span className="text-[12px] text-[#020617] font-medium leading-5">
                Add New Stage
              </span>
            </Button>
          </div>

          <DndProvider backend={HTML5Backend}>
            <ul className="space-y-1">
              <li className="items-center px-[2.7rem] py-3 bg-white border rounded-lg shadow-sm text-[14px] text-[#64748B]">
                All Applicants
              </li>
              <li className="items-center px-[2.7rem] py-3 bg-white border rounded-lg shadow-sm text-[14px] text-[#64748B]">
                AI Top Results
              </li>
              {stages.map((stage, index) => (
                <DraggableStage
                  key={stage.uuid}
                  stage={stage}
                  index={index}
                  moveStage={moveStage}
                  editingIndex={editingIndex}
                  newStageName={newStageName}
                  setNewStageName={setNewStageName}
                  handleSaveEdit={handleSaveEdit}
                  handleRemoveStage={handleOpenDeletePopup}
                  handleDiscardSingleEdit={handleDiscardSingleEdit}
                  handleEdit={handleEdit}
                  setValidationError={setValidationError}
                  setDisableButton={setDisableButton}
                />
              ))}
            </ul>
            {validationError && (
              <div className="mt-4 p-2 w-[300px] text-[12px] text-red-700 rounded">
                {validationError}
              </div>
            )}
          </DndProvider>
        </div>
      </div>
      <AlertDialogWrapper
        isOpen={modalState.type === "delete"}
        onClose={closeModal}
        title="Are you sure you want to delete?"
        description="By deleting, you'll lose the track of applicants data of this stage"
        confirmText="Delete"
        cancelText="Cancel"
        onConfirm={() => handleRemoveStage(modalState.id)}
      />
    </>
  );
}


