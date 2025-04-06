'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import api from '@/services/api';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { showToast } from '@/lib/toast';
import { AxiosError } from 'axios';

interface FormErrors {
  domainName?: string;
  displayName?: string;
}

const AddDomainWizard = () => {
  const [domainName, setDomainName] = useState('');
  const [displayName, setDisplayName] = useState('');
  const [description, setDescription] = useState('');
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState<FormErrors>({});
  const router = useRouter();

  const validateForm = (): boolean => {
    const newErrors: FormErrors = {};

    if (!domainName) {
      newErrors.domainName = 'Domain name is required';
    } else if (!/^[a-z0-9-]+$/.test(domainName)) {
      newErrors.domainName = 'Domain name can only contain lowercase letters, numbers, and hyphens';
    }

    if (!displayName) {
      newErrors.displayName = 'Display name is required';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async () => {
    if (!validateForm()) {
      return;
    }

    setLoading(true);
    try {
      await api.post('/api/v1/domains', {
        domain_name: domainName,
        display_name: displayName,
        description: description || undefined // Only include if not empty
      });
      showToast.success('Domain created successfully');
      router.push(`/dashboard`);
    } catch (err) {
      console.error('Error creating domain:', err);
      if (err instanceof AxiosError) {
        showToast.error(
          err.response?.data?.detail || 
          'Failed to create domain. Please try again.'
        );
      } else {
        showToast.error('An unexpected error occurred. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-lg mx-auto bg-white rounded-lg shadow-md p-6">
        <h1 className="text-2xl font-bold mb-6">Add Domain</h1>
        
        <div className="space-y-4">
          <div>
            <Label htmlFor="domainName">Domain Name</Label>
            <Input
              id="domainName"
              type="text"
              value={domainName}
              onChange={e => setDomainName(e.target.value)}
              placeholder="e.g., my-domain"
              className={errors.domainName ? 'border-red-500' : ''}
            />
            {errors.domainName && (
              <p className="mt-1 text-sm text-red-500">{errors.domainName}</p>
            )}
            <p className="mt-1 text-sm text-gray-500">
              This will be used as the Keycloak realm name and cannot be changed later.
            </p>
          </div>

          <div>
            <Label htmlFor="displayName">Display Name</Label>
            <Input
              id="displayName"
              type="text"
              value={displayName}
              onChange={e => setDisplayName(e.target.value)}
              placeholder="e.g., My Domain"
              className={errors.displayName ? 'border-red-500' : ''}
            />
            {errors.displayName && (
              <p className="mt-1 text-sm text-red-500">{errors.displayName}</p>
            )}
            <p className="mt-1 text-sm text-gray-500">
              A friendly name that will be displayed in the UI.
            </p>
          </div>

          <div>
            <Label htmlFor="description">Description (Optional)</Label>
            <Input
              id="description"
              type="text"
              value={description}
              onChange={e => setDescription(e.target.value)}
              placeholder="e.g., Domain for internal applications"
            />
          </div>

          <div className="flex justify-end space-x-3 pt-4">
            <Button
              variant="ghost"
              onClick={() => router.back()}
              disabled={loading}
            >
              Cancel
            </Button>
            <Button
              onClick={handleSubmit}
              disabled={loading}
            >
              {loading ? 'Creating...' : 'Create Domain'}
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AddDomainWizard;
