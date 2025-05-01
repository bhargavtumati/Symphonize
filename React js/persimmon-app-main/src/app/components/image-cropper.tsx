import type React from "react"
import { useState } from "react"
import ReactCrop, { type Crop, type PixelCrop, centerCrop, makeAspectCrop } from "react-image-crop"
import "react-image-crop/dist/ReactCrop.css"
import { Button } from "@/components/ui/button"

interface CropModalProps {
  src: string
  crop: Crop
  setCrop: (crop: Crop) => void
  onComplete: (croppedImageUrl: string) => void
  onClose: () => void
}

function centerAspectCrop(mediaWidth: number, mediaHeight: number, aspect: number) {
  return centerCrop(
    makeAspectCrop(
      {
        unit: "%",
        width: 90,
      },
      aspect,
      mediaWidth,
      mediaHeight,
    ),
    mediaWidth,
    mediaHeight,
  )
}

export function CropModal({ src, crop, setCrop, onComplete, onClose }: CropModalProps) {
  const [imgRef, setImgRef] = useState<HTMLImageElement | null>(null)
  const [completedCrop, setCompletedCrop] = useState<PixelCrop>()

  function onImageLoad(e: React.SyntheticEvent<HTMLImageElement>) {
    const { width, height } = e.currentTarget
    setCrop(centerAspectCrop(width, height, 1))
  }

  const getCroppedImg = () => {
    if (!imgRef || !completedCrop) return

    const canvas = document.createElement("canvas")
    const ctx = canvas.getContext("2d")
    if (!ctx) {
      throw new Error("No 2d context")
    }

    const scaleX = imgRef.naturalWidth / imgRef.width
    const scaleY = imgRef.naturalHeight / imgRef.height

    canvas.width = completedCrop.width
    canvas.height = completedCrop.height

    ctx.drawImage(
      imgRef,
      completedCrop.x * scaleX,
      completedCrop.y * scaleY,
      completedCrop.width * scaleX,
      completedCrop.height * scaleY,
      0,
      0,
      completedCrop.width,
      completedCrop.height,
    )

    canvas.toBlob((blob) => {
      if (blob) {
        const croppedImageUrl = URL.createObjectURL(blob)
        onComplete(croppedImageUrl)
      }
    })
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white p-4 rounded-lg max-w-2xl w-full">
        <ReactCrop
          crop={crop}
          onChange={(_, percentCrop) => setCrop(percentCrop)}
          onComplete={(c) => setCompletedCrop(c)}
          aspect={undefined}
          minWidth={50}
          minHeight={50}
        >
          <img
            ref={setImgRef}
            src={src || "/placeholder.svg"}
            alt="Crop"
            onLoad={onImageLoad}
            style={{ maxWidth: "100%", maxHeight: "70vh" }}
          />
        </ReactCrop>
        <div className="mt-4 flex justify-end space-x-2">
          <Button onClick={onClose} variant="outline">
            Cancel
          </Button>
          <Button onClick={getCroppedImg}>Done</Button>
        </div>
      </div>
    </div>
  )
}

