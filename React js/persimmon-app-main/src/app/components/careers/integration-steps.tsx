"use client";

import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Step } from "@/app/components/careers/step";
import { CodeSnippet } from "@/app/components/careers/code-snippet";
import { CustomizationUI } from "@/app/components/careers/career-modal";
import { CustomizationSettings } from "@/app/types/customization";
import { Input } from "@/components/ui/input";
import { Label } from "@radix-ui/react-label";
import { apiService } from "@/app/api/service";
import { getCurrentUserEmail } from "../AuthProvider";

interface IntegrationStepsProps {
  settings: CustomizationSettings;
  onSettingsChange: (settings: CustomizationSettings) => void;
  domain?: string
}

export function IntegrationSteps({
  settings,
  onSettingsChange,
  domain
}: IntegrationStepsProps) {
  const [hasCopied, setHasCopied] = useState(false);
  const [iframeCode, setIframeCode] = useState<string | null>(null);
  const [isCustomizing, setIsCustomizing] = useState(false);
  const [careerPageUrl, setCareerPageUrl] = useState(settings.careerPageUrl);


  useEffect(() => {
    const fetchCareerPageData = async () => {
      try {
        const userEmail = (await getCurrentUserEmail()) as string;
        const CompanyDomain = userEmail.split("@")[1];
        const response = await apiService(`/careerpage/customization/domain/${CompanyDomain}`, "GET", null);
        setCareerPageUrl(response.data.career_page_url);
        console.log("response.career_page_url: ", response.career_page_url)
      } catch (error) {
        console.error("Error fetching data:", error);
      }
    };
  
    fetchCareerPageData();
  }, [domain]); // Add dependencies if needed
  

  useEffect(() => {
    if (domain) {
      setIframeCode(
        `<iframe id="dynamicIframe"
  width="100%"
  height="100vh"
  style="border:0px solid #ccc; min-height: 100vh; height: 100%;"
  sandbox="allow-scripts allow-same-origin allow-forms allow-popups allow-top-navigation"
  loading="lazy"
></iframe>
<script async defer src="https://otpless.com/v3/ancestorsCommunication.js"></script>
<script>
  function getQueryParam(param) {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get(param);
  }
  const jobURL = getQueryParam("jobURL");
  const defaultValue ="${process.env.NEXT_PUBLIC_FE_URL}/connection/${domain}"
  document.getElementById("dynamicIframe").src = jobURL || defaultValue;
</script>`
      );
    }
  }, [domain]);

  const copyCode = async () => {
    if (iframeCode) {
      await navigator.clipboard.writeText(iframeCode);
      setHasCopied(true);
      setTimeout(() => setHasCopied(false), 2000);
    }
  };

  const handleCareerPageUrlBlur = async () => {
    if (careerPageUrl) {
      try {
        const formData = new FormData();
        formData.append("career_page_url", careerPageUrl);
        const response = await apiService(`/careerpage/customization/domain/${domain}`, "POST", formData, true)
      } catch (error) {
        console.error("Error updating career page URL:", error)
        // You can add error handling logic here, such as showing an error message
      }
    }
  }

  const handleCustomize = (newSettings: CustomizationSettings) => {
    onSettingsChange(newSettings);
  };

  if (isCustomizing) {
    return (
      <div className="space-y-6">
        <CustomizationUI
          settings={settings}
          onSettingsChange={handleCustomize}
          onBack={() => setIsCustomizing(false)}
          careerPageUrl={careerPageUrl}
        />
      </div>
    );
  }

  return (
    <div className="space-y-10">
      <Step
        number={1}
        title="Create a career page on your website"
        description="Example: www.companyname.com/careers"
      />
      <Step
        number={2}
        title="Please paste your career page link"
        content={
          <div className="p-0 m-0">
            <Label className="font-medium text-sm		text-[#0F172A]">URL</Label>
            <Input
              type="text"
              placeholder="eg: www.companyname.com/careers"
              className="h-10"
              value={careerPageUrl}
              onChange={(e) => setCareerPageUrl(e.target.value)}
              onBlur={handleCareerPageUrlBlur}
            />
          </div>
        }
      />
      <Step
        number={3}
        title="Create an i-frame on your career page and embed the code"
        content={
          <CodeSnippet
            code={
              iframeCode || (
                <div
                  style={{
                    display: "flex",
                    justifyContent: "center",
                    alignItems: "center",
                    height: "100%",
                    textAlign: "center",
                  }}
                >
                  Loading...
                </div>
              )
            }
            onCopy={copyCode}
            hasCopied={hasCopied}
          />
        }
      />
      <Step
        number={4}
        title="Customize your career page with your brand style"
        description="Change colors, fonts, styles etc."
        content={
          <Button
            className="bg-primary ml-[270px]"
            onClick={() => setIsCustomizing(true)}
          >
            Customize
          </Button>
        }
      />
    </div>
  );
}
