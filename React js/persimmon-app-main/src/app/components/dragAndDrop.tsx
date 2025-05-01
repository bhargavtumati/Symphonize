import { useRef } from "react";
import { useDrag, useDrop } from "react-dnd";
import Image from "next/image";
import { Input } from "@/components/ui/input";
import { GripVertical, X, Check } from "lucide-react";
import { set } from "lodash";
import StagesList from "./StagebleList";

interface Stage {
  uuid: string;
  name: string;
  isNew?: boolean;

}

interface DraggableStageProps {
  stage: Stage;
  index: number;
  moveStage: (dragIndex: number, hoverIndex: number) => void;
  editingIndex: number | null;
  newStageName: string;
  setNewStageName: (name: string) => void;
  handleSaveEdit: (index: number) => void;
  handleDiscardSingleEdit: () => void;
  handleRemoveStage: (stageId: string) => void;
  handleEdit: (index: number) => void;
  setValidationError: (error: string | null) => void;
  setDisableButton: (disableButton: boolean) => void
}

const PROTECTED_STAGES = ['Shortlisted', 'Rejected', 'Selected'];

const DraggableStage = ({
  stage,
  index,
  moveStage,
  editingIndex,
  newStageName,
  setNewStageName,
  handleSaveEdit,
  handleDiscardSingleEdit,
  handleRemoveStage,
  handleEdit,
  setValidationError,
  setDisableButton,
}: DraggableStageProps) => {
  const ref = useRef<HTMLLIElement>(null);

  const [{ isDragging }, drag] = useDrag({
    type: "STAGE",
    item: { index },
    collect: (monitor) => ({
      isDragging: monitor.isDragging(),
    }),
    canDrag: editingIndex === null
  });

  const [, drop] = useDrop({
    accept: "STAGE",
    hover: (item: { index: number }, monitor) => {
      if (!ref.current) {
        return;
      }
      const dragIndex = item.index;
      const hoverIndex = index;

      if (dragIndex === hoverIndex) {
        return;
      }

      moveStage(dragIndex, hoverIndex);
      item.index = hoverIndex;
    },
  });

  drag(drop(ref));

  const isProtectedStage = PROTECTED_STAGES.includes(stage.name);

  const handleDoubleClick = () => {
    if (editingIndex !== index && !isProtectedStage) {
      handleEdit(index);
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newName = e.target.value;
    setNewStageName(newName);
    setValidationError(null);
  };

  const handleEditCrossClick = () => {
    if (stage.isNew) {
      handleRemoveStage(stage.uuid);
      console.log(stage.isNew,);
    }
    else {
     handleDiscardSingleEdit();
      console.log("exist");
    }
  }
  return (
    <li
      ref={ref}
      className={`flex items-center p-3 border rounded-lg shadow-sm group hover:bg-blue-50  hover:border-blue-500 ${isDragging ? "opacity-50" : ""
        }`}
      onDoubleClick={handleDoubleClick}
    >
      {editingIndex === index && !isProtectedStage ? (
        <div className="flex items-center w-full space-x-2">
          <Input
            type="text"
            placeholder="Stage Name"
            value={newStageName}
            onChange={handleInputChange}
            className="flex-1"


          />
          <Check className="w-4 h-4 text-black"
            onClick={() => handleSaveEdit(index)}
          />
          <X className="w-4 h-4 text-black" onClick={handleEditCrossClick} />
        </div>
      ) : (
        <div className="flex justify-between w-full items-center group relative cursor-pointer">
          <div className="flex items-center gap-4">
            <GripVertical className="h-4 w-4 text-[#000] cursor-move" />
            <span className="text-[14px] text-[#64748B]">
              {stage.name || "Stage name-1"}
            </span>
          </div>
          <div className="flex items-center hover:bg-blue-50">
            {!isProtectedStage && (
              <div className="hidden group-hover:flex items-center space-x-2 absolute right-0 pr-3 hover:bg-blue-50">
                <Image
                  src="/images/trash.png"
                  width={16}
                  height={16}
                  alt="Delete stage"
                  onClick={() => handleRemoveStage(stage.uuid)}
                />
                <Image
                  src="/images/pencil.png"
                  width={16}
                  height={16}
                  alt="Edit stage"
                  onClick={() => handleEdit(index)}
                />
              </div>
            )}
          </div>
          <div className={`flex items-center justify-center w-6 h-6 rounded-full bg-[#F1F9FE] p-[4px] ${isProtectedStage ? '' : 'group-hover:invisible'}`}>
            <span className="text-blue-500 font-medium text-[14px] leading-6 text-blue-500 font-medium text-center">
              {index + 1}
            </span>
          </div>
        </div>
      )}
    </li>
  );
};

export default DraggableStage;

