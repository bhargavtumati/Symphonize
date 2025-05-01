import type React from "react"
import Image from "next/image"
import type { CustomizationSettings } from "@/app/types/customization"
import { useCallback } from "react"

interface HeaderProps {
  settings?: CustomizationSettings | null
  careerPage: boolean
}

const Header: React.FC<HeaderProps> = ({ settings, careerPage }) => {
  const headerStyle = {
    backgroundColor: settings?.headerColor || "transparent",
  }

    const handleClick = useCallback(
      (e: React.MouseEvent<HTMLAnchorElement>) => {
        e.preventDefault()
  
        if (settings) {
          // Try to open the link in a new tab
          const newWindow = window.open(settings.iconLink, "_top", "noopener,noreferrer")
  
          // If the new window is blocked, try to notify the parent window
          if (!newWindow || newWindow.closed || typeof newWindow.closed === "undefined") {
            if (window.top && window.top !== window) {
              window.top.postMessage({ type: "openLink", url: settings.iconLink }, "*")
            }
          }
        }
      },
      [settings],
    )
  return (
    <header
      className={`${careerPage ? "fixed top-0 left-0 right-0 z-10 shadow-md" : ""} 
                  h-20 flex items-center px-4`}
      style={headerStyle}
    >
      <div className={`container mx-auto flex ${careerPage ? "justify-start" : "justify-between"} items-center`}>
        {careerPage ? (
          <a href={settings?.iconLink || "#"} className="inline-block" onClick={handleClick}>
            <Image
              src={`data:image/png;base64,${settings?.icon}`}
              height={40}
              width={100}
              alt="Company Logo"
              className="rounded-lg h-[60px] w-auto object-contain"
            />
          </a>
        ) : (
          <div className="inline-block">
            <Image
              src={settings?.icon || "/placeholder.svg"}
              height={40}
              width={100}
              alt="Company Logo"
              className="rounded-lg h-[60px] w-auto object-contain"
            />
          </div>
        )}
        {!careerPage && (
          <div className="text-white">{/* Add any additional header content for non-career pages here */}</div>
        )}
      </div>
    </header>
  )
}

export default Header

