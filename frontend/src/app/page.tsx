'use client'; // Add this directive for client-side hooks like useState and useEffect

import React, { useEffect, useState } from 'react';
import Link from 'next/link'; // Use next/link for client-side navigation
import api from '../services/api'; // Assuming api.ts is in src/services

// Define an interface for the domain object if you know its structure
interface Domain {
  id: string; // or number, depending on your API
  name: string;
  display_name?: string;
}

export default function Dashboard() {
  const [domains, setDomains] = useState<Domain[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api.get<Domain[]>('/domains')
      .then((res) => {
        setDomains(res.data);
        setLoading(false);
      })
      .catch((err) => {
        console.error("Error fetching domains:", err);
        setError(typeof err === 'string' ? err : 'Failed to load domains.');
        setLoading(false);
      });
  }, []); // Empty dependency array means this runs once on mount

  return (
    <div className="container mx-auto p-4 pt-10">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">Domains</h1>
        {/* Link to the Add Domain page/wizard - we'll create this page next */}
        <Link href="/domains/new"
              className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded">
          Add Domain
        </Link>
      </div>

      {loading && <p>Loading domains...</p>}
      {error && <p className="text-red-500">Error: {error}</p>}

      {!loading && !error && (
        <ul className="space-y-2">
          {domains.length === 0 ? (
            <p>No domains found. Add one!</p>
          ) : (
            domains.map((d) => (
              <li key={d.id} className="border p-3 rounded shadow-sm hover:bg-gray-50">
                {/* Link to the domain details page - needs implementation */}
                <Link href={`/domains/${d.id}`} className="text-blue-600 hover:underline">
                  {d.display_name || d.name}
                </Link>
                <span className="text-gray-500 text-sm ml-2">(ID: {d.id})</span>
              </li>
            ))
          )}
        </ul>
      )}
    </div>
  );
}
