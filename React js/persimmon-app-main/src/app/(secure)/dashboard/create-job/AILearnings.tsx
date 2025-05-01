import React from 'react';
import { Card } from "@/components/ui/card";
import { Sparkles } from 'lucide-react';

const AILearnings = () => {
  return (
    <Card className="w-full md:w-[30%] bg-teal-50 p-6 rounded-lg border-green-200 h-full">
        <div className="mb-4">
          <div className="flex flex-col mb-4">
            <div className="flex items-center">
              <Sparkles className="text-green-400" />
              <h1 className="font-bold text-lg pl-2">Ai Learnings</h1>
            </div>
            <p className="text-gray-500 pl-7">Parameters considered in Matching Criteria</p>
          </div>
        </div>
        <ul className="space-y-8 px-8">
          <li className="flex items-center">
            <input
              type="checkbox"
              className="mr-2 accent-green-400 h-4 w-4"
            />
            <span>Job title is Node JS Developer</span>
          </li>
          <li className="flex items-center">
            <input
              type="checkbox"
              className="mr-2 accent-green-400 h-4 w-4"
            />
            <span>3 Years Experience required</span>
          </li>
          <li className="flex items-center">
            <input
              type="checkbox"
              className="mr-2 accent-green-400 h-4 w-4"
            />
            <span>Publish on Career page website</span>
          </li>
          <li className="flex items-center">
            <input
              type="checkbox"
              className="mr-2 accent-green-400 h-4 w-4"
            />
            <span>Publish on Career page website</span>
          </li>
          <li className="flex items-center">
            <input
              type="checkbox"
              className="mr-2 accent-green-400 h-4 w-4"
            />
            <span>3 Years Experience required</span>
          </li>
          <li className="flex items-center">
            <input
              type="checkbox"
              className="mr-2 accent-green-400 h-4 w-4"
            />
            <span>3 Years Experience required</span>
          </li>
          <li className="flex items-center">
            <input
              type="checkbox"
              className="mr-2 accent-green-400 h-4 w-4"
            />
            <span>3 Years Experience required</span>
          </li>
        </ul>

        <div className="mt-4 text-center pt-14">
          <p className="font-bold italic">Learning.....</p>
        </div>
      </Card>
  );
};

export default AILearnings;