"use client"

import { useState, useEffect } from "react"
import { X, Minimize2, Maximize2 } from "lucide-react"
import ParsingAnimation from "./ParsingAnimation"
import SuccessAnimation from "./successAnimation"
import FailureAnimation from "./FailureAnimation"
import { Button } from "@/components/ui/button"
import { CustomizationSettings } from "../types/customization"

interface AnimationDialogProps {
  isParsing: boolean
  isSuccess: boolean
  isFailure: boolean
  tokenExpired: boolean
  onClose: () => void
  parsingMessage?: string
  successMessage?: string
  failureMessage?: string
  tokenExpiredMessage?: string
  settings: CustomizationSettings | null
}

const AnimationDialog: React.FC<AnimationDialogProps> = ({
  isParsing,
  isSuccess,
  isFailure,
  tokenExpired,
  onClose,
  parsingMessage = "Parsing in progress...",
  successMessage = "Operation completed successfully!",
  failureMessage = "An error occurred. Please try again.",
  tokenExpiredMessage = "The token has expired. Please re-authenticate the user.",
  settings
}) => {
  const [isMinimized, setIsMinimized] = useState(false)

  useEffect(() => {
    if (isParsing || isSuccess || isFailure) {
      setIsMinimized(false)
    }
  }, [isParsing, isSuccess, isFailure])

  if (!(isParsing || isSuccess || isFailure || tokenExpired)) {
    return null
  }

  const handleMinimize = () => {
    setIsMinimized(true)
  }

  const handleMaximize = () => {
    setIsMinimized(false)
  }

  if (isMinimized) {
    return (
      <div className="fixed bottom-4 right-4 bg-white shadow-lg rounded-lg p-4 cursor-pointer" onClick={handleMaximize}>
        <Maximize2 className="h-4 w-4" />
      </div>
    )
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 w-96">
        <div className="flex justify-end mb-4">
          <Button onClick={handleMinimize} variant="none">
            <Minimize2 className="h-5 w-5" />
          </Button>
          <Button
            variant="none"
            onClick={onClose}
            disabled={isParsing}
            className={`${isParsing ? "opacity-50 cursor-not-allowed" : "opacity-100 cursor-pointer"}`}
          >
            <X className="h-5 w-5" />
          </Button>
        </div>
        <div className="text-center">
          {tokenExpired && (
            <>
              <p className="mt-4 text-red-600">{tokenExpiredMessage}</p>
              <Button onClick={onClose} className="mt-4 w-20" style={{ backgroundColor: settings?.primaryColor }}>
                OK
              </Button>
            </>
          )}
          {isParsing && (
            <>
              <ParsingAnimation />
              <p className="mt-4 text-gray-600">{parsingMessage}</p>
            </>
          )}
          {isSuccess && (
            <>
              <SuccessAnimation />
              <p className="mt-4 text-green-600">{successMessage}</p>
              <Button onClick={onClose} className="mt-4 w-20" style={{ backgroundColor: settings?.primaryColor }}>
                Done
              </Button>
            </>
          )}
          {isFailure && (
            <>
              <FailureAnimation />
              <p className="mt-4 text-red-600">{failureMessage}</p>
              <Button onClick={onClose} className="mt-4 w-20" style={{ backgroundColor: settings?.primaryColor }}>
                OK
              </Button>
            </>
          )}
        </div>
      </div>
    </div>
  )
}

export default AnimationDialog

