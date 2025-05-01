"use client";
import Image from "next/image";
import { useForm, SubmitHandler } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { auth } from "../../components/firebaseConfig";
import {
  createUserWithEmailAndPassword,
  sendPasswordResetEmail,
} from "firebase/auth";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { emailSchema } from "../../utils/emailValidation";
import { Card } from "@/components/ui/card";
import { AuthSlider } from "@/app/components/slider";

const signUpSchema = z.object({
  email: emailSchema,
});

type SignUpFormData = z.infer<typeof signUpSchema>;

const SignUp = () => {
  const router = useRouter();
  const {
    register,
    handleSubmit,
    formState: { errors },
    setError,
  } = useForm<SignUpFormData>({
    resolver: zodResolver(signUpSchema),
  });

  const onSubmit: SubmitHandler<SignUpFormData> = async (data) => {
    try {
      const password = Math.random().toString(36).slice(-8);

      await createUserWithEmailAndPassword(auth, data.email, password);

      const currentUser = auth.currentUser;
      if (currentUser) {
        await sendPasswordResetEmail(auth, data.email, {
          url: `https://persimmon-ui.storage.googleapis.com?typeOfPage=create-password&email=${data.email}`,
          handleCodeInApp: true,
        });

        router.push("/auth/verification?pageType=sign-up");
      } else {
        console.error("No current user found after sign-up");
      }
    } catch (error: any) {
      // Catch specific error from Firebase
      if (
        error.code === "auth/email-already-in-use" ||
        error.message === "EMAIL_EXISTS"
      ) {
        setError("email", {
          type: "manual",
          message: "Email already exists, please provide a new Email ID",
        });
      } else {
        console.error("Error during sign-up:", error);
      }
    }
  };
  const handleLinkedInLogin = () => {
    const clientId = "869hipzzzol1op"; // Replace with your LinkedIn app's Client ID
    const redirectUri = "http://localhost:3000/dashboard"; // Replace with your backend callback endpoint
    const scope = "openid profile email"; // Scopes for profile and email access

    // Construct LinkedIn's authorization URL
    const linkedInAuthUrl = `https://www.linkedin.com/oauth/v2/authorization?response_type=code&client_id=${clientId}&redirect_uri=${encodeURIComponent(
      redirectUri
    )}&scope=${encodeURIComponent(scope)}`;

    // Redirect user to LinkedIn's authentication page
    (window.location.href = linkedInAuthUrl), "_blank";
  };
  return (
    <div className="grid h-screen w-full grid-cols-1 overflow-hidden lg:grid-cols-2">
      <div className="hidden h-full lg:block p-6">
        <div className="h-full w-full overflow-hidden rounded-3xl">
          <AuthSlider />
        </div>
      </div>

      <div className="flex flex-col items-center justify-center py-12 h-screen">
        <form
          onSubmit={handleSubmit(onSubmit)}
          noValidate
          className="mx-auto grid w-[350px] gap-4"
        >
          <h1 className="text-3xl font-bold text-center Inter">Sign Up</h1>
          <p className="text-[#71717A] text-[14px] text-center">
            Enter your information to create an account
          </p>

          <div>
            <Label>Email</Label>
            <Input
              {...register("email")}
              placeholder="Enter your company email"
              type="email"
              className="mt-[5px]"
            />
            {errors.email && (
              <p className="text-red-500 text-sm mt-1">
                {errors.email.message}
              </p>
            )}
          </div>

          <Button type="submit" className="w-full text-white">
            Verify Email
          </Button>
          <Button onClick={handleLinkedInLogin}>Continue With LinkedIn</Button>

          <div className="text-center text-sm ">
            <p className="pb-4 text-[#71717A]">or</p>
            Already have an account?{" "}
            <Link href="/auth/log-in" className="text-primary">
              Login
            </Link>
          </div>
        </form>
      </div>
    </div>
  );
};

export default SignUp;
