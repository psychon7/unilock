'use client';

import React, { useState } from 'react';
import TopNavBar from '@/components/layout/TopNavBar';
import DomainSelector from '@/components/dashboard/DomainSelector';
import ApplicationsAndProviders from '@/components/dashboard/ApplicationsAndProviders';
import ThemingAndAdvanced from '@/components/dashboard/ThemingAndAdvanced';
import { Toaster as Sonner } from "@/components/ui/sonner";

const Dashboard = () => {
  const [selectedDomain, setSelectedDomain] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');

  const handleSearch = (query: string) => {
    setSearchQuery(query);
  };

  return (
    <div className="flex flex-col h-screen bg-gray-100">
      <TopNavBar onSearch={handleSearch} />
      <main className="flex flex-1 overflow-hidden p-4 gap-4">
        {/* Left Column: Domain Selector */}
        <div className="w-1/4 flex flex-col bg-white rounded-lg shadow overflow-y-auto">
          <DomainSelector 
            onSelectDomain={setSelectedDomain} 
            searchQuery={searchQuery}
          />
        </div>

        {/* Center Column: Applications & Identity Providers */}
        <div className="w-1/2 flex flex-col bg-white rounded-lg shadow overflow-y-auto p-4">
          <ApplicationsAndProviders selectedDomain={selectedDomain} />
        </div>

        {/* Right Column: Theming & Advanced */}
        <div className="w-1/4 flex flex-col bg-white rounded-lg shadow overflow-y-auto p-4">
          <ThemingAndAdvanced selectedDomain={selectedDomain} />
        </div>
      </main>
      <Sonner />
    </div>
  );
};

export default Dashboard;
