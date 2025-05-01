import { JobCardProps } from "@/app/types";
import { Card } from "@/components/ui/card";

export const AiClarifyingQuestions: React.FC<JobCardProps> = ({ job }) => {
    return (
      <Card className="rounded-lg px-6 py-4  border-none">
        <h2 className="text-lg font-medium text-slate-800 mb-4">AI Clarifying Questions</h2>
  
        <div className="space-y-4">
          { job.ai_clarifying_questions.length > 0  ? (job.ai_clarifying_questions.map((question, index) => (
            <div key={index} className="text-gray-700">
              <p className="text-base text-slate-600 leading-7 mb-1">
                {index + 1}. {question.question}
              </p>
              <p className="ml-5 text-slate-800 font-semibold text-base">
                {question.answer || "No answer provided"}
              </p>
            </div>
          ))):(<p className="text-base text-slate-600 leading-6 font-medium">No questions available</p>)}
        </div>
      </Card>
    );
  };