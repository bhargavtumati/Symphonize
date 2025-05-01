"use client"

import { Check, X } from "lucide-react"
import { Input } from "@/components/ui/input"
import { cn } from "@/lib/utils"
import type { InputWithIconsProps } from "../types"

export default function InputWithIcons({
  containerClassName = "relative w-full",
  inputClassName = "pr-16 h-8 w-48",
  iconsContainerClassName = "absolute right-3 top-1/2 -translate-y-1/2 flex items-center gap-2",
  checkIconClassName = "h-4 w-4 text-black cursor-pointer",
  xIconClassName = "h-4 w-4 text-black-500 cursor-pointer",
  placeholder = "Enter Name",
  value,
  onChange,
  onCheckClick,
  onXClick,
}: InputWithIconsProps) {
  return (
    <div className={cn(containerClassName)}>
      <Input type="text" placeholder={placeholder} className={cn(inputClassName)} value={value} onChange={onChange} />
      <div className={cn(iconsContainerClassName)}>
        <Check className={cn(checkIconClassName)} onClick={onCheckClick} />
        <X className={cn(xIconClassName)} onClick={onXClick} />
      </div>
    </div>
  )
}

