"use client"

import type React from "react"

import { useEffect, useState, useRef, useCallback } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card"
import Image from "next/image"
import { ArrowLeftRight, Loader2, ArrowLeft } from "lucide-react"
import { useToast } from "@/components/hooks/use-toast"
import { apiService } from "@/app/api/service"
import ZoomIntegrationStatus from "@/app/components/integration-status"
import IntegrationStatus from "@/app/components/integration-status"
import { useRouter } from "next/navigation"

export default function ZoomIntegrations() {
  const [clientId, setClientId] = useState("")
  const [clientSecret, setClientSecret] = useState("")
  const [verifyStatus, setVerifyStatus] = useState(false)
  const [loading, setLoading] = useState(true)
  const { toast } = useToast()
  const inputRef = useRef<HTMLInputElement>(null)
  const initialCheckRef = useRef(false)
  const router = useRouter()

  const handleRowClick = () => {
    router.push("/integrations")
  }
  const handleZoomIntegration = useCallback(
    async (zoomCode: string) => {
      if (!zoomCode) return
      try {
        const storedClientId = localStorage.getItem("zoomClientId")
        const storedClientSecret = localStorage.getItem("zoomClientSecret")
        const payload = {
          client_id: storedClientId,
          client_secret: storedClientSecret,
          code: zoomCode,
          redirect_uri: `${process.env.NEXT_PUBLIC_REDIRECT_URL}`,
        }
        const response = await apiService(`/integration/zoom`, "POST", payload)

        if (!response) {
          throw new Error("API call failed")
        }
        setVerifyStatus(true)
        toast({
          variant: "default",
          title: "Success",
          description: "Zoom integration successful",
          duration: 3000,
        })
      } catch (error) {
        console.error("Zoom integration error:", error)
        toast({
          variant: "destructive",
          title: "Error",
          description: error instanceof Error ? error.message : "An unexpected error occurred",
          duration: 3000,
        })
      }
    },
    [toast],
  )

  useEffect(() => {
    if (initialCheckRef.current) return
    initialCheckRef.current = true

    const checkVerifyStatus = async () => {
      try {
        const searchParams = new URLSearchParams(window.location.search)
        const zoomCode = searchParams.get("code")

        const status = await apiService("/integration/zoom/verify-status", "GET", null)
        if (zoomCode || !status) {
          await handleZoomIntegration(zoomCode || "")
        } else {
          setVerifyStatus(status)
        }
      } catch (error) {
        toast({
          variant: "destructive",
          title: "Not verified",
          description: error instanceof Error ? error.message : "An unexpected error occurred",
        })
      } finally {
        setLoading(false)
      }
    }

    checkVerifyStatus()
  }, [handleZoomIntegration, toast])

  const handleCopy = async () => {
    if (inputRef.current) {
      await navigator.clipboard.writeText(inputRef.current.value)
      toast({
        description: "URL copied to clipboard",
        duration: 2000,
      })
    }
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    localStorage.setItem("zoomClientId", clientId)
    localStorage.setItem("zoomClientSecret", clientSecret)
    const redirect_uri = `${process.env.NEXT_PUBLIC_REDIRECT_URL}`
    if (!clientId.trim() || !clientSecret.trim()) {
      toast({
        variant: "destructive",
        title: "Error",
        description: !clientId.trim() ? "Client ID is required" : "Client Secret is required",
      });
      return;
    }

    const zoomAuthUrl = `https://zoom.us/oauth/authorize?response_type=code&client_id=${clientId}&redirect_uri=${encodeURIComponent(
      redirect_uri,
    )}`

    window.location.href = zoomAuthUrl
  }

  if (loading) {
    return (
      <div className="loader absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 flex items-center justify-center">
        <Loader2 className="mr-2 h-[30px] w-12 animate-spin" />
      </div>
    )
  }

  if (verifyStatus) {
    return (
      <IntegrationStatus
        imageSrc="/images/zoom.svg"
        description="Manage your Zoom connection to schedule interviews seamlessly."
        handleEditClick={() => {
          setVerifyStatus(false)
        }}
      />
    );
  }


  return (
    <Card className="my-8 max-w-4xl p-2">
      <CardHeader>
        <span onClick={handleRowClick} className="flex space-x-2 ">
          <ArrowLeft className="w-6 h-6 cursor-pointer" />{" "}
          <CardTitle className="text-xl semibold leading-7 text-black">Zoom Integration</CardTitle>
        </span>
        <CardDescription className="text-base text-slate-500">
          Connect your Zoom account to schedule and manage interviews directly within Persimmon.
        </CardDescription>
        <CardContent className="space-y-4 p-0">
          <div>
            <div className="flex items-center space-x-2">
              <Image src={"/images/zoom.svg"} height={100} width={100} alt={"Zoom logo"} />
              <ArrowLeftRight strokeWidth={2} />
              <Image src="/images/persimmon-full-icon.svg" height={120} width={120} alt={"Perssimon logo"} />
            </div>
            <div className="p-6">
              <div className="space-x-2">
                <div className="space-x-2">
                  <span className="w-4 h-4 rounded-full bg-primary text-white p-4 inline-flex items-center justify-center">
                    1
                  </span>
                  <span className="text-base text-black">Once Login to Zoom Market Place App Account Go to</span>
                  <span className="text-baseS font-bold">Develop{">"} Build App</span>
                </div>
                <Image
                  src={"/images/step-1.png"}
                  height={100}
                  width={100}
                  className="w-full h-full p-6"
                  alt={"Zoom logo"}
                />
              </div>
              <div className="space-x-2 pt-6">
                <span className="w-4 h-4 rounded-full bg-primary text-white p-4 inline-flex items-center justify-center">
                  2
                </span>
                <span className="text-base text-black text-semibold">
                  Select <span className="font-bold">General App</span> and click Create
                </span>
                <Image
                  src={"/images/step-7.png"}
                  height={100}
                  width={100}
                  className="w-full h-full p-6"
                  alt={"Zoom logo"}
                />
              </div>
              <div className="space-x-2 pt-6">
                <span className="w-4 h-4 rounded-full bg-primary text-white p-4 inline-flex items-center justify-center">
                  3
                </span>
                <span className="text-base text-black text-semibold">
                  Select <span className="font-bold">Admin-Managed</span> and Click Save
                </span>
                <Image
                  src={"/images/step-6.png"}
                  height={100}
                  width={100}
                  className="w-full h-full p-6"
                  alt={"Zoom logo"}
                />
              </div>
              <div className="space-x-2 pt-6">
                <span className="w-4 h-4 rounded-full bg-primary text-white p-4 inline-flex items-center justify-center">
                  4
                </span>
                <span className="text-base text-black">
                  Copy OAuth Redirection URL From Persimmon and Paste to ZOOM OAuth Redirect URL
                </span>
                <div className="p-6">
                  <div className="w-full max-w-2xl space-y-2 bg-sky-50 p-6 rounded-2xl">
                    <Label htmlFor="url" className="text-sm font-medium">
                      OAuth Redirect URL
                    </Label>
                    <div className="flex gap-4">
                      <Input
                        ref={inputRef}
                        id="url"
                        value={process.env.NEXT_PUBLIC_REDIRECT_URL}
                        readOnly
                        className="bg-white flex-1"
                      />
                      <Button onClick={handleCopy} className="bg-sky-500 hover:bg-sky-600 text-white px-8">
                        Copy Link
                      </Button>
                    </div>
                  </div>
                </div>

                <Image
                  src={"/images/step-5.png"}
                  height={100}
                  width={100}
                  className="w-full h-full px-6"
                  alt={"Zoom logo"}
                />
              </div>

              <div className="space-x-2 pt-6">
                <span className="w-4 h-4 rounded-full bg-primary text-white p-4 inline-flex items-center justify-center">
                  5
                </span>
                <span className="text-base text-black">Copy Client ID and Client Secret from Zoom and Paste below</span>
                <div className="p-6">
                  <Image
                    src={"/images/step-4.png"}
                    height={100}
                    width={100}
                    className="w-full h-full"
                    alt={"Zoom logo"}
                  />
                  <Card className="border rounded-2xl mt-4 bg-[#E8F7FF]">
                    <CardHeader className="">
                      <CardTitle className="text-sm text-black">Paste Client ID and Client Secret here</CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-4">
                      <div className="space-y-2">
                        <Label htmlFor="clientId" className="text-sm font-medium text-black">
                          Client ID
                        </Label>
                        <div className="flex gap-2">
                          <Input
                            id="clientId"
                            placeholder="Past Client ID"
                            className="bg-white flex-1"
                            value={clientId}
                            onChange={(e) => setClientId(e.target.value)}
                          />
                        </div>
                      </div>
                      <div className="space-y-2">
                        <Label htmlFor="clientSecret" className="text-sm font-medium text-black ">
                          Client Secret
                        </Label>
                        <div className="flex gap-2 mt-4">
                          <Input
                            id="clientSecret"
                            placeholder="Paste Client Secret"
                            type="password"
                            className="bg-white flex-1"
                            value={clientSecret}
                            onChange={(e) => setClientSecret(e.target.value)}
                          />
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                </div>
              </div>
              <div className="space-x-2 pt-6">
                <span className="w-4 h-4 rounded-full bg-primary text-white p-4 inline-flex items-center justify-center">
                  6
                </span>
                <span className="text-base text-black font-bold">Add Scopes</span>
                <Image
                  src={"/images/step-3.png"}
                  height={100}
                  width={100}
                  className="w-full h-full p-6"
                  alt={"Zoom logo"}
                />
              </div>
              <div className="space-x-2 pt-6">
                <span className="w-4 h-4 rounded-full bg-primary text-white p-4 inline-flex items-center justify-center">
                  7
                </span>
                <span className="text-base text-black font-bold">Select the following and Click Done.</span>
                <div className="px-8 py-4 space-y-2">
                  <Card className="border rounded-2xl">
                    <CardTitle className="text-base font-bold text-black p-4 pb-0">
                      Meeting {">"} View and manage all user meetings
                    </CardTitle>
                    <CardContent className="p-4">
                      <p className="text-black text-base">
                        <span className="font-medium">Select : </span>
                        Create a meeting for user, update a meeting, delete a meeting
                      </p>
                    </CardContent>
                  </Card>
                  <Card className="border rounded-2xl">
                    <CardTitle className="text-base font-bold text-black p-4 pb-0">
                      User {">"} View all user information
                    </CardTitle>
                    <CardContent className="p-4">
                      <p className="text-black text-base">
                        <span className="font-medium">Select : </span>
                        Select : user’s token, view a user and view users.
                      </p>
                    </CardContent>
                  </Card>
                </div>
                <Image
                  src={"/images/step-2.png"}
                  height={100}
                  width={100}
                  className="w-full h-full px-6"
                  alt={"Zoom logo"}
                />
              </div>
            </div>
          </div>
        </CardContent>
        <div className="flex items-center justify-end mb-8">
          <Button onClick={handleSubmit} backgroundColor="primary" className="justify-end px-8">
            Connect
          </Button>
        </div>
      </CardHeader>
    </Card>
  )
}

