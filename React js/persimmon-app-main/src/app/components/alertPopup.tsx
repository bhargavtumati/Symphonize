"use client";

import React from "react";
import {
  AlertDialog,
  AlertDialogContent,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogAction,
  AlertDialogCancel,
} from "@/components/ui/alert-dialog";
import Image from "next/image";
interface AlertDialogWrapperProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  description: string;
  confirmText?: string;
  cancelText?: string;
  onConfirm?: () => void;
  onCancel?: () => void;
}

const AlertDialogWrapper: React.FC<AlertDialogWrapperProps> = ({
  isOpen,
  onClose,
  title,
  description,
  confirmText = "Yes",
  cancelText = "No",
  onConfirm,
  onCancel,
}) => {
  if (!isOpen) return null;
  return (
    <div className="fixed inset-0 flex items-center justify-center z-[1000] bg-black bg-opacity-5">
      <AlertDialog open={isOpen} onOpenChange={onClose}>
        <AlertDialogContent className="bg-white rounded-lg p-4 w-[564px] shadow-lg">
          {/* Close Button */}
          <div className="flex justify-end">
            <Image
              src="/images/crossIcon.svg"
              width={16}
              height={16}
              alt={""}
              onClick={onClose}
            />
          </div>
          <div className="pl-2 pr-2">
            {/* Header Section */}
            <AlertDialogHeader>
              <AlertDialogTitle className="text-[20px] text-[#1E293B] font-normal leading-7">
                {title}
              </AlertDialogTitle>
              <AlertDialogDescription className="text-[#64748B] text-[14px] mt-2 leading-6">
                {description}
              </AlertDialogDescription>
            </AlertDialogHeader>

            {/* Footer Section */}
            <AlertDialogFooter className="flex justify-end mt-4">
              <AlertDialogCancel
                onClick={onClose}
                className="bg-[#F3F4F6] hover:bg-[#E5E7EB] text-[#374151] rounded-lg px-4 py-2 transition-colors"
              >
                {cancelText}
              </AlertDialogCancel>
              <AlertDialogAction
                onClick={onConfirm}
                className="bg-[#EF4444] hover:bg-[#DC2626] text-white rounded-lg px-4 py-2 transition-colors"
              >
                {confirmText}
              </AlertDialogAction>
            </AlertDialogFooter>
          </div>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
};

export default AlertDialogWrapper;
