"use client";

import { useEffect, useState } from "react";
import { Loader2, MailPlus } from "lucide-react";
import { format } from "date-fns";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";
import type React from "react";
import { TIME_ZONES } from "../utils/constants";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Form } from "@/components/ui/form";
import { apiService } from "../api/service";
import { usePathname } from "next/navigation";
import { toast } from "@/components/hooks/use-toast";
import type { Applicant } from "../types/applicants";
import { InterviewFormContent } from "@/app/components/interview-content-form"; // Import the extracted component
import { useRouter } from "next/navigation";
import { cn } from "@/lib/utils";
import Image from "next/image";
import { emailSchema } from "../utils/emailValidation";

const formSchema = z.object({
  fromEmail: z.string().email("Invalid email address"),
  toEmail: z.string().email("Invalid email address"),
  interviewType: z.enum(["ONLINE", "FACE_TO_FACE", "PHONE_CALL"]),
  platform: z.string().optional(),
  date: z.date(),
  timezone: z.string(),
  fromTime: z.string().min(1, "From time is required"),
  toTime: z.string().min(1, "To time is required"),
  round: z.string().min(1, "Interview title is required"),
  interviewerEmail: z
    .string()
    .min(1, "Interviewer email is required.")
    .transform((val) => val.split(",").map((email) => email.trim()))
    .refine((emails) => emails.length > 0 && emails[0] !== "", {
      message: "Interviewer email is required.",
    })
    .refine(
      (emails) =>
        emails.every((email) => {
          const emailCheck = z.string().email().safeParse(email);
          return emailCheck.success || email === "";
        }),
      { message: "Please enter valid email addresses." }
    ),
  description: z.string().min(1, "Description is required"),
});

type FormValues = z.infer<typeof formSchema>;

interface ScheduleInterviewDialogProps {
  children: React.ReactNode;
  applicantData?: Applicant;
  onScheduleClick: () => Promise<{
    emailServiceStatus: boolean;
    indidualEmailServiceStatus: boolean;
  } | null>;
  verifyingEmailService: boolean;
}

export function ScheduleInterviewDialog({
  children,
  applicantData,
  onScheduleClick,
  verifyingEmailService,
}: ScheduleInterviewDialogProps) {
  const getDefaultTimezone = () => {
    const systemTimezone = Intl.DateTimeFormat().resolvedOptions().timeZone;
    return TIME_ZONES.includes(systemTimezone) ? systemTimezone : "";
  };

  const [open, setOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [showCalendar, setShowCalendar] = useState(false);
  const [emailServiceStatus, setEmailServiceStatus] = useState(true);
  const [indidualEmailServiceStatus, setIndidualEmailServiceStatus] =
    useState(true);

  const router = useRouter();
  const form = useForm<FormValues>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      fromEmail: "",
      toEmail: applicantData?.details.personal_information.email || "",
      description: "",
      round: "",
      interviewerEmail: [],
      fromTime: "",
      toTime: "",
      timezone: getDefaultTimezone(),
    },
    mode: "onSubmit", // Only validate on submit
  });

  const interviewType = form.watch("interviewType");
  const pathname = usePathname();

  const handleScheduleClick = async () => {
    const result = await onScheduleClick();
    if (result) {
      setEmailServiceStatus(result.emailServiceStatus);
      setIndidualEmailServiceStatus(result.indidualEmailServiceStatus);
      setOpen(true);
    }
  };

  useEffect(() => {
    try {
      console.log("this main call right");
      const verifyEmailService = async () => {
        const verifiedValue = await apiService(
          `/integration/email/verify-from-address`,
          "GET",
          null
        );
        if (!verifiedValue) {
          toast({
            variant: "destructive",
            title: "Email service not verified",
            description:
              "Please verify your email service before scheduling an interview",
          });
        }
        if (verifiedValue.message === "Email Integration details not found") {
          setEmailServiceStatus(verifiedValue.data);
        } else if (
          verifiedValue.message ===
          "Your email not found within any integrated email service, please contact your administrator"
        ) {
          setIndidualEmailServiceStatus(verifiedValue.data);
        } else {
          setEmailServiceStatus(verifiedValue.data);
          setIndidualEmailServiceStatus(verifiedValue.data);
        }
      };
      verifyEmailService();
    } catch (error) {}
  }, []);

  useEffect(() => {
    const email = sessionStorage.getItem("userEmail");
    if (email) {
      form.setValue("fromEmail", email, {
        shouldValidate: false,
        shouldDirty: false,
      });
    }

    if (applicantData?.details.personal_information.email) {
      form.setValue(
        "toEmail",
        applicantData.details.personal_information.email,
        {
          shouldValidate: false,
          shouldDirty: false,
        }
      );
    }
  }, [applicantData?.details.personal_information.email, form]);

  const onSubmit = async (data: FormValues) => {
    try {
      setLoading(true);

      // Validate required fields before submission
      if (!data.fromEmail || !data.toEmail) {
        toast({
          variant: "destructive",
          title: "Error",
          description: "Please fill in all required fields",
        });
        return;
      }
      const recruiterEmail = sessionStorage.getItem("userEmail");
      const payload = {
        agenda: data.description,
        allow_multiple_devices: true,
        schedule_for: recruiterEmail,
        settings: {
          meeting_authentication: true,
          meeting_invitees: data.interviewerEmail.map((email) => ({ email })),
          push_change_to_calendar: true,
        },
        start_time: `${format(data.date, "yyyy-MM-dd")}T${data.fromTime}:00`,
        timezone: data.timezone,
        topic: data.round,
      };

      const endTime = `${format(data.date, "yyyy-MM-dd")}T${data.toTime}:00`;
      const userId = recruiterEmail;
      const idMatch = pathname?.match(/\/all-applicants\/([^/]+)/);
      const id = idMatch ? idMatch[1] : null;
      const interviewType = data.interviewType;

      const response = await apiService(
        `/applicants/${id}/create-meeting?platform_name=${
          data.platform
        }&user_id=${userId}&end_time=${encodeURIComponent(
          endTime
        )}&interview_type=${interviewType}&from_address=${data.fromEmail}`,
        "POST",
        payload
      );

      if (!response) {
        throw new Error("API call failed");
      }
      console.log(response);

      form.reset();
      form.clearErrors();
      setOpen(false);
      toast({
        variant: "default",
        title: "Your interview has been scheduled successfully.",
      });
    } catch (error: any) {
      toast({
        variant: "destructive",
        title: "Error",
        description: error.message || "Failed to schedule interview",
      });
    } finally {
      setLoading(false);
    }
  };

  /**
   * Resets the form state to its default values
   * and sets showCalendar to false
   */

  const resetForm = () => {
    form.reset({
      fromEmail: "",
      toEmail: applicantData?.details.personal_information.email || "",
      description: "",
      round: "",
      interviewerEmail: [],
      fromTime: "",
      toTime: "",
      timezone: getDefaultTimezone(),
    });
    setShowCalendar(false);
  };

  const useOurOwnService = () => {
    const email = process.env.NEXT_PUBLIC_EMAIL_SERVICE_ACCOUNT || "";
    form.setValue("fromEmail", email);
    if (applicantData?.details.personal_information.email) {
      form.setValue(
        "toEmail",
        applicantData.details.personal_information.email,
        {
          shouldValidate: false,
          shouldDirty: false,
        }
      );
    }

    setEmailServiceStatus(true);
    setIndidualEmailServiceStatus(true);
  };

  const navigateEmailIntegrationPage = () => {
    router.push("/integrations");
  };

  return (
    <Dialog
      open={open}
      onOpenChange={(newOpen) => {
        setOpen(newOpen);
        if (!newOpen) {
          // Reset form when dialog is closed
          resetForm();
        }
      }}
    >
      <DialogTrigger asChild>
        <div onClick={handleScheduleClick}>{children}</div>
      </DialogTrigger>

      <DialogContent
        className={cn(
          !emailServiceStatus ? "max-w-[600px]" : "sm:max-w-[730px]",
          "max-h-[95vh] overflow-y-auto"
        )}
      >
        {verifyingEmailService ? (
          <div className="flex flex-col items-center justify-center h-64">
            <Loader2 className="h-8 w-8 animate-spin text-primary" />
            <p className="mt-4 text-sm text-gray-500">
              Verifying email service...
            </p>
          </div>
        ) : !emailServiceStatus || !indidualEmailServiceStatus ? (
          <>
            <div className="flex flex-col items-center justify-center space-y-4 py-10 px-8">
              {!emailServiceStatus && (
                <>
                  {" "}
                  <Image
                    src={"/images/email-integration.svg"}
                    alt={""}
                    height={100}
                    width={100}
                  />
                  <h1 className="text-xl font-bold text-slate-800">
                    Email Not Integrated
                  </h1>
                  <p className="text-base text-slate-500 font-medium text-center">
                    You haven{"'"}t integrated your company email yet. The email
                    would be persimmon email Id, integrate your companies email
                    Id for professional experience to your receipts.
                  </p>
                  <Button onClick={navigateEmailIntegrationPage}>
                    <MailPlus /> Integrate email
                  </Button>
                  <a
                    onClick={useOurOwnService}
                    className="cursor-pointer text-primary"
                  >
                    Continue with persimmon email (0/100)
                  </a>
                </>
              )}
            </div>
            {!indidualEmailServiceStatus && (
              <div className="flex flex-col items-center justify-center space-y-4">
                <p className="text-xl text-slate-800 p-8">
                  Your email not found within any integrated email service,
                  please contact your administrator
                </p>
              </div>
            )}
          </>
        ) : (
          <>
            <DialogHeader className="flex flex-row items-center justify-between">
              <DialogTitle className="text-base font-semibold">
                Schedule Interview
              </DialogTitle>
            </DialogHeader>
            <Form {...form}>
              <form
                onSubmit={form.handleSubmit(onSubmit)}
                className="space-y-4"
              >
                {/* Use the extracted component here */}
                <InterviewFormContent
                  form={form}
                  interviewType={interviewType}
                  applicantData={applicantData}
                  TIME_ZONES={TIME_ZONES}
                />

                <div className="flex justify-end">
                  <Button type="submit" disabled={loading}>
                    {loading ? "Sending..." : "Send"}
                  </Button>
                </div>
              </form>
            </Form>
          </>
        )}
      </DialogContent>
    </Dialog>
  );
}
