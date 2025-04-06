'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import api from '@/services/api';
import { Button } from '@/components/ui/button';
import { showToast } from '@/lib/toast';

interface Domain {
  id: number;
  name: string;
  display_name: string;
  description?: string;
}

interface DomainSelectorProps {
  onSelectDomain: (domainName: string | null) => void;
  searchQuery?: string;
}

const DomainSelector: React.FC<DomainSelectorProps> = ({ onSelectDomain, searchQuery }) => {
  const [domains, setDomains] = useState<Domain[]>([]);
  const [filteredDomains, setFilteredDomains] = useState<Domain[]>([]);
  const [selectedDomainName, setSelectedDomainName] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  useEffect(() => {
    const fetchDomains = async () => {
      try {
        setLoading(true);
        const response = await api.get('/api/v1/domains');
        setDomains(response.data.domains);
        setError(null);
      } catch (err) {
        console.error("Error fetching domains:", err);
        showToast.error('Failed to load domains.');
        setError('Failed to load domains.');
        setDomains([]); // Clear domains on error
      } finally {
        setLoading(false);
      }
    };

    fetchDomains();
  }, []);

  useEffect(() => {
    if (!searchQuery) {
      setFilteredDomains(domains);
      return;
    }

    const query = searchQuery.toLowerCase();
    const filtered = domains.filter(domain => 
      domain.name.toLowerCase().includes(query) || 
      domain.display_name.toLowerCase().includes(query) ||
      (domain.description && domain.description.toLowerCase().includes(query))
    );
    setFilteredDomains(filtered);
  }, [domains, searchQuery]);

  const handleSelect = (domainName: string) => {
    setSelectedDomainName(domainName);
    onSelectDomain(domainName);
  };

  return (
    <div className="p-4 h-full flex flex-col">
      <h2 className="text-lg font-semibold mb-4 border-b pb-2">Domains</h2>
      {loading && <p className="text-gray-500">Loading domains...</p>}
      {error && <p className="text-red-500">{error}</p>}
      {!loading && !error && (
        <ul className="flex-1 overflow-y-auto space-y-2 mb-4">
          {filteredDomains.length === 0 ? (
            <li className="text-gray-500 text-center py-4">
              {searchQuery ? 'No domains match your search' : 'No domains found'}
            </li>
          ) : (
            filteredDomains.map((domain) => (
              <li key={domain.id}>
                <button
                  onClick={() => handleSelect(domain.name)}
                  className={`w-full text-left p-2 rounded hover:bg-gray-100 ${
                    selectedDomainName === domain.name ? 'bg-blue-100 font-medium' : ''
                  }`}
                >
                  <div className="font-semibold">{domain.display_name}</div>
                  <div className="text-sm text-gray-600">{domain.name}</div>
                  {domain.description && <div className="text-xs text-gray-500 mt-1">{domain.description}</div>}
                </button>
              </li>
            ))
          )}
        </ul>
      )}
      <div className="mt-auto pt-4 border-t">
        <Button 
          className="w-full"
          onClick={() => router.push('/domains/new')}
        >
          + Add Domain
        </Button>
      </div>
    </div>
  );
};

export default DomainSelector;
