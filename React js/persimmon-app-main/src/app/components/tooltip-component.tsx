import React, { ElementType, ReactElement, useState } from "react";
import { Tooltip, TooltipTrigger, TooltipContent, TooltipProvider } from "@/components/ui/tooltip";

// Define the type for the component's props
type TooltipComponentProps = {
    icon: ReactElement; // Icon to display
    message: string; // Tooltip message text
    tag: ElementType; // The tag type for wrapping the message (e.g., "p", "span", "div")
    className?: string; // Optional additional className for TooltipContent
};

const TooltipComponent: React.FC<TooltipComponentProps> = ({icon, message, tag: Tag, className }) => {
    const [isTooltipVisible, setIsTooltipVisible] = useState(false); // State to manage tooltip visibility

    // Handle tooltip visibility toggle on icon click
    const handleIconClick = (e: React.MouseEvent) => {
        e.stopPropagation(); // Prevents the click from bubbling up
        setIsTooltipVisible((prev) => !prev); // Toggle tooltip visibility on click
    };

    return (
        <TooltipProvider>
            <Tooltip open={isTooltipVisible} onOpenChange={setIsTooltipVisible}>
                {/* TooltipTrigger is responsible for triggering tooltip on hover or click */}
                <TooltipTrigger
                    asChild
                    onClick={handleIconClick} // Handle click event to toggle visibility
                >
                    <div className="relative inline-block">
                        <span
                            className="cursor-pointer"
                            onClick={handleIconClick} // Handle click event to toggle visibility
                        >
                            {icon}
                        </span>
                    </div>
                </TooltipTrigger>

                {/* Tooltip content */}
                <TooltipContent
                    className={`absolute top-full mt-4 left-1/2 z-10 ${className}`}
                >
                    <Tag>{message}</Tag>
                </TooltipContent>
            </Tooltip>
        </TooltipProvider>
    );
};

export default TooltipComponent;
