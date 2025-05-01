import Image from "next/image";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { ReactNode } from "react";
interface StepInstructionProps {
  stepNumber: number;
  description:  React.ReactNode
  imageSrc?: string;
  content ?: ReactNode
  

}

const StepInstruction: React.FC<StepInstructionProps> = ({ stepNumber, description, imageSrc, content}) => {
  return (
    <div className="space-x-2">
      <div className="space-x-2">
        <span className="w-4 h-4 rounded-full bg-primary text-white p-4 inline-flex items-center justify-center">
          {stepNumber}
        </span>
        <span className="text-base text-black">
          {description}
        </span>
      </div>
      {imageSrc && (
        <Image
          src={imageSrc}
          height={100}
          width={100}
          className="w-full h-full p-6"
          alt=""
        />
      )}
      {content && (
         <Card className="border rounded-xl mt-4 bg-[#E8F7FF]">
         <CardContent className="space-y-4">{content}</CardContent>
       </Card>
      )}

    </div>
  );
};

export default StepInstruction;
