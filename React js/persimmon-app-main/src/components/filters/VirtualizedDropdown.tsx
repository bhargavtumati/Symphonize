import React, { useEffect, useRef } from "react";
import { FixedSizeList as List } from "react-window";
import { Input } from "../ui/input";
import { ChevronDown } from "lucide-react";

interface VirtualizedDropdownProps {
    value: string;
    handleChange: (index: number, key: string, value: string) => void;
    index: number;
    placeholder: string;
    options: string[];
}

const VirtualizedDropdown: React.FC<VirtualizedDropdownProps> = ({
    value,
    handleChange,
    index,
    placeholder,
    options,
}) => {
    const [isOpen, setIsOpen] = React.useState(false);
    const [searchQuery, setSearchQuery] = React.useState("");

    // Create a reference for the dropdown container
    const dropdownRef = useRef<HTMLDivElement>(null);

    // Filter options based on searchQuery
    const filteredOptions = options.filter(option =>
        option.toLowerCase().startsWith(searchQuery.toLowerCase())
    );

    const handleSelect = (selectedItem: string) => {
        handleChange(index, "institution", selectedItem || "");
        setIsOpen(false); // Close the dropdown after selection
    };

    const Row = ({ index: itemIndex, style }: { index: number; style: React.CSSProperties }) => (
        <div
            style={style}
            className="p-2 hover:bg-gray-100 cursor-pointer text-sm"
            onClick={() => handleSelect(filteredOptions[itemIndex])}
        >
            {filteredOptions[itemIndex]}
        </div>
    );

    // Close dropdown when clicking outside
    useEffect(() => {
        const handleClickOutside = (event: MouseEvent) => {
            if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
                setIsOpen(false);
            }
        };

        // Add event listener for clicks
        document.addEventListener("mousedown", handleClickOutside);

        // Cleanup event listener on component unmount
        return () => {
            document.removeEventListener("mousedown", handleClickOutside);
        };
    }, []);

    return (
        <div className="relative w-full" ref={dropdownRef}>
            <button
                className="w-full flex justify-between px-4 py-2.5 text-sm border border-gray-300 rounded-md text-left bg-white overflow-hidden text-ellipsis whitespace-nowrap"
                onClick={() => setIsOpen(!isOpen)}
            >
                {value || placeholder}
                <ChevronDown className="w-4 h-4 ml-2" />
            </button>

            {isOpen && (
                <div className="absolute mt-1 z-50 w-full border border-gray-300 rounded-md bg-white shadow-lg max-h-64 overflow-hidden">
                    {/* Input field to filter the options */}
                    <Input
                        type="text"
                        className="w-full px-4 py-2 border-b border-gray-300 rounded-t-md focus:outline-none"
                        placeholder="Search..."
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                    />

                    {/* List of filtered items */}
                    <List
                        height={256} // Dropdown height
                        itemCount={filteredOptions.length}
                        itemSize={70} // Row height
                        width="100%"
                    >
                        {Row}
                    </List>
                </div>
            )}
        </div>
    );
};

export default VirtualizedDropdown;
