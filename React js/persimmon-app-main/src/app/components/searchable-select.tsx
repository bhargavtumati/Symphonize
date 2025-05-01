"use client"

import { useState, useEffect, useRef } from "react"

interface CustomDropdownProps {
  options: string[]
  value: string
  onChange: (value: string) => void
  placeholder: string
}

export function CustomDropdown({ options, value, onChange, placeholder }: CustomDropdownProps) {
  const [isOpen, setIsOpen] = useState(false)
  const [searchTerm, setSearchTerm] = useState("")
  const [filteredOptions, setFilteredOptions] = useState(options)
  const dropdownRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const filtered = options.filter((option) => option.toLowerCase().includes(searchTerm.toLowerCase()))
    setFilteredOptions(filtered)
  }, [searchTerm, options])

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false)
      }
    }

    document.addEventListener("mousedown", handleClickOutside)
    return () => {
      document.removeEventListener("mousedown", handleClickOutside)
    }
  }, [])

  return (
    <div className="relative" ref={dropdownRef}>
      <button
        type="button"
        className="w-full px-3 py-2 text-left text-sm border rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
        onClick={() => setIsOpen(!isOpen)}
      >
        {value || placeholder}
      </button>
      {isOpen && (
        <div className="absolute z-50 w-[200px] mt-1 bg-white border rounded-md shadow-lg">
          <input
            type="text"
            placeholder="Search..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full px-3 py-2 text-sm border-b focus:outline-none"
          />
          <div className="max-h-60 overflow-auto">
            {filteredOptions.map((option) => (
              <button
                key={option}
                className={`w-full px-3 py-2 text-left text-sm hover:bg-gray-100 ${
                  value === option ? "bg-gray-100" : ""
                }`}
                onClick={() => {
                  onChange(option)
                  setIsOpen(false)
                  setSearchTerm("")
                }}
              >
                {option}
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
