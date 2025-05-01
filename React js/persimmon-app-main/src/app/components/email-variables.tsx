import { Button } from "@/components/ui/button"
import { variables } from "../utils/constants";



interface EmailVariablesProps {
  onVariableClick: (variable: string) => void
}

const EmailVariables: React.FC<EmailVariablesProps> = ({ onVariableClick }) =>  {
  return (
    <div className="flex h-full flex-col pr-2">
      <div className="px-4 py-2 font-bold text-base">Variables</div>
      <div className="space-y-1 p-2 overflow-y-auto">
        {variables.map((variable) => (
          <Button key={variable.id} variant="none" className="w-auto h-auto ml-6 p-1 font-normal flex justify-start text-xs bg-slate-100" size="sm" onClick={() => onVariableClick(`{{${variable.name}}}`)}>
            {`{{${variable.name}}}`}
          </Button>
        ))}
      </div>
    </div>
  )
}
export default EmailVariables;
