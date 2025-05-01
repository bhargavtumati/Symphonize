import Link from 'next/link';
import { usePathname } from 'next/navigation';
import TooltipComponent from '../components/tooltip-component';
import {Plug, type LucideIcon } from 'lucide-react';



interface NavIconsProps {
    iconPath: string;
    textContent: string;
    Icon: LucideIcon;
  }
  
  export const NavIcons: React.FC<NavIconsProps> = ({ iconPath, textContent, Icon }) => {
    const pathName = usePathname();
    const isActive = pathName.includes(iconPath);
  
    return (
      <li  className="mb-0 text-xs">
        <Link href={iconPath} className='text-white no-underline'>
        <TooltipComponent
            icon={
              <div
                className={`${
                  isActive
                    ? "flex flex-col items-center justify-around text-center mt-2 pt-2 text-black bg-primary rounded-full text-white h-[48px] w-[48px] hover:none"
                    : "bg-slate-50 rounded-full text-white h-[48px] w-[48px] flex flex-col items-center justify-around text-center mt-2.5 pt-2.5 bg-[#f7f7f7] text-black hover:bg-[#e7ebeb]"
                }`}
                style={{ padding: "1.1em" }}
              >
                <Icon
                  className={`
                  ${isActive ? "text-white w-[24px] h-[24px]" : "text-[#94A3B8]"
                  } ${Icon === Plug ? "transform -rotate-[315deg]" : ""}`}
                />
              </div>
            }
            message={textContent} // Tooltip message
            tag="p" // You can change this to "span" or any other HTML element
            className="bg-primary text-white rounded-full h-7 justify-around mt-6 ml-8 text-[12px]" // Tooltip styling
          />
        </Link>
      </li>
    );
  };