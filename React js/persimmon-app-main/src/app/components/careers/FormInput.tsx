import { CustomizationSettings } from "@/app/types/customization"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { cn } from "@/lib/utils"
import type React from "react"
import { useState, useEffect } from "react"

interface FormFieldProps {
  label: string
  id: string
  type: string
  value: string
  onChange: (e: React.ChangeEvent<HTMLInputElement>) => void
  placeholder: string
  error?: string
  validate: (value: string) => string
  onValidation: (id: string, error: string) => void
  showError: boolean
  settings: CustomizationSettings | null
}

const FormField: React.FC<FormFieldProps> = ({
  label,
  id,
  value,
  type,
  onChange,
  placeholder,
  error,
  validate,
  onValidation,
  showError,
  settings,
}) => {
  const [localError, setLocalError] = useState<string>("")

  useEffect(() => {
    const validationError = validate(value);
    if (validationError !== localError) {
      setLocalError(validationError);
      onValidation(id, validationError);
    }
  }, [value, id, validate, onValidation, localError]);
  
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    onChange(e)
    const validationError = validate(e.target.value)
    setLocalError(validationError)
    onValidation(id, validationError)
  }

  return (
    <div>
      <Label htmlFor={id} className="block font-medium mb-1">
        {label}
      </Label>
      <Input
        id={id}
        value={value}
        type={type}
        onChange={handleChange}
        placeholder={placeholder}
        className={cn("pr-20", settings?.darkMode && "border-white", "border")}
        />
      {showError && (error || localError) && <p className="text-red-500 mt-1">{error || localError}</p>}
    </div>
  )
}

export default FormField

