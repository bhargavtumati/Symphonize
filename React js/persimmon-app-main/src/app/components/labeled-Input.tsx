import { useState, useRef, useEffect } from "react"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import type { FC, KeyboardEvent, ChangeEvent } from "react"
import { Label } from "@/components/ui/label"
import { Lock } from "lucide-react"
import { Button } from "@/components/ui/button"
import { formatText } from "../utils/helper"

interface LabeledInputProps {
  label: string
  type: string
  placeholder: string
  badgeClass?: string
  inputClass?: string
  containerClass?: string
  tabtype?: string
  value: string | string[] | undefined | number
  onChange?: (value: string | string[]) => void
  name: string
  keyNotPresent?: boolean
  isLocked?: boolean
}

const LabeledInput: FC<LabeledInputProps> = ({
  label,
  type,
  placeholder,
  badgeClass = "absolute right-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-500 z-50 bg-white",
  inputClass = "w-full h-10",
  containerClass = "flex items-center",
  tabtype,
  value,
  onChange,
  name,
  keyNotPresent = false,
  isLocked = false
}) => {
  const [inputValue, setInputValue] = useState("")
  const [showAllEmails, setShowAllEmails] = useState(false)
  const inputRef = useRef<HTMLInputElement>(null)
  const containerRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (inputRef.current && tabtype === "send_to_all") {
      inputRef.current.focus()
    }
  }, [tabtype])

  const handleInputChange = (e: ChangeEvent<HTMLInputElement>) => {
    if (tabtype === "send_to_all") {
      if (label.toLowerCase() === "to" || label.toLowerCase() === "from") {
        setInputValue(e.target.value)
      } else {
        onChange?.(e.target.value)
      }
    } else {
      onChange?.(e.target.value)
    }
  }

  if (tabtype === "send_to_all") {
    if (label.toLowerCase() === "from" || label.toLowerCase() === "to") {
      const emails =
        label.toLowerCase() === "from" ? (value ? [value as string] : []) : Array.isArray(value) ? value : []
      const visibleEmails = emails.slice(0, 3)
      const remainingEmailsCount = emails.length - 3

      return (
        <div className={`${containerClass}`}>
          <Badge variant="none" key="label" className={badgeClass}>
            {label}
          </Badge>
          <div className="w-full">
            <div className="flex items-center gap-2 p-2 border rounded-md h-[40px] w-full">
              {visibleEmails.map((email, index) => (
                <Badge
                  key={email}
                  variant="secondary"
                  className={`${index === 0 ? "ml-20" : ""
                    } flex items-center gap-2 px-2 py-1 ${label.toLowerCase() === "from" ? "max-w-full" : "max-w-[140px]"} overflow-hidden text-ellipsis whitespace-nowrap`}
                >
                  <span className="w-full">{email}</span>
                </Badge>
              ))}
              {remainingEmailsCount > 0 && (
                <span
                  className="text-sm text-muted-foreground cursor-pointer"
                  onMouseEnter={() => setShowAllEmails(true)}
                >
                  +{remainingEmailsCount} more
                </span>
              )}

            </div>
            {showAllEmails && remainingEmailsCount > 0 && (
              <div
                className="absolute left-0 mt-1 w-full bg-popover p-2 rounded-md shadow-md z-10 flex flex-wrap gap-2 items-center"
                onMouseEnter={() => setShowAllEmails(true)}
                onMouseLeave={() => setShowAllEmails(false)}
              >
                {emails.slice(3).map((email) => (
                  <div key={email} className="flex items-center">
                    <Badge
                      variant="secondary"
                      className="flex items-center gap-2 px-2 py-1 max-w-full overflow-hidden text-ellipsis whitespace-nowrap"
                    >
                      <span className="w-full">{email}</span>
                    </Badge>
                  </div>
                ))}
              </div>
            )}

          </div>
        </div>
      )
    } else if (label.toLowerCase() === "subject") {
      return (
        <div className={`${containerClass}`}>
          <Badge variant="none" key="label" className={badgeClass}>
            {label}
          </Badge>
          <div className="w-full">
            <Input
              type="text"
              placeholder={placeholder}
              className={`${inputClass}`}
              value={value as string}
              name={name}
              onChange={(e) => onChange?.(e.target.value)} 
            />
          </div>
        </div>
      )
    }
  }

  // Default case (non-send_to_all)
  return (
    <div className={`${containerClass}`}>
      <Label className={`w-48 ${keyNotPresent ? 'opacity-50 cursor-not-allowed' : ''}`}>
        {label}
      </Label>
      <div className="relative w-60 max-w-full">
        <Input
          placeholder={placeholder}
          className={`${inputClass} ${keyNotPresent && isLocked ? 'cursor-not-allowed' : ''}`}
          value={keyNotPresent ? "" : formatText(value as string)}
          onChange={(e) => {
            if (!keyNotPresent && !isLocked) { // Allow input only if keyNotPresent is false
              handleInputChange(e);
            }
          }}
          name={name}
          readOnly={keyNotPresent}
          disabled={keyNotPresent && isLocked}
        />
        {isLocked && value && !keyNotPresent && <Lock className={`${badgeClass}`} />}
      </div>
    </div>
  )
}

export default LabeledInput

