import { z } from 'zod';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { Card } from '@/components/ui/card';
import { Label } from '@/components/ui/label';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Upload } from 'lucide-react';
import { CustomizationSettings } from '@/app/types/customization';

// Zod Schema for validation
const applyFormSchema = z.object({
  phone: z.string().min(10, { message: "Phone number is required" }).regex(/^\+91\s\d{10}$/, {
    message: "Invalid phone number format",
  }),
  name: z.string().min(3, { message: "Full name is required" }),
  email: z.string().email({ message: "Please enter a valid email" }),
  linkedin: z.string().url({ message: "Please enter a valid LinkedIn profile URL" }).optional(),
  resume: z.any().refine((file) => file?.[0], {
    message: "Please upload a resume file",
  }),
});

interface ApplyFormProps {
  settings: CustomizationSettings
}

type ApplyFormData = z.infer<typeof applyFormSchema>;

const ApplyForm = ({ settings }: ApplyFormProps) => {
  const {
    register,
    formState: { errors },
  } = useForm<ApplyFormData>({
    resolver: zodResolver(applyFormSchema),
  });

  const cardClasses = settings.darkMode
    ? "bg-slate-800 text-white"
    : "bg-[#f8fafc] text-black";

  const inputClasses = settings.darkMode
    ? "bg-slate-700 text-white border-slate-400"
    : "bg-white text-black border-gray-300";

  return (
    <Card className={`border-none p-4 ${cardClasses}`} style={{ fontFamily: settings.fontStyle }}>
      <div>
        <h2 className="text-lg font-semibold mb-4">Apply For the Job</h2>
        <form className="space-y-4">
          <div className="flex gap-4">
            <div className="flex-2">
              <Label htmlFor="phone">Phone number</Label>
              <div className="relative">
                <Input
                  id="phone"
                  placeholder="+91 95422 99999"
                  {...register('phone')}
                  className={`pr-20 ${inputClasses}`}
                />
                <Button
                  style={{ backgroundColor: settings.primaryColor }}
                  className="absolute top-1/2 right-0.5 -translate-y-1/2 whitespace-nowrap h-8"
                  disabled={true}
                >
                  Send OTP
                </Button>
              </div>
              {errors.phone && <p className="text-red-500 text-sm">{errors.phone.message}</p>}
            </div>
          </div>

          <div className="grid md:grid-cols-2 gap-4">
            <div>
              <Label htmlFor="name">Full Name</Label>
              <Input id="name" placeholder="Enter your name" {...register('name')} className={inputClasses} />
              {errors.name && <p className="text-red-500 text-sm">{errors.name.message}</p>}
            </div>
            <div>
              <Label htmlFor="email">Email ID</Label>
              <Input id="email" type="email" placeholder="Enter your email" {...register('email')} className={inputClasses} />
              {errors.email && <p className="text-red-500 text-sm">{errors.email.message}</p>}
            </div>
          </div>

          <div>
            <Label htmlFor="linkedin">LinkedIn Profile</Label>
            <Input id="linkedin" placeholder="Enter LinkedIn Profile URL" {...register('linkedin')} className={inputClasses} />
            {errors.linkedin && <p className="text-red-500 text-sm">{errors.linkedin.message}</p>}
          </div>

          <div>
            <Label>Resume</Label>
            <div className={`border-2 border-solid rounded-lg p-6 text-center ${settings.darkMode ? 'border-slate-50 text-slate-50' : 'border-gray-300 text-muted-foreground'}`}>
              <Upload
                className="h-8 w-8 mx-auto mb-2"
              />
              <p className="text-sm mb-1">Choose a file or Drag and Drop here</p>
              <p className="text-xs">or Browse</p>
            </div>
          </div>

          <Button style={{ backgroundColor: settings.primaryColor }} type="submit" className="w-full" disabled={true}>
            Submit
          </Button>
        </form>
      </div>
    </Card>
  );
};

export default ApplyForm;

