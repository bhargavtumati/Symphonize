import { useState } from "react";
import { HexColorPicker } from "react-colorful";
import { Button } from "@/components/ui/button";
import { Plus } from "lucide-react";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";

interface ColorPickerPopoverProps {
  onAddColor: (color: string) => void;
}

export function ColorPickerPopover({ onAddColor }: ColorPickerPopoverProps) {
  const [newColor, setNewColor] = useState("#000000");
  const [isOpen, setIsOpen] = useState(false);

  const handleAddColor = () => {
    onAddColor(newColor);
    setIsOpen(false);
  };

  return (
    <Popover open={isOpen} onOpenChange={setIsOpen}>
      <PopoverTrigger asChild>
        <Button variant="outline" size="icon" className="w-8 h-8">
          <Plus className="h-4 w-4" />
        </Button>
      </PopoverTrigger>
      <PopoverContent className="w-auto p-0">
        <div className="p-2">
          <HexColorPicker color={newColor} onChange={setNewColor} />
          <Button className="mt-2 w-full" onClick={handleAddColor}>
            Add Color
          </Button>
        </div>
      </PopoverContent>
    </Popover>
  );
}
