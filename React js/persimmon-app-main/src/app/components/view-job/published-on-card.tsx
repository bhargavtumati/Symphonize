import { PublishedOnCardProps } from "@/app/types";
import { Card } from "@/components/ui/card";
import { Check, Eye, Globe, Pencil, X } from "lucide-react";
import { useEffect, useState } from "react";
import Image from "next/image";
import { Switch } from "@/components/ui/switch";

type ViewKeys = keyof PublishedOnCardProps["views"];
export const PublishedOnCard: React.FC<PublishedOnCardProps> = ({
    views,
    setViews,
  }) => {
    const [isEditMode, setIsEditMode] = useState(false);
    const [currentViews, setCurrentViews] = useState(views); // Track current toggle states
  
    useEffect(() => {
      setCurrentViews(views); // Sync current views with props whenever views change
    }, [views]);
  
    const handleToggleChange = (label: ViewKeys, value: boolean) => {
      setCurrentViews((prev) => ({
        ...prev,
        [label]: !currentViews[label], // Toggle the value
      }));
    };
  
    const confirmChanges = () => {
      (Object.keys(currentViews) as ViewKeys[]).forEach((key) => {
        setViews(key, !currentViews[key]); // Call setViews correctly with valid key
      });
      setIsEditMode(false);
    };
  
    const cancelChanges = () => {
      setCurrentViews(views); // Revert to original views
      setIsEditMode(false);
    };
  
    return (
      <Card className="bg-white px-6 py-4 rounded-lg mt-4 h-fit  border-none">
        <div className="flex justify-between items-center mb-14">
          <h2 className="text-lg font-medium">Published on</h2>
          <div className="flex">
            {isEditMode ? (
              <>
                <Card className="p-2 mr-2" onClick={cancelChanges}>
                  <X className="text-red-500 cursor-pointer w-4 h-4 stroke-[3]" />
                </Card>
                <Card className="p-2" onClick={confirmChanges}>
                  <Check className="text-green-500 cursor-pointer w-4 h-4 stroke-[3]" />
                </Card>
              </>
            ) : (
              <button
                className="p-2"
                type="button"
                onClick={() => setIsEditMode(true)}
              >
                <Pencil className="text-black-500 cursor-pointer w-5 h-5 stroke-[2]" />{" "}
                {/* Replace with edit icon */}
              </button>
            )}
          </div>
        </div>
  
        <div className="space-y-2 mt-0">
          {[
            // List of job boards
            {
              icon: <Globe className="text-slate-500" />,
              label: "Career Page",
              view: currentViews.careerPageView,
              name: "careerPageView",
            },
            {
              icon: (
                <Image
                  src="/images/view_job_page/persimmon_logo.png"
                  alt="Persimmon Icon"
                  width={24}
                  height={24}
                  className="object-contain"
                />
              ),
              label: "Persimmon",
              view: currentViews.persimmonView,
              name: "persimmonView",
            },
            {
              icon: (
                <Image
                  src="\images\view_job_page\indeed_b_logo.png"
                  alt="Indeed Icon"
                  width={24}
                  height={24}
                  className="object-contain"
                />
              ),
              label: "Indeed",
              view: currentViews.Indeed,
              name: "Indeed",
            },
            {
              icon: (
                <Image
                  src="\images\view_job_page\linkedin_logo.png"
                  alt="LinkedIn Icon"
                  width={24}
                  height={24}
                  className="object-contain"
                />
              ),
              label: "Linkedin",
              view: currentViews.linkedInView,
              name: "linkedInView",
            },
            {
              icon: (
                <Image
                  src="\images\view_job_page\monster_logo.png"
                  alt="Monster Job Icon"
                  width={24}
                  height={24}
                  className="object-contain"
                />
              ),
              label: "Monster Jobs",
              view: currentViews.monsterJobsView,
              name: "monsterJobsView",
            },
            {
              icon: (
                <Image
                  src="\images\view_job_page\hirist_logo.png"
                  alt="Hirist Icon"
                  width={24}
                  height={24}
                  className="object-contain transform scale-[2]"
                />
              ),
              label: "hirist",
              view: currentViews.hiristIconView,
              name: "hiristIconView",
            },
            {
              icon: (
                <Image
                  src="\images\view_job_page\google_logo.png"
                  alt="Google Icon"
                  width={24}
                  height={24}
                  className="object-contain"
                />
              ),
              label: "Google",
              view: currentViews.googleView,
              name: "googleView",
            },
          ].map((item, index) => (
            <div key={index} className="py-2">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <div className="text-xl">{item.icon}</div>
                  <p>{item.label}</p>
                </div>
                {isEditMode ? (
                  <Switch
                    checked={item.view}
                    onCheckedChange={() =>
                      handleToggleChange(item.name as ViewKeys, item.view)
                    } // Cast label to ViewKeys
                    style={{
                      backgroundColor: item.view ? "#22C55E" : "#D1D5DB", // Green for "on", Gray for "off"
                    }}
                  />
                ) : (
                  <span>
                    {item.view ? (
                      <div className="flex">
                        <Eye className="text-blue-600 mr-1" />
                        <span>View</span>
                      </div>
                    ) : (
                      ""
                    )}
                  </span> // Display status when not in edit mode
                )}
              </div>
              {index < 6 && <hr className="border-gray-1 mt-6 w-full" />}
            </div>
          ))}
        </div>
      </Card>
    );
  };