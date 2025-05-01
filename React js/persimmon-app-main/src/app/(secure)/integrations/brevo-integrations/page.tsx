"use client"

import { useEffect, useState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card"
import Image from "next/image"
import { ArrowLeft, ArrowLeftRight, Loader2 } from "lucide-react"
import { useToast } from "@/components/hooks/use-toast"
import { apiService } from "@/app/api/service"
import { useRouter } from "next/navigation"
import StepInstruction from "@/app/components/stepInstruction"
import IntegrationStatus from "@/app/components/integration-status"


export default function BrevoIntegrations() {
  const router = useRouter()
  const [apikey, setApiKey] = useState("")
  const [verifyStatus, setVerifyStatus] = useState(false)
  const [loading, setLoading] = useState(true)
  const { toast } = useToast()

  const handleRowClick = () => {
    router.push("/integrations")
  }

  useEffect(() => {
    const checkVerifyStatus = async (name: string) => {
      try {
        const status = await apiService(`/integration/email/${name}/verify-status`, "GET", null)
        setVerifyStatus(status)
        console.log(status)

      } catch (error) {
        toast({
          variant: "destructive",
          title: "Not verified",
          description: error instanceof Error ? error.message : "An unexpected error occurred",
        })
      }
      finally {
        setLoading(false)
      }
    }
    checkVerifyStatus("brevo")
  }, [])
  const handleBrevoIntegration = async (apikey: string, name: string) => {
    try {
      const payload = { api_key: apikey.trim() }
      const response = await apiService(`/integration/email/${name}`, "POST", payload)
      if (!response) {
        throw new Error("API call failed")
      }
      setVerifyStatus(true)
      toast({
        variant: "default",
        title: "Success",
        description: "Brevo integration successful",
        duration: 2000,
      })

    } catch (error) {
      console.error("Brevo integration error:", error)
      toast({
        variant: "destructive",
        title: "Error",
        description: error instanceof Error ? error.message : "An unexpected error occurred",
        duration: 3000,
      })
    }
    finally {
      setLoading(false)
    }
  }
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!apikey.trim()) {
      toast({
        variant: "destructive",
        title: "Error",
        description: "API Key is required",
      })
      return
    }
    handleBrevoIntegration(apikey, "brevo")
  }

  if (loading) {
    return (
      <div className="loader absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 flex items-center justify-center">
        <Loader2 className="mr-2 h-[30px] w-12 animate-spin" />
      </div>
    )
  }
  const handleGetKey = async (name: string) => {
    try {
      const response = await apiService(`/integration/email/${name}/api_key`, "GET", null);
      if (response.api_key) {
        setApiKey(response.api_key);
      } else {
        throw new Error("API key not found")
      }
    } catch (error) {
      toast({
        variant: "destructive",
        title: "Error",
        description: error instanceof Error ? error.message : "An unexpected error occurred",
      });
    }
  };

  if (verifyStatus) {
    return (
      <IntegrationStatus
        imageSrc="/images/brevo.png"
        description="Manage your Brevo connection to send emails seamlessly."
        editPath="integrations/brevo-integrations"
        handleEditClick={() => {
          setVerifyStatus(false)
          handleGetKey("brevo");
        }}
      />
    );
  }

  return (
    <Card className="my-8 max-w-4xl p-2 cursor-pointer" >
      <CardHeader>
        <div className="flex text-xl semibold leading-7 text-black">
          <span onClick={handleRowClick} className="flex space-x-2 ">
            <ArrowLeft className="w-6 h-6 cursor-pointer " />{" "}
            <CardTitle>Brevo Integration</CardTitle>
          </span>
        </div>
        <CardDescription className="text-base text-slate-500 space-x-2">
          Connect your Brevo account to send emails seamlessly within Persimmon.
        </CardDescription>
        <CardContent className="space-y-4 p-0">
          <div>
            <div className="flex items-center space-x-2 mt-4">
              <Image src={"/images/brevo.png"} height={32} width={109} alt={"Brevo logo"} />
              <ArrowLeftRight strokeWidth={2} className="mt-3" />
              <Image src="/images/persimmon-full-icon.svg" height={36} width={155} alt={"Perssimon logo"} className="mt-2" />
            </div>
            <div className="p-6">
              <StepInstruction
                stepNumber={1}
                description={
                  <span>
                    Go to{" "}
                    <a
                      href="https://onboarding.brevo.com/account/register"
                      className="text-base text-blue-500 hover:underline"
                      target="_blank"
                      rel="noopener noreferrer"
                    >
                      https://onboarding.brevo.com/account/register
                    </a>
                    {""} and Signup
                  </span>
                }
                imageSrc={"/images/brevo-step1.png"}
              />

              <div className="space-x-2 pt-6">
                <StepInstruction
                  stepNumber={2}
                  description={
                    <span>
                      In the home page click on top-right corner, then click on  <span className="text-base font-bold">SMTP & API</span>
                    </span>
                  }
                  imageSrc={"/images/brevo-step2.png"}
                />
              </div>
              <div className="space-x-2 pt-6">
                <StepInstruction
                  stepNumber={3}
                  description={
                    <span>
                      Go to <span className="text-base font-bold">API Key</span>
                    </span>
                  }
                  imageSrc={"/images/brevo-step3.png"}
                />
              </div>
              <div className="space-x-2 pt-6">
                <StepInstruction
                  stepNumber={4}
                  description={
                    <span>
                      Click on <span className="text-base font-bold">Generate a new API key</span> and give a name to it
                    </span>
                  }
                  imageSrc={"/images/brevo-step4.png"}
                />
              </div>

              <div className="space-x-2 pt-6">
                <StepInstruction
                  stepNumber={5}
                  description="copy your API key"
                  imageSrc={"/images/brevo-step5.png"}
                />
              </div>
              <div className="space-x-8 pt-6">
                <StepInstruction
                  stepNumber={6}
                  description="Paste API Key Here"
                  content={
                    <div className="space-y-2 mt-2">
                      <Label className="text-sm font- medium text-black">API Key</Label>
                      <div className="flex gap-2">
                        <Input
                          id="apiKey"
                          placeholder="Enter your API Key"
                          className="bg-white flex-1 h-10 w-64"
                          autoComplete="off"
                          value={apikey}
                          onChange={(e) => setApiKey(e.target.value)}
                        />
                      </div>
                    </div>
                  }
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

