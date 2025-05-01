import { applicantsPreferedData } from "@/app/types/model";
import { validateResponsibility } from "@/app/utils/validations";
import { useEffect } from "react";
import { Checkbox } from "@/components/ui/checkbox";
import { IResponsibilitiesFC } from "@/components/filters/models";

export const FilterByResponsibilities: React.FC<IResponsibilitiesFC> = ({ responsibilities, setResponsibilities, setErrorMessage, setShowInputField, setNewResponsibility, newResponsibility, showInputField, responsibilitiesError, setResponsibilitiesError }) => {

    const handleCheckboxChange = (index: number, isChecked: boolean) => {
        setResponsibilities((prevResponsibilities) => {
            const updatedResponsibilities = [...prevResponsibilities];
            updatedResponsibilities[index].checked = isChecked;
            return updatedResponsibilities;
        });
    };

    useEffect(() => {
        // Update applicantsPreferedData with only the checked responsibilities
        const selectedResponsibilities = responsibilities
            .filter((responsibility) => responsibility.checked)
            .map((responsibility) => responsibility.text); // Use the text of the responsibility

        applicantsPreferedData.filters["responsibilities"] = selectedResponsibilities; // Update applicantsPreferedData payload
    }, [responsibilities]); // Run when responsibilities state changes

    const addNewResponsibility = () => {
        setShowInputField(true); // Show input field for new responsibility
    };

    const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        setNewResponsibility(e.target.value);
        setResponsibilitiesError("");
        setErrorMessage((prev)=>({...prev,responsibilities:""}));
    };

    const handleEnterPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
        if (e.key === "Enter" && newResponsibility.trim()) {
            // Validate the new responsibility text
            const respError = validateResponsibility(newResponsibility, responsibilities)
            if (respError) {
                setErrorMessage((prev)=>({...prev,responsibilities:respError}));
                setResponsibilitiesError(respError);
                return;
            }

            // Add new responsibility to the list
            setResponsibilities([
                ...responsibilities,
                { text: newResponsibility.trim(), checked: true },
            ]);
            setNewResponsibility(""); // Clear input field
            setShowInputField(false); // Hide input field
        }
    };
    return (
        <div className="py-11 px-6 Inter">
            <div className="flex items-center space-x-1">
                <h1 className="text-lg font-semibold">Responsibilities</h1>
            </div>
            <div className="flex flex-wrap gap-y-4">
                {responsibilities.map((responsibility, index) => (
                    <div key={index} className="flex items-center space-x-2 w-1/2 p-2">
                        {/* Checkbox and Label */}
                        <Checkbox
                            checked={responsibility.checked} // Use checked property of each responsibility
                            onCheckedChange={(isChecked) => handleCheckboxChange(index, isChecked === true)}
                        />
                        <span className="text-sm cursor-pointer truncate w-full">
                            {responsibility.text}
                        </span>
                    </div>
                ))}

                {/* Show input field for adding a new responsibility */}
                {showInputField && (
                    <div className="flex items-center space-x-2 w-1/2 p-2">
                        <Checkbox
                            checked={true} // Default to checked
                            disabled
                        />
                        <input
                            type="text"
                            value={newResponsibility}
                            onChange={handleInputChange}
                            onKeyDown={handleEnterPress}
                            placeholder="Responsibility name"
                            className="text-sm w-full p-2 border border-gray-300 rounded"
                        />
                    </div>
                )}
            </div>

            {/* Show error message */}
            {responsibilitiesError && (
                <p className="text-red-500 text-sm mt-2 ml-2 mb-4">{responsibilitiesError}</p>
            )}

            {/* Button to add a new responsibility */}
            <button
                className={`text-base font-normal hover:font-semibold ${responsibilities.length >= 25 || responsibilitiesError ? 'text-gray-400 cursor-not-allowed' : 'text-primary'}`}
                onClick={addNewResponsibility}
                disabled={responsibilities.length >= 25 || !!responsibilitiesError}
            >
                + Add New Responsibility
            </button>
        </div>
    );
};