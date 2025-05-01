import { CustomizationSettings } from '@/app/types/customization';
import { Settings } from 'lucide-react';
import React from 'react';

interface InfoItemProps {
  icon: React.ReactNode; // Accepts a React node (like an SVG or icon component)
  heading: string;
  message: string|undefined;
  settings: CustomizationSettings | null
}

const InfoItem: React.FC<InfoItemProps> = ({ icon, heading, message, settings }) => {
  return (
    <div className="flex items-center gap-2">
      <div className={`h-6 w-6 ${settings?.darkMode ? 'text-slate-300' : 'text-muted-foreground'}`}>{icon}</div>
      <div>
        <div className={`text-xs ${settings?.darkMode ? 'text-slate-300' : 'text-muted-foreground'}`}>{heading}</div>
        <div className="text-sm">{message}</div>
      </div>
    </div>
  );
};

export default InfoItem;
