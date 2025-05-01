"use client"

import type React from "react"
import { useState, useRef, useEffect } from "react"
import { Card } from "@/components/ui/card"
import { Label } from "@/components/ui/label"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { Check, ImagePlus } from "lucide-react"
import type { CustomizationSettings } from "@/app/types/customization"
import { useOtpless } from "@/app/components/careers/useOtpless"
import { validateEmail, validateFullName, validateLinkedIn, validateWhatsAppNumber } from "@/app/utils/validations"
import ReCAPTCHA from "react-google-recaptcha"
import type { Job } from "@/app/connection/[company]/model"
import FormField from "./FormInput"
import AnimationDialog from "../AnimationDialog"
import { cn } from "@/lib/utils"

type JobApplicationProps = {
  formRef: React.RefObject<HTMLDivElement>
  settings: CustomizationSettings | null
  selectedJob: {
    job: Job | null
  }
}

const JobApplicationForm: React.FC<JobApplicationProps> = ({ formRef, settings, selectedJob }) => {
  const [phoneNumber, setPhoneNumber] = useState("");
  const [otp, setOtp] = useState("");
  const [showOtpInput, setShowOtpInput] = useState(false);
  const [pdfFile, setPdfFile] = useState<File | null>(null);
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [linkedInProfile, setLinkedInProfile] = useState("");
  const [errors, setErrors] = useState<{ [key: string]: string }>({});
  const [captchaValue, setCaptchaValue] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [canResendOtp, setCanResendOtp] = useState(false);
  const [resendTimer, setResendTimer] = useState(0);
  const [showErrors, setShowErrors] = useState(false);
  const [isParsing, setIsParsing] = useState(false);
  const [isSuccess, setIsSuccess] = useState(false);
  const [isFailure, setIsFailure] = useState(false);
  const [showDialog, setShowDialog] = useState(false);
  const [localVerified, setLocalVerified] = useState(false);
  const [showNumberError, setShowNumberError] = useState(false);
  const [showMessage, setShowMessage] = useState(false);
  const [tokenExpired, setTokenExpired] = useState(false);
  const { jwtToken, isVerified, error, initiateOtp, verifyOtp, setIsVerified, setJwtToken } = useOtpless();


  useEffect(() => {
    setShowOtpInput(false)
    setPdfFile(null)
    setLocalVerified(false)
    setOtp("")
    setIsVerified(false)
    setJwtToken("")
    setErrors({ ...errors, otp: "" })
  }, [selectedJob])

  useEffect(() => {
    if (jwtToken) {
      localStorage.setItem("otplessJwtToken", jwtToken);
      setShowMessage(true);
      const timer = setTimeout(() => {
        setShowMessage(false);
      }, 5000); // Hide message after 5 seconds

      return () => clearTimeout(timer); // Cleanup the timer when the component unmounts or jwtToken changes
    }
  }, [jwtToken]);
  useEffect(() => {
    let timer: NodeJS.Timeout
    if (resendTimer > 0) {
      timer = setTimeout(() => setResendTimer(resendTimer - 1), 1000)
    } else if (resendTimer === 0) {
      setCanResendOtp(true)
    }
    return () => clearTimeout(timer)
  }, [resendTimer])

  const handlePhoneAuth = () => {
    const errorMessage = validateWhatsAppNumber(phoneNumber)
    if (errorMessage === "") {
      initiateOtp(phoneNumber)
      setShowOtpInput(true)
      setCanResendOtp(false)
      setResendTimer(30)
      setLocalVerified(true)
      setShowNumberError(false)
      setErrors({ ...errors, phoneNumber: "" })
    } else {
      setShowNumberError(true);
      setErrors({ ...errors, phoneNumber: errorMessage })
    }
  }

  const handleVerifyOTP = async () => {
    if (otp.length === 4) {
      try {
        await verifyOtp(phoneNumber, otp);
        await new Promise((resolve) => setTimeout(resolve, 2000));
        if (jwtToken) {
          setErrors({ ...errors, otp: "" });
        }
        else {
          setErrors({ ...errors, otp: "Enter a valid OTP." });
        }
      } catch (error) {
        setErrors({ ...errors, otp: "Enter a valid OTP." });
      }
    } else {
      setErrors({ ...errors, otp: "Enter a valid OTP" })
    }
  }

  const handleResendOTP = () => {
    if (canResendOtp) {
      initiateOtp(phoneNumber)
      setCanResendOtp(false)
      setResendTimer(30)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setShowErrors(true);
    if (!captchaValue) {
      setErrors({ ...errors, captcha: "Please complete the CAPTCHA." });
      return;
    }

    if (validateForm()) {
      try {
        setIsParsing(true);
        setShowDialog(true);
        // Build the query parameters
        const queryParams = new URLSearchParams({
          job_id: `${selectedJob.job?.id}`,
          job_code: `${selectedJob.job?.code}`,
          phone_number: phoneNumber,
          full_name: fullName,
          email_id: email,
          linkedin_url: linkedInProfile,
        }).toString();
        const apiUrl = `${process.env.NEXT_PUBLIC_API}api/v1/applicants/career-page?${queryParams}`;

        // Ensure a PDF file is selected
        if (!pdfFile) {
          setErrors({ ...errors, pdf: "Please upload a PDF file." });
          return;
        }

        // Validate the file type (only accept PDF files)
        if (pdfFile.type !== "application/pdf") {
          setErrors({ ...errors, pdf: "Only PDF files are allowed." });
          return;
        }

        // Prepare the FormData object
        const formData = new FormData();
        formData.append("file", pdfFile, pdfFile.name);

        // Get the JWT token from localStorage
        const localJwtToken = localStorage.getItem("otplessJwtToken");

        // Make the API request
        const response = await fetch(apiUrl, {
          method: "POST",
          headers: {
            token: localJwtToken || "",
          },
          body: formData,
        });

        setIsParsing(false);

        // Handle different response statuses
        if (response.status === 200 || response.status === 201) {
          setIsSuccess(true);
          setErrors({}); // Clear any previous errors
          return;
        }

        if (response.status === 401) {
          setTokenExpired(true);
          return;
        }

        setIsFailure(true);
      } catch (error) {
        console.error("Error submitting form:", error);
        setErrors({ ...errors, api: "Failed to submit form. Please try again later." });
        setIsFailure(true);
      }
    }
  };


  const validateForm = (): boolean => {
    const newErrors: { [key: string]: string } = {}

    newErrors.fullName = validateFullName(fullName)
    newErrors.email = validateEmail(email)
    newErrors.linkedInProfile = validateLinkedIn(linkedInProfile)

    if (!pdfFile) newErrors.resume = "Please upload a resume"

    setErrors(newErrors)
    return Object.values(newErrors).every((error) => error === "")
  }

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      if (file.type === "application/pdf" && file.size <= 2 * 1024 * 1024) {
        setPdfFile(file);
        setErrors({ ...errors, resume: "" });
      } else if (file.type !== "application/pdf") {
        setErrors({ ...errors, resume: "Please select a PDF file." });
      } else {
        setErrors({ ...errors, resume: "File size exceeds 2MB." });
      }
    }
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
  };

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    const file = e.dataTransfer.files[0];
    if (file) {
      if (file.type === "application/pdf" && file.size <= 2 * 1024 * 1024) {
        setPdfFile(file);
        setErrors({ ...errors, resume: "" });
      } else if (file.type !== "application/pdf") {
        setErrors({ ...errors, resume: "Please drop a PDF file." });
      } else {
        setErrors({ ...errors, resume: "File size exceeds 2MB." });
      }
    }
  };


  const handleValidation = (id: string, error: string) => {
    setErrors((prevErrors) => ({
      ...prevErrors,
      [id]: error,
    }))
  }

  const handleCloseDialog = () => {
    setShowDialog(false)
    setIsParsing(false)
    setIsSuccess(false)
    setIsFailure(false)
    setShowErrors(false)
    setOtp("")
    setShowOtpInput(false)
    setPdfFile(null)
    setErrors({})
    setCaptchaValue(null)
    setCanResendOtp(false)
    setResendTimer(0)
    setLocalVerified(false)
    setIsVerified(false)
    setJwtToken("")
    setTokenExpired(false)
  }

  const isFormValid = () => {
    return (
      (isVerified || localVerified) &&
      fullName.trim() !== "" &&
      email.trim() !== "" &&
      linkedInProfile.trim() !== "" &&
      pdfFile !== null &&
      captchaValue !== null
    )
  }

  return (
    <div ref={formRef} className="mt-6">
      <Card className={cn(
        settings?.darkMode ? "bg-slate-800 text-slate-200" : "bg-[#f8fafc]",
        "border-none p-4"
      )}
        style={{ fontFamily: settings?.fontStyle }}>
        <h2 className="text-lg font-semibold mb-4">Apply For the Job</h2>
        <form className="space-y-4" onSubmit={handleSubmit}>
          {/* Phone Number Input */}
          <div className="flex gap-4 w-full">
            <div className="w-full lg:w-1/2 pr-2">
              <Label htmlFor="phone">Phone number</Label>
              <div className="relative">
                <Input
                  id="phone"
                  value={phoneNumber}
                  onChange={(e) => {
                    const value = e.target.value.replace(/[^0-9]/g, "");
                    setPhoneNumber(value);
                  }}
                  placeholder="Enter 10 digit number"
                  className={cn("pr-20", settings?.darkMode && "border-white", "border")}
                  type="text"
                />

                {isVerified ? (
                  <Check
                    className="absolute top-1/2 right-0.5 -translate-y-1/2 whitespace-nowrap h-8"
                    style={{ color: settings?.primaryColor || "black" }}
                  />
                ) : (
                  <Button
                    type="button"
                    onClick={handlePhoneAuth}
                    style={{ backgroundColor: settings?.primaryColor }}
                    className="absolute top-1/2 right-0.5 -translate-y-1/2 whitespace-nowrap h-8"
                    disabled={localVerified || phoneNumber.length < 10}
                  >
                    Send OTP
                  </Button>
                )}
              </div>
              {showNumberError && errors.phoneNumber && <p className="text-red-500 mt-1">{errors.phoneNumber}</p>}
            </div>
          </div>

          {/* OTP Input */}
          {showOtpInput && !(isVerified) && (
            <div>
              <Label htmlFor="otp">Enter OTP</Label>
              <div className="flex gap-2">
                <Input id="otp" value={otp} onChange={(e) => setOtp(e.target.value)} placeholder="Enter OTP" className={cn("pr-20", settings?.darkMode && "border-white", "border")}
                />
                <Button type="button" onClick={handleVerifyOTP} style={{ backgroundColor: settings?.primaryColor }} disabled={otp.length < 4}>
                  Verify OTP
                </Button>
              </div>
              {errors.otp && <p className="text-red-500 mt-1">{errors.otp}</p>}
              <button
                type="button"
                onClick={handleResendOTP}
                className={`text-sm mt-2 ${canResendOtp ? "text-blue-600 hover:underline" : "text-gray-400"}`}
                disabled={!canResendOtp}
              >
                {canResendOtp ? "Resend OTP" : `Resend OTP in ${resendTimer}s`}
              </button>
            </div>
          )}

          {/* Success Message */}
          {showMessage && <p className="text-green-500 mt-2">Mobile number verified successfully.</p>}

          {/* Other Fields */}
          <div className="grid md:grid-cols-2 gap-4">
            <div>
              <FormField
                label="Full Name"
                id="fullName"
                type="text"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                placeholder="Enter your name"
                error={errors.fullName}
                validate={validateFullName}
                onValidation={handleValidation}
                showError={showErrors}
                settings={settings}
              />
            </div>
            <div>
              <FormField
                label="Email ID"
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="Enter your email"
                error={errors.email}
                validate={validateEmail}
                onValidation={handleValidation}
                showError={showErrors}
                settings={settings}
              />
            </div>
          </div>

          <div>
            <FormField
              label="LinkedIn Profile"
              id="linkedInProfile"
              type="text"
              value={linkedInProfile}
              onChange={(e) => setLinkedInProfile(e.target.value)}
              placeholder="Enter LinkedIn Profile URL"
              error={errors.linkedInProfile}
              validate={validateLinkedIn}
              onValidation={handleValidation}
              showError={showErrors}
              settings={settings}
            />
          </div>

          <div>
            <Label>Resume</Label>
            <div
              className={cn(
                "border-2 border-dashed rounded-lg p-6 text-center",
                settings?.darkMode && "border-white"
              )}
              onDragOver={handleDragOver}
              onDrop={handleDrop}
              onClick={() => fileInputRef.current?.click()}
            >
              <ImagePlus className="h-8 w-8 mx-auto mb-2 text-muted-foreground" />
              <p className="text-sm text-muted-foreground mb-1">
                {pdfFile ? `Selected file: ${pdfFile.name}` : "Choose a file or Drag and Drop here"}
              </p>
              <p className="text-xs text-muted-foreground">PDF files only</p>
              <input
                type="file"
                ref={fileInputRef}
                onChange={handleFileChange}
                accept=".pdf"
                style={{ display: "none" }}
              />
            </div>
            {errors.resume && <p className="text-red-500 mt-1">{errors.resume}</p>}
          </div>

          <div>
            <ReCAPTCHA
              sitekey={process.env.NEXT_PUBLIC_RECAPTCHA_SITE_KEY || ""}
              onChange={(value) => {
                setCaptchaValue(value)
                setErrors({ ...errors, captcha: "" })
              }}
            />
            {showErrors && errors.captcha && <p className="text-red-500 mt-1">{errors.captcha}</p>}
          </div>

          <Button
            type="submit"
            className="w-full"
            style={{ backgroundColor: settings?.primaryColor }}
          //disabled={!(isVerified || localVerified) || isParsing || !isFormValid()}
          >
            {isParsing ? "Submitting..." : "Submit"}
          </Button>
        </form>
      </Card>
      {showDialog && (
        <AnimationDialog
          isParsing={isParsing}
          isSuccess={isSuccess}
          isFailure={isFailure}
          tokenExpired={tokenExpired}
          onClose={handleCloseDialog}
          parsingMessage="Processing your application..."
          successMessage="Your application has been successfully submitted!"
          failureMessage="We encountered an issue while submitting your application. Please try again."
          settings={settings}
        />
      )}
    </div>
  )
}

export default JobApplicationForm

