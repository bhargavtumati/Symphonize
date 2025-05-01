"use client";

import { useEffect, useState } from "react";
import { Card } from "@/components/ui/card";
import { IntegrationSteps } from "@/app/components/careers/integration-steps";
import { PreviewSection } from "@/app/components/careers/preview-section";
import { CustomizationSettings } from "@/app/types/customization";
import { apiService } from "@/app/api/service";
import { getCurrentUserEmail } from "../AuthProvider";
import { ArrowLeft } from "lucide-react";
import { useRouter } from "next/navigation";

const initialSettings: CustomizationSettings = {
  coverImage:
    "https://images.unsplash.com/photo-1662643500140-7c2fdf816dd2?q=80&w=1470&auto=format&fit=crop",
  heading: "Join Us",
  description:
    "Explore opportunities that empower you to grow, innovate, and make an impact. Join a team where your talents are valued, your ideas are heard, and your career aspirations become a reality. Let's build the future together!",
  darkMode: false,
  primaryColor: "#0EA5E9",
  fontStyle: "Open Sans",
  allPrimaryColors: ["#F97316", "#0EA5E9", "#22C55E", "#EF4444", "#A855F7"],
  showCover: true,
  icon: null,
  iconLink: "",
  headerColor: "#0EA5E9",
  headerColors: ["#F97316", "#0EA5E9", "#22C55E", "#EF4444", "#A855F7"],
  careerPageUrl: "",
};

export function CareerIntegration() {
  const [domain, setDomain] = useState<string>("");
  const [loading, setLoading] = useState<boolean>(false);
  const [settings, setSettings] = useState<CustomizationSettings>(initialSettings);
  const router = useRouter();

  useEffect(() => {
    const fetchSettings = async () => {
      setLoading(true);
      try {
        const userEmail = (await getCurrentUserEmail()) as string;
        const CompanyDomain = userEmail.split("@")[1];
        setDomain(CompanyDomain);
        const response = await apiService(
          `/careerpage/customization/domain/${CompanyDomain}`
        );
        if (response.data) {
          setSettings((prevSettings) => ({
            ...prevSettings,
            heading: response.data.heading || prevSettings.heading,
            fontStyle: response.data.font_style || prevSettings.fontStyle,
            coverImage: response.data.image_data
              ? `data:image/jpeg;base64,${response.data.image_data}`
              : prevSettings.coverImage,
            description: response.data.description || prevSettings.description,
            primaryColor:
              response.data.color_selected || prevSettings.primaryColor,
            allPrimaryColors:
              response.data.primary_colors || prevSettings.allPrimaryColors,
            darkMode: response.data.enable_dark_mode || prevSettings.darkMode,
            showCover:
              response.data.enable_cover_photo || prevSettings.showCover,
            icon: response.data.logo_data
              ? `data:image/jpeg;base64,${response.data.logo_data}`
              : prevSettings.icon,
            iconLink: response.data.website_url || prevSettings.iconLink,
            headerColor:
              response.data.selected_header_color || prevSettings.headerColor,
            headerColors:
              response.data.header_colors || prevSettings.headerColors,
            careerPageUrl:
              response.data.career_page_url || prevSettings.careerPageUrl,
          }));
        }
      } catch (error) {
        console.error("Error fetching settings:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchSettings();
    console.log("api call settings", settings);
  }, []);

  const handleSettingsChange = (newSettings: CustomizationSettings) => {
    setSettings(newSettings);
  };

  const handleRoute = () => {
    router.push("/integrations");
  };

  return (
    <div className="min-h-screen p-6">
      <div className="flex text-xl font-semibold leading-7 tracking-tight mb-6">
        <span onClick={handleRoute} className="flex space-x-2">
          <ArrowLeft className="w-6 h-6 mt-[2px]" />{" "}
          <span>Career Page Integration</span>
        </span>
      </div>
      <div className="grid lg:grid-cols-1 xl:grid-cols-[420px,1fr] gap-8">
        <div className="w-full">
          <Card className="p-6 border-none">
            <IntegrationSteps
              settings={settings}
              onSettingsChange={handleSettingsChange}
              domain={domain}
            />
          </Card>
        </div>
        <div className="w-full overflow-hidden">
          <PreviewSection settings={settings} domain={domain} />
        </div>
      </div>
    </div>
  );
}
