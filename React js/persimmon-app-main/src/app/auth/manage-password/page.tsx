"use client";
import { useEffect, useState } from "react";
import {
  verifyPasswordResetCode,
  confirmPasswordReset,
  signInWithEmailAndPassword,
} from "firebase/auth";
import Image from "next/image";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Eye, EyeOff } from "lucide-react";
import { useRouter } from "next/navigation";
import { auth } from "../../components/firebaseConfig";
import { getCurrentUserEmail } from "@/app/components/AuthProvider";
import { apiService } from "@/app/api/service";
import { AuthSlider } from "@/app/components/slider";

export default function CreatePassword() {
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [passwordError, setPasswordError] = useState("");
  const [confirmPasswordError, setConfirmPasswordError] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [firebaseError, setFirebaseError] = useState("");
  const [resetCodeVerified, setResetCodeVerified] = useState(false);
  const [resetCodeError, setResetCodeError] = useState("");
  const [typeOfPage, setTypeOfPage] = useState("create-password");
  const [submitted, setSubmitted] = useState(false);
  const [email, setEmail] = useState("");
  const router = useRouter();

  const validatePassword = (passwordValue: any, confirmPasswordValue: any) => {
    const passwordPattern =
      /^(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*])[A-Za-z\d!@#$%^&*]{8,16}$/;
    let isValid = true;

    if (!passwordValue) {
      setPasswordError("Password is required.");
      isValid = false;
    } else if (passwordValue.includes(" ")) {
      setPasswordError(
        "Spaces are not allowed. Kindly enter a valid password."
      );
      isValid = false;
    } else if (!passwordPattern.test(passwordValue)) {
      setPasswordError(
        "Password must be at least 8 characters long and contain one uppercase letter, one number, and one special character."
      );
      isValid = false;
    } else {
      setPasswordError("");
    }

    if (!confirmPasswordValue) {
      setConfirmPasswordError("Confirm password is required.");
      isValid = false;
    } else if (passwordValue !== confirmPasswordValue) {
      setConfirmPasswordError("Passwords do not match.");
      isValid = false;
    } else {
      setConfirmPasswordError("");
    }

    return isValid;
  };

  useEffect(() => {
    const searchParams = new URLSearchParams(window.location.search);
    const continueUrl = searchParams.get("continueUrl");
    const oobCode = searchParams.get("oobCode");

    if (continueUrl) {
      const url = new URL(continueUrl);
      const pageType = url.searchParams.get("typeOfPage");
      const emailId = url.searchParams.get("email");
      if (emailId) setEmail(emailId);
      if (pageType) setTypeOfPage(pageType);
    }

    if (oobCode) {
      verifyPasswordResetCode(auth, oobCode)
        .then(() => setResetCodeVerified(true))
        .catch(() => setResetCodeError("Invalid or expired reset link."));
    }
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitted(true);

    const isValid = validatePassword(password, confirmPassword);

    if (isValid) {
      try {
        const searchParams = new URLSearchParams(window.location.search);
        const oobCode = searchParams.get("oobCode");

        if (oobCode) {
          await confirmPasswordReset(auth, oobCode, password);
          await signInWithEmailAndPassword(auth, email, password);
          const userEmail = (await getCurrentUserEmail()) as string;
          const user = auth.currentUser;
          if (user) {
            user
              .getIdToken(true) // Force token refresh
              .then((idToken: any) => {
                // Store refreshed token in localStorage
                localStorage.setItem("firebaseIdToken", idToken);
              });
          }
          const response = await apiService(
            `/recruiter/${userEmail}`,
            "GET",
            null
          );
          const data = response;

          if (data) {
            router.push("/dashboard");
          } else {
            router.push("/multi-form");
          }
        } else {
          setFirebaseError("No user is currently logged in.");
        }
      } catch (error: any) {
        if (error.message == "EXPIRED_OOB_CODE") {
          setFirebaseError("Email link has expired");
        } else {
          setFirebaseError("Failed to update password. Please try again.");
        }

        console.error(error);
      }
    }
  };

  // Real-time validation on input change after first submit
  const handlePasswordChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setPassword(value);
    if (submitted) validatePassword(value, confirmPassword); // Pass direct values
  };

  const handleConfirmPasswordChange = (
    e: React.ChangeEvent<HTMLInputElement>
  ) => {
    const value = e.target.value;
    setConfirmPassword(value);
    if (submitted) validatePassword(password, value); // Pass direct values
  };

  return (
    <div className="grid h-screen w-full grid-cols-1 overflow-hidden lg:grid-cols-2">
      {resetCodeError && <p className="error">{resetCodeError}</p>}
      {resetCodeVerified && (
        <>
          <div className="hidden h-full lg:block p-6">
            <div className="h-full w-full overflow-hidden rounded-3xl">
              <AuthSlider />
            </div>
          </div>
          <div className="flex items-center justify-center py-12 h-screen">
            <form
              onSubmit={handleSubmit}
              className="mx-auto grid w-[350px] gap-6"
            >
              <div className="grid gap-2 text-center">
                {typeOfPage === "reset-password" ? (
                  <>
                    <h1 className="text-3xl font-bold">Reset Password</h1>
                    <p className="text-balance text-muted-foreground">
                      Reset a strong and secure password to keep your account
                      safe
                    </p>
                  </>
                ) : (
                  <>
                    <h1 className="text-3xl font-bold">Create Password</h1>
                    <p className="text-balance text-muted-foreground">
                      Create a strong and secure password to keep your account
                      safe
                    </p>
                  </>
                )}
              </div>
              <div className="grid gap-4">
                <div className="grid gap-2">
                  <Label htmlFor="password">Password</Label>
                  <div className="relative">
                    <Input
                      id="password"
                      type={showPassword ? "text" : "password"}
                      placeholder="Enter Password"
                      value={password}
                      onChange={handlePasswordChange}
                    />
                    <button
                      type="button"
                      className="absolute inset-y-0 right-0 pr-3 flex items-center justify-center h-full"
                      onClick={() => setShowPassword(!showPassword)}
                    >
                      {showPassword ? <EyeOff size={20} /> : <Eye size={20} />}
                    </button>
                  </div>
                  {submitted && passwordError && (
                    <p className="text-red-600 text-sm mt-1">{passwordError}</p>
                  )}
                </div>
                <div className="grid gap-2">
                  <Label htmlFor="confirm-password">Confirm Password</Label>
                  <Input
                    id="confirm-password"
                    type="password"
                    placeholder="Re-Enter Password"
                    value={confirmPassword}
                    onChange={handleConfirmPasswordChange}
                  />
                  {submitted && confirmPasswordError && (
                    <p className="text-red-600 text-sm">
                      {confirmPasswordError}
                    </p>
                  )}
                </div>
                {firebaseError && (
                  <p className="text-red-600 text-sm">{firebaseError}</p>
                )}
                <Button type="submit" className="w-full">
                  {typeOfPage === "reset-password"
                    ? "Reset Password"
                    : "Create Password"}
                </Button>
              </div>
            </form>
          </div>
        </>
      )}
    </div>
  );
}
