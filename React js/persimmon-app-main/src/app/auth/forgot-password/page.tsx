"use client";
import Link from "next/link";
import { auth } from "../../components/firebaseConfig"; // Import auth from your firebaseConfig file
import { sendPasswordResetEmail } from 'firebase/auth';
import Image from 'next/image';
import React, { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useRouter } from "next/navigation"; // For navigation
import { AuthSlider } from "@/app/components/slider";

export default function ForgotPassword() {
  const [email, setEmail] = useState("");
  const [errors, setErrors] = useState({ email: "", credentialsValidation: "" });
  const router = useRouter(); // Initialize router for navigation

  const validateEmail = (email:string) => {
    if (!email) {
      return "Email is required";
    } else if (!/\S+@\S+\.\S+/.test(email)) {
      return "Please enter a valid email address";
    }
    return "";
  };

  const handleEmailChange = (e:any) => {
    const newEmail = e.target.value;
    setEmail(newEmail);

    // Update email error message on change
    setErrors((prevErrors) => ({
      ...prevErrors,
      email: validateEmail(newEmail),
    }));
  };

  const handleSubmit = async (e: React.FormEvent<HTMLElement>) => {
    e.preventDefault();
    const emailError = validateEmail(email);

    if (emailError) {
      setErrors({ email: emailError, credentialsValidation: "" });
      return;
    }

    try {
      const actionCodeSettings = {
        url: `https://persimmon-ui.storage.googleapis.com?typeOfPage=reset-password&email=${email}`,
        handleCodeInApp: true,
      };

      await sendPasswordResetEmail(auth, email, actionCodeSettings);
      console.log("Mail sent successfully");
      router.push("/auth/verification?pageType=forgot-password"); 
    } catch (error) {
      console.log("Error:", error);
    }
  };

  return (
    <div className="grid h-screen w-full grid-cols-1 overflow-hidden lg:grid-cols-2">
          <div className="hidden h-full lg:block p-6">
            <div className="h-full w-full overflow-hidden rounded-3xl">
              <AuthSlider />
            </div>
          </div>
      <div className="flex items-center justify-center py-12 h-screen">
        <form onSubmit={handleSubmit} noValidate className="mx-auto grid w-[405px] gap-6">
          <div className="grid gap-2 text-center">
            <h1 className="text-3xl font-bold">Forgot Password?</h1>
            <p className="text-muted-foreground">
              Enter the email address associated with your account and we’ll send you a link to reset your password
            </p>
          </div>
          <div className="grid gap-4 justify-center">
            <div className="grid gap-2">
              <Label htmlFor="email">Email</Label>
              <Input
                id="email"
                type="email"
                placeholder="Enter your company email"
                value={email}
                onChange={handleEmailChange}
              />
              {errors.email && <p className="text-red-500 text-sm mt-1">{errors.email}</p>}
              {errors.credentialsValidation && <p className="text-red-500 text-sm mt-1">{errors.credentialsValidation}</p>}
            </div>
            <Button type="submit" className=" w-[350px] bg-primary">
              Continue
            </Button>
          </div>
          <div className="mt-2 text-center text-sm">
            <div className="mb-2 text-center text-sm text-muted-foreground" >or</div>
            Already have an account?{" "}
            <Link href="/auth/log-in" className="text-primary">
              Login
            </Link>
          </div>
        </form>
      </div>
    </div>
  );
}
