"use client";
import { useState, useEffect } from "react";
import { sendEmailVerification } from "firebase/auth";
import { auth } from "../../components/firebaseConfig"; // Adjust the path as necessary
import Image from "next/image";
import { AuthSlider } from "@/app/components/slider";
import EmailSentToast from "@/app/components/EmailSentToast";
import ForgotPassword from "../forgot-password/page";

export default function Verification() {
  const [emailSent, setEmailSent] = useState(false);
  const [error, setError] = useState("");
  const [isResendDisabled, setIsResendDisabled] = useState(true); // Start disabled by default
  const [timer, setTimer] = useState(60); // Start with 60 seconds timer
  const [isForgotPassword, setIsForgotPassword] = useState(false);

  useEffect(() => {
    // Check the query parameter to see where the user came from
    const queryParams = new URLSearchParams(window.location.search);
    const pageType = queryParams.get("pageType");
    setIsForgotPassword(pageType ==="forgot-password");
  }, []);


  // Function to handle email resend and reset the timer
  const resendVerificationEmail = async () => {
    setError("");
    try {
      if (auth.currentUser) {
        await sendEmailVerification(auth.currentUser, {
          url: "https://persimmon-ui.storage.googleapis.com?typeOfPage=create-password&email",
          handleCodeInApp: true,
        });
        setEmailSent(true);
        setIsResendDisabled(true);
        setTimer(60); // Reset timer to 60 seconds
      } else {
        setError("No current user found. Please log in and try again.");
      }
    } catch (err) {
      setError("Failed to resend verification email. Please try again later.");
    }
  };

  // Effect to handle the countdown timer
  useEffect(() => {
    if (timer > 0) {
      const countdown = setTimeout(() => {
        setTimer(timer - 1); // Decrease the timer by 1 every second
      }, 1000);

      // Cleanup timeout on unmount or when timer reaches 0
      return () => clearTimeout(countdown);
    } else if (timer === 0) {
      setIsResendDisabled(false); // Enable the resend button once the timer reaches 0
    }
  }, [timer]);

  // Effect to start the timer when the page is loaded (via routing or refreshing)
  useEffect(() => {
    setTimer(60); // Initialize the timer when the component mounts
    setIsResendDisabled(true); // Disable the resend button initially
  }, []);

  // Effect to clear error and emailSent messages after 3 seconds
  useEffect(() => {
    if (error || emailSent) {
      const clearMessages = setTimeout(() => {
        setError("");
        setEmailSent(false);
      }, 3000); // Clear after 3 seconds

      return () => clearTimeout(clearMessages);
    }
  }, [error, emailSent]);

  return (
    <div className="grid h-screen w-full grid-cols-1 overflow-hidden lg:grid-cols-2">
      <div className="hidden h-full lg:block p-6">
        <div className="h-full w-full overflow-hidden rounded-3xl">
          <AuthSlider />
        </div>
      </div>
      <div className="flex items-center justify-center py-12 h-screen">
        <div className="mx-auto grid w-[350px] gap-6">
          <div className="flex items-center justify-center">
            <Image src={"/images/file.png"} alt={""} width={80} height={80} />
          </div>
          <div className="text-lg font-bold text-center pt-[25px]">
            <h1 className="text-[20px] font-semibold text-[#09090B]">
              A verification link has been
            </h1>
            <h1 className="text[20px] font-semibold text-[#09090B]">
              sent to your email account
            </h1>
          </div>
          {}
          <div className="text-center text-[16px] text-[#71717A]">
          {!isForgotPassword ? (
            "Please click on the link that has been sent to your email account to  verify your email and continue the registration process"):
            ("Please click on the link that has just been sent to your email account to change password")}
          </div>

          {error && <p className="text-red-500">{error}</p>}

          <div className="mt-4 text-center text-[16px] text-[#000]">
            Still cannot find the mail?{" "}
            <button
              onClick={resendVerificationEmail}
              disabled={isResendDisabled} // Disable the button during the countdown
              className={`${isResendDisabled
                ? "text-gray-400 cursor-not-allowed"
                : "text-primary"
                }`}
            >
              Resend email
            </button>
            {isResendDisabled && (
              <span className="ml-2">
                ({timer}s) {/* Show the countdown beside the button */}
              </span>
            )}
          </div>
        </div>
        <EmailSentToast emailSent={emailSent}
          variant="default"
          title="Success"
          description="Email has been sent successfully"
          duration={3000} />
      </div>
    </div>
  );
}
