"use client"
import React from 'react';
import CreateJobPage from "./create-job/listJobs";

const DashboardPage: React.FC = () => {
  return (
    <div className="w-full">
        <CreateJobPage />
    </div>
  );
};

export default DashboardPage;
