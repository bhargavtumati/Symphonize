"use client";

import { useEffect } from "react";
import { useToast } from "@/components/hooks/use-toast";

interface ToastProps {
  emailSent: boolean;
  variant?: "default" | "destructive"; // Default or error type
  title: string;
  description: string;
  duration?: number; // Auto-dismiss duration
}

const EmailSentToast = ({
  emailSent,
  variant = "default",
  title,
  description,
  duration = 3000,
}: ToastProps) => {
  const { toast } = useToast();

  useEffect(() => {
    if (emailSent) {
      toast({
        variant,
        title,
        description,
        duration,
      });
    }
  }, [emailSent, toast, variant, title, description, duration]);

  return null; // No UI element, just fires the toast
};

export default EmailSentToast;
