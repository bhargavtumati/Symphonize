"use client"
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { Pencil } from "lucide-react";
import Image from "next/image";
import { Button } from "@/components/ui/button";
import { ReactNode } from "react";
interface integrationStatusprops{
  imageSrc: string;
  description:ReactNode;
  editPath?: string;
  handleEditClick?:()=>void
}

export default function IntegrationStatus({imageSrc,description ,handleEditClick} :integrationStatusprops) {
  return (
    <Card className="my-4">
      <CardHeader className="flex justify-start">
        <Image
          src={imageSrc}
          height={100}
          width={100}
          alt="logo"
        />
      </CardHeader>
      <CardContent className="space-y-6">
        <p className="text-base font-medium text-slate-500">
         {description}
        </p>
        <div className="flex items-center justify-between">
          <div className="flex gap-3">
            <Button
              variant="outline"
              className="flex items-center gap-2 text-sm font-medium"
              onClick={handleEditClick}
            >
              <Pencil className="h-4 w-4" strokeWidth={1.5} />
              Edit
            </Button>
            <Button variant="outline" className="text-sm font-medium">
              Disconnect
            </Button>
          </div>
          <div className="flex items-center gap-2">
            <div className="h-2 w-2 rounded-full bg-green-600" />
            <span className="text-sm font-medium">Active</span>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
