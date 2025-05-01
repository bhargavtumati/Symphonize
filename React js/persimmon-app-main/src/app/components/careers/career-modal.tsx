"use client"

import { useState, useEffect } from "react"
import { Label } from "@/components/ui/label"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { Switch } from "@/components/ui/switch"
import { Button } from "@/components/ui/button"
import { Edit, Settings, Loader2, Upload } from "lucide-react"
import type { CustomizationSettings } from "@/app/types/customization"
import AlertDialogWrapper from "../alertPopup"
import { ColorPickerPopover } from "../ColorPickerPopover"
import { CustomSelect } from "@/components/filters/custom-select"
import { toast } from "@/components/hooks/use-toast"
import { CropModal } from "../image-cropper"
import type { Crop } from "react-image-crop"
import {INITIAL_COLORS, INITIAL_FONTS} from "@/app/utils/constants"

type CustomizationUIProps = {
  settings: CustomizationSettings
  onSettingsChange: (settings: CustomizationSettings) => void
  onBack: () => void
  careerPageUrl: string
}

export function CustomizationUI({ settings, onSettingsChange, onBack, careerPageUrl }: CustomizationUIProps) {
  const [primaryColors, setPrimaryColors] = useState(INITIAL_COLORS)
  const [headerColors, setHeaderColors] = useState(INITIAL_COLORS)
  const [newColor, setNewColor] = useState("#000000")
  const [fonts, setFonts] = useState(INITIAL_FONTS)
  const [loading, setLoading] = useState<boolean>(false)
  const [originalSettings, setOriginalSettings] = useState<CustomizationSettings>(settings)
  const [modalState, setModalState] = useState<{
    type: "delete" | null
  }>({ type: null })
  const [coverImageError, setCoverImageError] = useState<string | null>(null)
  const [iconError, setIconError] = useState<string | null>(null)
  const [cropModalOpen, setCropModalOpen] = useState(false)
  const [cropSrc, setCropSrc] = useState<string | null>(null)
  const [crop, setCrop] = useState<Crop>({
    unit: "%",
    x: 0,
    y: 0,
    width: 100,
    height: 100,
  })
  const [croppedIconData, setCroppedIconData] = useState<string | null>(null)

  useEffect(() => {
    setOriginalSettings(settings)
    // Only set colors if they don't exist yet

    setPrimaryColors(settings.allPrimaryColors || INITIAL_COLORS)
    setHeaderColors(settings.headerColors || INITIAL_COLORS)
  }, []) // Removed unnecessary dependencies

  const handleAddPrimaryColor = (newColor: string) => {
    if (primaryColors.includes(newColor)) return

    const updatedColors =
      primaryColors.length >= 10 ? [...primaryColors.slice(1), newColor] : [...primaryColors, newColor]

    setPrimaryColors(updatedColors)
    onSettingsChange({
      ...settings,
      primaryColor: newColor,
      allPrimaryColors: updatedColors,
    })
  }

  const handleAddHeaderColor = (newColor: string) => {
    if (headerColors.includes(newColor)) return

    const updatedColors = headerColors.length >= 10 ? [...headerColors.slice(1), newColor] : [...headerColors, newColor]

    setHeaderColors(updatedColors)
    onSettingsChange({
      ...settings,
      headerColor: newColor,
      headerColors: updatedColors,
    })
  }

  const closeModal = () => {
    setModalState({ type: null })
    // onBack()
  }

  const openModal = () => {
    setModalState({ type: "delete" })
  }

  console.log("here is the settinqs", settings)

  const handleDiscard = () => {
    onSettingsChange(originalSettings)
    setPrimaryColors(originalSettings.allPrimaryColors || INITIAL_COLORS)
    setHeaderColors(originalSettings.headerColors || INITIAL_COLORS)
    setModalState({ type: null })
    onBack()
  }

  const handleCroppedImage = (croppedImage: string) => {
    setCroppedIconData(croppedImage)
    onSettingsChange({ ...settings, icon: croppedImage })
    setCropModalOpen(false)
  }

  /**
   * Handles form submission to save the user's customization settings
   * for their career page. The settings are sent as a multipart form
   * with the image data if the user has uploaded a new cover image.
   * The request is sent to the API endpoint for updating the
   * customization settings.
   *
   * @returns {Promise<void>}
   */
  const handleSubmit = async () => {
    console.log('settings data',settings)
    setLoading(true)
    try {
      const formData = new FormData()
      formData.append("enable_cover_photo", settings.showCover.toString())
      formData.append("heading", settings.heading)
      formData.append("description", settings.description)
      formData.append("enable_dark_mode", settings.darkMode.toString())
      formData.append("color_selected", settings.primaryColor)
      formData.append("primary_colors", JSON.stringify(settings.allPrimaryColors))
      formData.append("font_style", settings.fontStyle)
      formData.append("selected_header_color", settings.headerColor)
      formData.append("header_colors", JSON.stringify(settings.headerColors))
      formData.append("career_page_url", careerPageUrl)

      // Handle cover image
      if (settings.coverImage && settings.coverImage.startsWith("data:image")) {
        const coverImageBlob = await fetch(settings.coverImage).then((r) => r.blob())
        formData.append("image", coverImageBlob, "cover_image.jpg")
      }

      // Handle icon
      if (croppedIconData) {
        const iconBlob = await fetch(croppedIconData).then((r) => r.blob())
        formData.append("icon", iconBlob, "icon_image.jpg")
      } else if (settings.icon) {
        const iconBlob = await fetch(settings.icon).then((r) => r.blob())
        formData.append("icon", iconBlob, "icon_image.jpg")
      }

      const storedUserEmail = sessionStorage.getItem("userEmail")
      if (storedUserEmail) {
        const domain = storedUserEmail.split("@")[1]
        const IdToken = localStorage.getItem("firebaseIdToken")
        const apiUrl = `${process.env.NEXT_PUBLIC_API}/api/v1/careerpage/customization/domain/${domain}`

        const response = await fetch(apiUrl, {
          method: "POST",
          headers: {
            Authorization: `Bearer ${IdToken}`,
          },
          body: formData,
        })

        if (!response.ok) {
          throw new Error("Failed to update settings")
        }

        toast({
          variant: "default",
          title: "Settings updated successfully",
        })
        console.log("Settings updated successfully")
        onBack()
      }
    } catch (error) {
      console.error("Error updating settings:", error)
      toast({
        variant: "destructive",
        title: "Failed to update settings",
        description: "Please try again later.",
      })
    } finally {
      setLoading(false)
      setCroppedIconData("")    }
  }

  return (
    <div className="space-y-6">
      <div>
        <div className="flex space-x-2">
          <Settings className="w-6 h-6" />
          <h3 className="text-xl text-black font-semibold mb-4 leading-7">General</h3>
        </div>
        <div className="space-y-2">
          <Label className="text-base text-black font-semibold">Header Color</Label>
          <div className="flex space-x-2">
            <ColorPickerPopover onAddColor={(color) => handleAddHeaderColor(color)} />

            <div className="flex gap-2 flex-wrap">
              {headerColors.map((color) => (
                <button
                  key={color}
                  className={`w-8 h-8 rounded-lg transition-all ${
                    settings.headerColor === color ? "ring-2 ring-offset-2 ring-blue-500" : ""
                  }`}
                  style={{ backgroundColor: color }}
                  onClick={() =>
                    onSettingsChange({
                      ...settings,
                      headerColor: color,
                      headerColors: headerColors,
                    })
                  }
                />
              ))}
            </div>
          </div>
        </div>
        <div className="flex justify-between mt-6">
          <div>
            <Label htmlFor="iconUpload" className="text-base text-black font-semibold">
              Logo
            </Label>
            <div className="relative h-32 bg-muted rounded-lg overflow-hidden mb-2 mt-2">
              {croppedIconData || settings.icon ? (
                <img
                  src={croppedIconData || settings.icon || "/placeholder.svg"}
                  alt="Icon"
                  className="object-cover w-full h-full"
                />
              ) : (
                <div className="w-full h-full flex items-center justify-center text-muted-foreground">
                  <Upload className="h-8 w-8" />
                </div>
              )}
              <div className="absolute inset-0 bg-black bg-opacity-50 flex items-center justify-center opacity-0 hover:opacity-100 transition-opacity">
                <label htmlFor="iconUpload" className="cursor-pointer">
                  <div className="bg-white text-black px-2 py-1 rounded-md text-sm flex items-center">
                    <Edit className="h-3 w-3 mr-1" />
                    {croppedIconData || settings.icon ? "Change" : "Upload"}
                  </div>
                </label>
              </div>
            </div>
            <input
              type="file"
              id="iconUpload"
              accept=".png,.jpg,.jpeg"
              className="hidden"
              onChange={(e) => {
                const file = e.target.files?.[0]
                if (file) {
                  if (file.type === "image/png" || file.type === "image/jpeg") {
                    const reader = new FileReader()
                    reader.onloadend = () => {
                      setCropSrc(reader.result as string)
                      setCropModalOpen(true)
                    }
                    reader.readAsDataURL(file)
                  } else {
                    toast({
                      variant: "destructive",
                      title: "Invalid file type",
                      description: "Please select a PNG or JPG file.",
                    })
                  }
                }
              }}
            />
          </div>
        </div>
        <div>
          <Label htmlFor="iconLink" className="text-base text-black font-semibold">
          Logo Destination
          </Label>
          <Input
            id="iconLink"
            disabled
            readOnly
            value={settings.iconLink}
            onChange={(e) => onSettingsChange({ ...settings, iconLink: e.target.value })}
            placeholder="Enter link for the icon"
          />
        </div>
        <div className="space-y-4 mt-6">
          <div className="flex items-center justify-between">
            <Label htmlFor="showCover" className="text-base text-black font-medium">
              Cover Image
            </Label>
            <Switch
              id="showCover"
              checked={settings.showCover}
              onCheckedChange={(checked) => onSettingsChange({ ...settings, showCover: checked })}
            />
          </div>

          <div className={`space-y-4 ${!settings.showCover ? "opacity-50 pointer-events-none" : ""}`}>
            <div>
              <div className="relative h-32 bg-muted rounded-lg overflow-hidden mb-2">
                {settings.coverImage ? (
                  <img
                    src={settings.coverImage || "/placeholder.svg"}
                    alt="Cover"
                    className="w-full h-full object-cover"
                  />
                ) : (
                  <div className="w-full h-full bg-slate-200 flex items-center justify-center text-muted-foreground">
                    No image selected
                  </div>
                )}
                <div className="absolute inset-0 bg-black bg-opacity-50 flex items-center justify-center opacity-0 hover:opacity-100 transition-opacity">
                  <label htmlFor="coverImageUpload" className="cursor-pointer">
                    <div className="bg-white text-black px-4 py-2 rounded-md flex items-center">
                      <Edit className="h-4 w-4 mr-2" />
                      {settings.coverImage ? "Change Image" : "Upload Image"}
                    </div>
                  </label>
                </div>
              </div>
              <input
                type="file"
                id="coverImageUpload"
                accept=".png,.jpg,.jpeg"
                className="hidden"
                onChange={(e) => {
                  const file = e.target.files?.[0]
                  if (file) {
                    if (file.type === "image/png" || file.type === "image/jpeg") {
                      setCoverImageError(null)
                      const reader = new FileReader()
                      reader.onloadend = () => {
                        onSettingsChange({
                          ...settings,
                          coverImage: reader.result as string,
                        })
                      }
                      reader.readAsDataURL(file)
                    } else {
                      setCoverImageError("Please select a PNG or JPG file.")
                      e.target.value = "" // Clear the input
                    }
                  }
                }}
              />
              {coverImageError && <p className="text-red-500 text-sm mt-2">{coverImageError}</p>}
            </div>

            <div className="space-y-2">
              <Label htmlFor="heading" className="text-base text-black font-semibold">
                Heading
              </Label>
              <Input
                id="heading"
                value={settings.heading}
                onChange={(e) => {
                  const value = e.target.value.slice(0, 15)
                  onSettingsChange({ ...settings, heading: value })
                }}
                maxLength={15}
                placeholder="Enter heading (max 15 characters)"
              />
              <p className="text-xs text-muted-foreground">{settings.heading.length}/15 characters</p>
            </div>

            <div className="space-y-2">
              <Label htmlFor="description" className="text-base text-black font-semibold">
                Description
              </Label>
              <Textarea
                id="description"
                value={settings.description}
                onChange={(e) => {
                  const value = e.target.value.slice(0, 250)
                  onSettingsChange({ ...settings, description: value })
                }}
                maxLength={250}
                placeholder="Enter description (max 250 characters)"
                className="resize-none"
                rows={4}
              />
              <p className="text-xs text-muted-foreground">{settings.description.length}/250 characters</p>
            </div>
          </div>
        </div>
      </div>

      <div>
        <h3 className="text-xl leading-7 font-semibold mb-4">Styling</h3>
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <Label htmlFor="darkMode" className="text-base font-semibold">
              Dark Mode
            </Label>
            <Switch
              id="darkMode"
              checked={settings.darkMode}
              onCheckedChange={(checked) => onSettingsChange({ ...settings, darkMode: checked })}
            />
          </div>

          <div className="space-y-2">
            <Label>Primary Color</Label>
            <div className="flex space-x-2">
              <ColorPickerPopover onAddColor={(color) => handleAddPrimaryColor(color)} />

              <div className="flex gap-2 flex-wrap">
                {primaryColors.map((color) => (
                  <button
                    key={color}
                    className={`w-8 h-8 rounded-lg transition-all ${
                      settings.primaryColor === color ? "ring-2 ring-offset-2 ring-blue-500" : ""
                    }`}
                    style={{ backgroundColor: color }}
                    onClick={() =>
                      onSettingsChange({
                        ...settings,
                        primaryColor: color,
                        allPrimaryColors: primaryColors,
                      })
                    }
                  />
                ))}
              </div>
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="fontStyle">Font Style</Label>
            <CustomSelect
              options={INITIAL_FONTS.map((font) => ({
                value: font,
                label: font,
              }))}
              placeholder="Select Font Style"
              value={settings.fontStyle}
              onValueChange={(value) => onSettingsChange({ ...settings, fontStyle: value })}
              triggerClassName={!settings.fontStyle ? "text-gray-400" : "text-black"}
            />
          </div>
        </div>
      </div>

      {loading && (
        <div className="loader absolute  top-2/3 left-1/2 transform -translate-x-1/2 -translate-y-1/2 flex items-center justify-center">
          <Loader2 className="mr-2 h-[30px] w-12 animate-spin z-1001" />
        </div>
      )}

      <AlertDialogWrapper
        isOpen={modalState.type === "delete"}
        onClose={closeModal}
        title="Are you sure you want to cancel?"
        description="You’ll lose all the current changes."
        confirmText="Yes"
        cancelText="No"
        onConfirm={handleDiscard}
      />
      <div className="flex justify-end gap-2 pt-4">
        <Button variant="outline" onClick={openModal}>
          Cancel
        </Button>
        <Button onClick={handleSubmit}>Submit</Button>
      </div>
      {cropModalOpen && cropSrc && (
        <CropModal
          src={cropSrc}
          crop={crop}
          setCrop={setCrop}
          onComplete={handleCroppedImage}
          onClose={() => setCropModalOpen(false)}
        />
      )}
    </div>
  )
}