import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { useRouter } from "next/navigation";



type ResetChangesProps = {
    backToApplicants:()=>void;
    applyFilters:(jobId: string, router: any, jobCode: string) => Promise<void>;
    hasErrors:boolean;
    jobId:string;
    jobCode:string;
    resetChanges:boolean;
    setResetChanges: React.Dispatch<React.SetStateAction<boolean>>;
}

const ResetChanges: React.FC<ResetChangesProps> = ({ backToApplicants, applyFilters, hasErrors, jobId, jobCode,resetChanges, setResetChanges }) => {
    const router = useRouter();
    const resetFilter = () => {
        setResetChanges(prevState => !prevState);
    }
    return(
        <div className="h-[88px] mt-0 min-h-[44px] mb-[50px]">
        <Card className="w-full h-full flex flex-col justify-center border-0 border-t border-slate-300 rounded-none rounded-br-lg rounded-bl-lg">
            <div className="flex justify-between items-center my-1 text-primary pl-9">
                {/* Left-aligned text */}
                <button type="button" onClick={resetFilter}>Reset Changes</button>
                {/* Right-aligned buttons */}
                <div className="flex items-center">
                    <Button variant="outline" className="mr-2" onClick={backToApplicants}>Cancel</Button>
                    <Button
                        onClick={() => applyFilters(jobId, router, jobCode)}
                        className={`mr-8 bg-primary hover:bg-primary ${hasErrors ? 'opacity-50 cursor-not-allowed' : ''}`}
                        disabled={hasErrors}
                    >
                        Apply
                    </Button>
                </div>
            </div>
        </Card>
    </div>
    )
}
export default ResetChanges

