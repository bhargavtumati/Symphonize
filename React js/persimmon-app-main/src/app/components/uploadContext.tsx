"use client"

import type React from "react"
import { createContext, useState, useContext, type ReactNode } from "react"
import type { FileData } from "../types"

interface UploadContextType {
  files: FileData[]
  setFiles: React.Dispatch<React.SetStateAction<FileData[]>>
  isMinimized: boolean
  setIsMinimized: React.Dispatch<React.SetStateAction<boolean>>
  showProgressModal: boolean
  setShowProgressModal: React.Dispatch<React.SetStateAction<boolean>>
  applicantCount: number
  setApplicantCount: React.Dispatch<React.SetStateAction<number>>
}

const UploadContext = createContext<UploadContextType | undefined>(undefined)

export const UploadProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [files, setFiles] = useState<FileData[]>([])
  const [isMinimized, setIsMinimized] = useState(false)
  const [showProgressModal, setShowProgressModal] = useState(false)
  const [applicantCount, setApplicantCount] = useState(0)

  return (
    <UploadContext.Provider
      value={{
        files,
        setFiles,
        isMinimized,
        setIsMinimized,
        showProgressModal,
        setShowProgressModal,
        applicantCount,
        setApplicantCount,
      }}
    >
      {children}
    </UploadContext.Provider>
  )
}

export const useUpload = () => {
  const context = useContext(UploadContext)
  if (context === undefined) {
    throw new Error("useUpload must be used within a UploadProvider")
  }
  return context
}

