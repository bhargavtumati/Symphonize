import React from "react";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuPortal,
  DropdownMenuSub,
  DropdownMenuSubContent,
  DropdownMenuSubTrigger,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

type MenuOption = {
  label: string;
  action?: () => void;
  disabled?: boolean;
  subMenu?: MenuOption[];
};

type DropdownMenuComponentProps = {
  triggerLabel: React.ReactNode;
  menuOptions: MenuOption[];
};

export const DropdownMenuComponent: React.FC<DropdownMenuComponentProps> = ({
  triggerLabel,
  menuOptions,
 
}) => {
  const renderMenuOptions = (options: MenuOption[]) => {
    return options.map((option, index) => {
      if (option.subMenu) {
        return (
          <DropdownMenuSub key={index}>
            <DropdownMenuSubTrigger disabled={option.disabled}>
              {option.label}
            </DropdownMenuSubTrigger>
            <DropdownMenuPortal>
              <DropdownMenuSubContent>
                {renderMenuOptions(option.subMenu)}
              </DropdownMenuSubContent>
            </DropdownMenuPortal>
          </DropdownMenuSub>
        );
      }

      return (
        <DropdownMenuItem
          key={index}
          onClick={option.action}
          disabled={option.disabled}
        >
          {option.label}
        </DropdownMenuItem>
      );
    });
  };

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button className="bg-transparent text-black hover:bg-transparent">{triggerLabel}</Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent className="w-full">
        {renderMenuOptions(menuOptions)}
      </DropdownMenuContent>
    </DropdownMenu>
  );
};

export default DropdownMenuComponent;
