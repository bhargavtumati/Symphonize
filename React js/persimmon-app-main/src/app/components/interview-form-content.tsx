"use client"

import { useState, useEffect, useRef } from "react"
import { CalendarIcon } from "lucide-react"
import { format } from "date-fns"
import { FormField, FormItem, FormLabel, FormControl, FormMessage } from "@/components/ui/form"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { Calendar } from "@/components/ui/calendar"
import { TimePicker } from "../components/time-picker"
import { CustomSelect } from "@/components/filters/custom-select"
import { CustomDropdown } from "@/app/components/searchable-select"
import { apiService } from "../api/service"
import { toast } from "@/components/hooks/use-toast"
import type { UseFormReturn } from "react-hook-form"
import type { Applicant } from "../types/applicants"

// Constants moved from original file
const platforms = [
  { value: "google meet", label: "Google Meet" },
  { value: "ms teams", label: "MS Teams" },
  { value: "zoom", label: "Zoom" },
]

const interviewTypes = [
  { value: "ONLINE", label: "Online Interview" },
  { value: "FACE_TO_FACE", label: "Face to Face" },
  { value: "PHONE_CALL", label: "Phone Call" },
]
interface InterviewFormContentProps {
  form: UseFormReturn<any>
  interviewType: string
  applicantData?: Applicant
  TIME_ZONES: string[]
}
// This component contains just the form fields from the original component
export function InterviewFormContent({ form, interviewType, applicantData, TIME_ZONES }: InterviewFormContentProps) {
  const [showCalendar, setShowCalendar] = useState(false)
  const calendarRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (calendarRef.current && !calendarRef.current.contains(event.target as Node) && showCalendar) {
        setShowCalendar(false)
      }
    }

    document.addEventListener("mousedown", handleClickOutside)
    return () => {
      document.removeEventListener("mousedown", handleClickOutside)
    }
  }, [showCalendar])

  const getZoomUser = async (platFormName: any) => {
    if (platFormName == "zoom") {
      try {
        const response = await apiService(`/integration/${platFormName}/user`, "GET")
        console.log(response)
      } catch (error: any) {
        toast({
          variant: "destructive",
          title: "Error",
          description: error.message,
        })
      }
    }
  }

  return (
    <>
      <FormField
        control={form.control}
        name="fromEmail"
        render={({ field }) => (
          <FormItem  className="w-[436px]">
            <FormLabel className="text-sm font-medium career_bg_color_dark_mode">From</FormLabel>
            <Select
              onValueChange={(value) => {
                field.onChange(value)
                form.clearErrors("fromEmail")
              }}
              value={field.value}
            >
              <FormControl>
                <SelectTrigger>
                  <SelectValue placeholder="Select email" />
                </SelectTrigger>
              </FormControl>
              <SelectContent>
                <SelectItem value={field.value || sessionStorage.getItem("userEmail") || ""}>
                  {field.value || sessionStorage.getItem("userEmail")}
                </SelectItem>
              </SelectContent>
            </Select>
            <FormMessage />
          </FormItem>
        )}
      />

      <FormField
        control={form.control}
        name="toEmail"
        render={({ field }) => (
          <FormItem  className="w-[436px]">
            <FormLabel className="text-sm font-medium  career_bg_color_dark_mode">To</FormLabel>
            <FormControl>
              <Input
                {...field}
                value={field.value || applicantData?.details.personal_information.email || ""}
                onChange={(e) => {
                  field.onChange(e.target.value)
                  form.clearErrors("toEmail")
                }}
              />
            </FormControl>
            <FormMessage />
          </FormItem>
        )}
      />

      <FormField
        control={form.control}
        name="interviewerEmail"
        render={({ field }) => (
          <FormItem  className="w-[436px]" >
            <FormLabel className="text-sm font-medium">
              <span className="career_bg_color_dark_mode">CC</span>
              <span className="text-slate-500"> (Interviewer Email)</span>
            </FormLabel>
            <FormControl>
              <Input placeholder="Enter Email addresses (comma-separated)" {...field} />
            </FormControl>
            <FormMessage />
          </FormItem>
        )}
      />

      <FormField
        control={form.control}
        name="round"
        render={({ field }) => (
          <FormItem  className="w-[436px]">
            <FormLabel className="text-sm font-medium">
              <span className="career_bg_color_dark_mode">Subject</span>
              <span className="text-slate-500"> (Interview Title)</span>
            </FormLabel>
            <FormControl>
              <Input placeholder="Enter Interview Round or Title" {...field} />
            </FormControl>
            <FormMessage />
          </FormItem>
        )}
      />

      <div className="flex space-x-2 ">
        <FormField
          control={form.control}
          name="interviewType"
          render={({ field }) => (
            <FormItem >
              <FormLabel className="text-sm font-medium career_bg_color_dark_mode">Interview Type</FormLabel>
              <CustomSelect
                options={interviewTypes}
                placeholder="Select Interview Type"
                onValueChange={(value) => field.onChange(value)}
                triggerClassName={interviewType === "ONLINE"? "w-[209px]":"w-[436px]"}
                value={field.value}
              />
              <FormMessage />
            </FormItem>
          )}
        />

        {interviewType === "ONLINE" && (
          <FormField
            control={form.control}
            name="platform"
            render={({ field }) => (
              <FormItem className="flex-1">
                <FormLabel className="text-sm font-medium career_bg_color_dark_mode">Platform</FormLabel>
                <CustomSelect
                  options={platforms}
                  placeholder="Select Platform"
                  triggerClassName="w-[223px]"
                  onValueChange={(value) => {
                    field.onChange(value)
                    if (value === "zoom") {
                      getZoomUser(value)
                    }
                  }}
                  value={field.value}
                />
                <FormMessage />
              </FormItem>
            )}
          />
        )}
      </div>
      <FormLabel className="text-sm font-medium mt-2 career_bg_color_dark_mode">Interview Date</FormLabel>

      <div className="flex gap-4 ">
        <FormField
          control={form.control}
          name="date"
          render={({ field }) => (
            <FormItem>
              <div className="relative">
                <FormControl>
                  <div className="relative">
                    <Input
                      placeholder="Select date"
                      className="cursor-pointer"
                      value={field.value ? format(field.value, "PPP") : ""}
                      onClick={() => setShowCalendar(true)}
                      readOnly
                    />
                    <button
                      type="button"
                      onClick={(e) => {
                        e.stopPropagation()
                        setShowCalendar(true)
                      }}
                      className="absolute right-3 top-1/2 -translate-y-1/2 h-4 w-4 opacity-50 hover:opacity-100"
                    >
                      <CalendarIcon className="h-4 w-4" />
                      <span className="sr-only">Open calendar</span>
                    </button>
                  </div>
                </FormControl>

                {showCalendar && (
                  <div
                    ref={calendarRef}
                    className="absolute bottom-full left-0 mb-2 z-50 bg-popover p-3 rounded-md shadow-md"
                  >
                    <Calendar
                      mode="single"
                      selected={field.value}
                      onSelect={(date) => {
                        field.onChange(date) 
                        setShowCalendar(false)                  
                      }}
                      disabled={(date) => date < new Date() || date < new Date("1900-01-01")}
                      initialFocus
                    />
                  </div>
                )}
              </div>
              <FormMessage />
            </FormItem>
          )}
        />

        <div className="flex space-x-2">
          <FormField
            control={form.control}
            name="timezone"
            render={({ field }) => (
              <FormItem className="flex-1">
                <FormControl>
                  <CustomDropdown
                    options={TIME_ZONES}
                    value={field.value}
                    onChange={field.onChange}
                    placeholder="Select timezone"
                  
                  />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />

          <div className="flex gap-2">
            <FormField
              control={form.control}
              name="fromTime"
              render={({ field }) => (
                <FormItem>
                  <FormControl>
                    <TimePicker placeholder="From" {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="toTime"
              render={({ field }) => (
                <FormItem>
                  <FormControl>
                    <TimePicker placeholder="To" {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
          </div>
        </div>
      </div>

      <FormField
        control={form.control}
        name="description"
        render={({ field }) => (
          <FormItem>
            <FormLabel className="text-sm font-medium career_bg_color_dark_mode">Description</FormLabel>
            <FormControl>
              <Textarea placeholder="Type here" className="resize-none" {...field} />
            </FormControl>
            <FormMessage />
          </FormItem>
        )}
      />
    </>
  )
}

