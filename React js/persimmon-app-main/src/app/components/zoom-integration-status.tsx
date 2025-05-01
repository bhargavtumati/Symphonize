import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { Pencil } from "lucide-react";
import Image from "next/image";
import { Button } from "@/components/ui/button";

interface ZoomIntegrationStatusProps {
  zoomIntegrationStatus: (status: boolean) => void
}

export default function ZoomIntegrationStatus(ZoomIntegrationStatusProps: ZoomIntegrationStatusProps) {
  return (
    <Card className="my-4">
      <CardHeader className="flex justify-start">
        <Image
          src="/images/zoom.svg"
          height={100}
          width={100}
          alt="Zoom logo"
        />
      </CardHeader>
      <CardContent className="space-y-6">
        <p className="text-base font-medium text-slate-500">
          Manage your Zoom connection to schedule interviews seamlessly
        </p>
        <div className="flex items-center justify-between">
          <div className="flex gap-3">
            <Button
              variant="outline"
              className="flex items-center gap-2 text-sm font-medium"
              onClick={() => ZoomIntegrationStatusProps.zoomIntegrationStatus(false)}
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
