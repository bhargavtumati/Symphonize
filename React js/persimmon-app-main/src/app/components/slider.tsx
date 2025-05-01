"use client";

import * as React from "react";
import {
  Carousel,
  CarouselContent,
  CarouselItem,
} from "@/components/ui/carousel";
import { Card, CardContent } from "@/components/ui/card";
import Autoplay from "embla-carousel-autoplay";
import Image from "next/image";

interface SlideContent {
  image: string;
  title: string;
  description: string;
  logo: string;
}

const slides: SlideContent[] = [
  {
    image: "/images/slider-2.png",
    title: "A One Stop Tool for Recruitment Management",
    description:
      "Effortlessly automate job postings, conduct in-depth applicant screenings, and manage the entire recruitment process from start to finish. All within a single, intuitive platform designed for recruiters",
    logo: "/images/Asset 2 3.png",
  },
  {
    image: "/images/slider-1.png",
    title: "AI-Powered Candidate Matching",
    description:
      "Leverage advanced AI algorithms to find the perfect match between job requirements and candidate profiles, saving time and improving hiring accuracy",
    logo: "/images/Asset 2 3.png",
  },
];

export function AuthSlider() {
  const plugin = React.useRef(
    Autoplay({ delay: 5000, stopOnInteraction: true })
  );

  return (
    <div className="flex h-full w-full bg-gradient-to-b from-custom_teal via-custom_blue to-custom_purple">
    <Carousel
      plugins={[plugin.current]}
      className="w-full"
      onMouseEnter={plugin.current.stop}
      onMouseLeave={plugin.current.reset}
    >
      <CarouselContent>
        {slides.map((slide, index) => (
          <CarouselItem key={index}>
            <Card className="border-none bg-transparent shadow-none">
              <CardContent className="flex flex-col justify-between gap-20 p-8">
                <div>
                  <Image
                    src={slide.logo}
                    alt="Company logo"
                    width={100}
                    height={100}
                    className="h-auto w-auto"
                  />
                </div>
                <div className="relative aspect-[5/3] w-full">
                  <Image
                    src={slide.image}
                    alt={slide.title}
                    fill
                    className="object-contain"
                  />
                </div>
                <div className="space-y-4 text-white">
                  <h2 className="text-2xl font-bold leading-tight">
                    {slide.title}
                  </h2>
                  <p className="text-sm/relaxed opacity-90">
                    {slide.description}
                  </p>
                </div>
              </CardContent>
            </Card>
          </CarouselItem>
        ))}
      </CarouselContent>
    
    </Carousel>
  </div>
  );
}
