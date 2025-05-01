import { applicantsPreferedData } from "@/app/types/model";
import { IRemunerationFC } from "@/components/filters/models";
import { validateCompareSalaries } from "@/app/utils/validations";
import { useEffect } from "react";
import SalaryRangeFilter from "@/components/filters/remuneration-items";
import { filterconfig } from "@/app/utils/filters/config";

export const FilterByRemuneration: React.FC<IRemunerationFC> = ({ remuneration, setRemuneration, checked, setChecked, setErrorMessage }) => {
    const remunerationRange = filterconfig.remunration.remunerationRange;
    useEffect(() => {
        if (checked) {
            applicantsPreferedData.filters.remuneration = {
                name: "Salary Range",
                min: remuneration.min_value,
                max: remuneration.max_value,
            }
        } else {
            applicantsPreferedData.filters.remuneration = {
                name: "",
                min: 0,
                max: 0,
            };
        }
    }, [checked, remuneration])



    // Single remuneration object
    const addToFilter = () => {
        setChecked(!checked)
    }
    const onSliderValueChange = (value: number[]) => {
        if (value.length === 2) {
            handleValueChange([value[0], value[1]]);
        }
    };
    const handleValueChange = (newRange: [number, number]) => {
        const min = Math.min(
            newRange[0] === remunerationRange
                ? remunerationRange - 1
                : newRange[0],
            newRange[1] - 1
        );
        const max = newRange[0] === remunerationRange
            ? remunerationRange
            : Math.max(newRange[1], newRange[0] + 1);

        setRemuneration({ ...remuneration, min_value: min, max_value: max });
    };

    const handleMaxInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        let value = parseInt(e.target.value, 10);
        value = Math.min(Math.max(value, 2), remunerationRange);
        const errorMessage = validateCompareSalaries(remuneration?.min_value, value);
        setErrorMessage((prev)=>({...prev,remuneration:errorMessage}));
        setRemuneration({ ...remuneration, max_value: value, errorMessage });
    };

    const handleMinInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        let value = parseInt(e.target.value, 10);
        value = Math.min(Math.max(value, 1), remunerationRange-1);
        const errorMessage = validateCompareSalaries(value, remuneration.max_value);
        setErrorMessage((prev)=>({...prev,remuneration:errorMessage}));

        setRemuneration({ ...remuneration, min_value: value, errorMessage });
    };

    const getPosition = (value: number) => {
        return (value / remunerationRange) * 100;
    };

    return (
        <div className="py-11 px-6 Inter">
            <div className="flex items-center space-x-1">
                <h1 className="text-lg font-semibold">CTC</h1>
                <span className="text-sm font-normal text-slate-500">(in LPA)</span>
            </div>
            <div>
                <SalaryRangeFilter
                    remuneration={remuneration}
                    remunerationRange={remunerationRange}
                    checked={checked}
                    addToFilter={addToFilter}
                    handleMinInputChange={handleMinInputChange}
                    handleMaxInputChange={handleMaxInputChange}
                    handleValueChange={onSliderValueChange}
                    getPosition={getPosition}
                />
                {remuneration.errorMessage && (
                    <div className="ml-4">
                        <p className="text-red-500 text-xs mr-4">{remuneration.errorMessage}</p>
                    </div>
                )}
            </div>
        </div>
    );
};