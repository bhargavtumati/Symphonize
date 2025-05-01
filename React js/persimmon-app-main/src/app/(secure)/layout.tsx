"use client";
import React, { ReactNode, useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Image from 'next/image';
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { BriefcaseBusiness, Users, Building2, Bell, Plug } from 'lucide-react';
import { NavIcons } from '../components/nav-icons-component';
import DropdownMenuComponent from '../components/drop-down-menu-component';
import { signOut } from "firebase/auth";
import { auth } from "@/app/components/firebaseConfig";




interface DashboardProps {
  children: ReactNode;
}

const Dashboard: React.FC<DashboardProps> = ({ children }) => {
  const [userName, setUserName] = useState<string | null>(null);
  const router = useRouter();

  useEffect(() => {
    const storedUserName = sessionStorage.getItem("userEmail");
    setUserName(storedUserName);
  }, []);

  const firstLetter = userName ? userName.charAt(0).toUpperCase() : "";

  const handleLogout = async () => {
    try {
      router.push("/");
      await signOut(auth); // Firebase sign-out
      sessionStorage.clear(); // Clear session storage
    } catch (error) {
      console.error("Error during logout:", error);
    }
  };
  const menuOptions = [
    {
      label: "Logout",
      action: handleLogout,
    },
  ];

  return (
    <div className="grid grid-rows-[auto_1fr] grid-cols-[64px_1fr] min-h-screen max-h-max bg-[#F8FAFC]">
      <header className="col-span-full flex justify-between items-center px-5 bg-[#334155] text-white h-[60px] sticky fixed top-0 left-0 w-full z-50">
        <div className="flex items-center">
          <Image src="/images/Asset 2 3.png" className="h-8 mr-2.5" width={120} height={120} alt="Logo" />
        </div>
        <div className="flex items-center">
          <Bell className="mr-5 text-[10px] text-white h-[22px]" />
          <div className="bg-[#f0f0f0] rounded-full w-10 h-7 flex items-center justify-center cursor-pointer">
            <DropdownMenuComponent
              triggerLabel={
                <Avatar>
                  <AvatarFallback className="text-[#333] text-[16px]">
                    {firstLetter}
                  </AvatarFallback>
                </Avatar>
              }
              menuOptions={menuOptions}
            />
          </div>
        </div>
      </header>
      <nav className={`row-span-[span 2 / span -1] bg-white text-white flex flex-col items-center pt-1 max-w-[64px] pl-2`}>
        <ul className="list-none p-0 m-0 w-full">
          <NavIcons iconPath="/dashboard" textContent="Jobs" Icon={BriefcaseBusiness} />
          <NavIcons iconPath="/integrations" textContent="Integrations" Icon={Plug} />
          <NavIcons iconPath="/applicants" textContent="Applicants" Icon={Users} />
          <NavIcons iconPath="/organization" textContent='Company' Icon={Building2} />
        </ul>
      </nav>
      <main className="bg-[#F8FAFC] text-black min-h-screen h-fit w-full max-w-[1440px] mx-auto px-8 box-border">
        {children}
      </main>
    </div>
  );
};

export default Dashboard;

