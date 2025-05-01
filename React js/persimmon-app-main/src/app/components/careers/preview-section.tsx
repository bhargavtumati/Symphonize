"use client"

import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { CareerPagePreview } from "@/app/components/careers/career-page-preview"
import { JobPagePreview } from "@/app/components/careers/job-page-preview"
import type { CustomizationSettings } from "@/app/types/customization"

interface PreviewSectionProps {
  settings: CustomizationSettings
  domain: string
}

export function PreviewSection({ settings, domain }: PreviewSectionProps) {
  return (
    <div className="space-y-4 w-full">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center">
        <Tabs defaultValue="career" className="w-full bg-inherit">
          <div className="flex flex-col sm:flex-row sm:items-center w-full gap-2 sm:gap-4">
            <h2 className="text-lg font-semibold mt-4">Preview</h2>
            <div className="w-full sm:w-[300px] rounded-md bg-muted p-1 text-muted-foreground sm:ml-auto">
              <TabsList className="grid w-full grid-cols-2">
                <TabsTrigger value="career">Career page</TabsTrigger>
                <TabsTrigger value="job">Job</TabsTrigger>
              </TabsList>
            </div>
          </div>
          <TabsContent value="career" className="mt-4 w-full overflow-hidden">
            <div className="w-full">
              <CareerPagePreview settings={settings} domain={domain} />
            </div>
          </TabsContent>
          <TabsContent value="job" className="mt-4 w-full overflow-hidden">
            <div className="w-full">
              <JobPagePreview settings={settings} />
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  )
}