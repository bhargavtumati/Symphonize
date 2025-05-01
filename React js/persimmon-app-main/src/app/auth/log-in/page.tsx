"use client";
import React, { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { signInWithEmailAndPassword } from "firebase/auth";
import { auth } from "../../components/firebaseConfig"; // Update the path if necessary
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { getCurrentUserEmail } from "../../components/AuthProvider";
import { apiService } from "@/app/api/service";
import { FiEye, FiEyeOff } from "react-icons/fi";
import { SESSION_STORAGE } from "@/app/utils/constants";
import { AuthSlider } from "@/app/components/slider";
import { Loader2 } from "lucide-react";

export default function LogIn() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState({
    email: "",
    password: "",
    credentialsValidation: "",
  });
  const [touched, setTouched] = useState({ email: false, password: false });
  const router = useRouter();

  // Helper function to validate inputs
  const validateFields = () => {
    let validationErrors = {
      email: "",
      password: "",
      credentialsValidation: "",
    };

    if (!email) {
      validationErrors.email = "Email is required";
    } else if (!/\S+@\S+\.\S+/.test(email)) {
      validationErrors.email = "Please enter a valid email address";
    }

    if (!password) {
      validationErrors.password = "Password is required";
    }

    return validationErrors;
  };

  // Handle field changes
  const handleInputChange = (
    e: React.ChangeEvent<HTMLInputElement>,
    field: string
  ) => {
    const { value } = e.target;

    // Update email or password based on field
    if (field === "email") {
      setEmail(value);
    } else if (field === "password") {
      setPassword(value);
    }

    // Set the field as touched when the user starts typing
    setTouched({ ...touched, [field]: true });

    // Re-validate the field after the user modifies it
    const newErrors = { ...errors };
    if (field === "email") {
      if (!value) {
        newErrors.email = "Email is required";
      } else if (!/\S+@\S+\.\S+/.test(value)) {
        newErrors.email = "Please enter a valid email address";
      } else {
        newErrors.email = ""; // Clear the error if valid
      }
    }

    if (field === "password") {
      if (!value) {
        newErrors.password = "Password is required";
        newErrors.credentialsValidation = "";
      } else {
        newErrors.password = ""; // Clear the error if valid
      }
    }

    setErrors(newErrors);
  };
  const togglePasswordVisibility = () => {
    setShowPassword(!showPassword);
  };

  // Handle form submission
  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();

    // Validate fields on submit
    const validationErrors = validateFields();
    setErrors(validationErrors);

    // Mark fields as touched so that errors show if the user hasn't interacted
    setTouched({
      email: true,
      password: true,
    });

    const hasErrors = Object.values(validationErrors).some(
      (value) => value !== ""
    );
    if (!hasErrors) {
      try {
        setLoading(true);
        await signInWithEmailAndPassword(auth, email, password);
        const userEmail = (await getCurrentUserEmail()) as string;
        sessionStorage.setItem(SESSION_STORAGE.userName, userEmail);
        const response = await apiService(
          `/recruiter/${userEmail}`,
          "GET",
          null
        );
        const data = response;
       
        if (data) {
          router.push("/dashboard");
          setLoading(false);
        } else {
          router.push("/multi-form");
          setLoading(false);
        }

        console.log("Logged in successfully");
      } catch (error) {
        validationErrors.credentialsValidation = "Invalid email or password";
        setErrors({ ...validationErrors});
        setLoading(false);
      }
    }
  };
  // Toggle password visibility

  return (
    <div className="grid h-screen w-full grid-cols-1 overflow-hidden lg:grid-cols-2">
      <div className="hidden h-full lg:block p-6">
        <div className="h-full w-full overflow-hidden rounded-3xl">
          <AuthSlider />
        </div>
      </div>
      <div className="flex h-full items-center justify-center p-6">
        <div className="w-full max-w-[350px] space-y-6">
          <div className="space-y-2 text-center">
            <h1 className="text-3xl font-bold">Login</h1>
            <p className="text-sm text-muted-foreground">
              Enter your email below to login to your account
            </p>
          </div>
          <form onSubmit={handleSubmit} noValidate className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="email">Email</Label>
              <Input
                id="email"
                type="email"
                placeholder="me@company.com"
                value={email}
                onChange={(e) => handleInputChange(e, "email")}
              />
              {touched.email && errors.email && (
                <p className="text-sm text-red-500">{errors.email}</p>
              )}
            </div>
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <Label htmlFor="password">Password</Label>
                <Link
                  href="/auth/forgot-password"
                  className="text-sm text-muted-foreground underline-offset-4 hover:underline"
                >
                  Forgot password?
                </Link>
              </div>
              <div className="relative">
                <Input
                  id="password"
                  type={showPassword ? "text" : "password"}
                  placeholder="Enter password"
                  value={password}
                  onChange={(e) => handleInputChange(e, "password")}
                  className="pr-10"
                />
                <button
                  type="button"
                  onClick={togglePasswordVisibility}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
                >
                  {showPassword ? (
                    <FiEye className="h-5 w-5" />
                  ) : (
                    <FiEyeOff className="h-5 w-5" />
                  )}
                </button>
              </div>
              {touched.password && errors.password && (
                <p className="text-sm text-red-500">{errors.password}</p>
              )}
            </div>
            {errors && <p className="text-sm text-red-500">{errors.credentialsValidation}</p>}
            <Button type="submit" className="w-full loader">
              {loading ? (
                <Loader2 className="mr-2 h-[30px] w-12 animate-spin" />
              ) : (
                <div>Login</div>
              )}
            </Button>
          </form>
          <div className="text-center text-sm">
            Don&apos;t have an account?{" "}
            <Link
              href="/auth/sign-up"
              className="font-medium underline underline-offset-4 hover:text-primary"
            >
              Sign up
            </Link>
          </div>
        
        </div>
      </div>
    </div>
  );
}
