'use client';

import React, { useState, useEffect } from 'react';
import api from '@/services/api';
import { showToast } from '@/lib/toast';
import { AxiosError } from 'axios';
import { Button } from '@/components/ui/button';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';

interface ThemingAndAdvancedProps {
  selectedDomain: string | null;
}

interface ThemeConfig {
  logoUrl?: string;
  primaryColor: string;
  secondaryColor: string;
  loginTheme?: string;
}

const ThemingAndAdvanced: React.FC<ThemingAndAdvancedProps> = ({ selectedDomain }) => {
  const [themeConfig, setThemeConfig] = useState<ThemeConfig>({
    primaryColor: '#3b82f6',
    secondaryColor: '#6b7280',
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!selectedDomain) {
      setThemeConfig({ primaryColor: '#3b82f6', secondaryColor: '#6b7280' });
      setError(null);
      return;
    }

    const fetchTheme = async () => {
      setLoading(true);
      setError(null);
      try {
        const response = await api.get(`/api/v1/domains/${selectedDomain}/theme`);
        setThemeConfig(response.data);
      } catch (err) {
        console.error(`Error fetching theme for domain ${selectedDomain}:`, err);
        setError(`Failed to load theme for ${selectedDomain}.`);
        setThemeConfig({ primaryColor: '#3b82f6', secondaryColor: '#6b7280' });
      } finally {
        setLoading(false);
      }
    };

    fetchTheme();
  }, [selectedDomain]);

  const handleThemeSave = async () => {
    if (!selectedDomain) return;

    try {
      await api.put(`/api/v1/domains/${selectedDomain}/theme`, themeConfig);
      showToast.success('Theme settings saved successfully');
    } catch (err: unknown) {
      console.error('Failed to save theme:', err);
      if (err instanceof AxiosError) {
        showToast.error(
          err.response?.data?.detail || 
          'Failed to save theme settings. Please try again.'
        );
      } else {
        showToast.error('An unexpected error occurred. Please try again.');
      }
    }
  };

  const handleLogoUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file || !selectedDomain) return;

    const formData = new FormData();
    formData.append('logo', file);

    try {
      const response = await api.post(`/api/v1/domains/${selectedDomain}/theme/logo`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      setThemeConfig(prev => ({ ...prev, logoUrl: response.data.url }));
      showToast.success('Logo uploaded successfully');
    } catch (err: unknown) {
      console.error('Failed to upload logo:', err);
      if (err instanceof AxiosError) {
        showToast.error(
          err.response?.data?.detail || 
          'Failed to upload logo. Please try again.'
        );
      } else {
        showToast.error('An unexpected error occurred. Please try again.');
      }
    }
  };

  if (!selectedDomain) {
    return <div className="text-center text-gray-500 pt-10">Select a domain to manage its theme and settings.</div>;
  }

  if (loading) {
    return <div className="text-center text-gray-500 pt-10">Loading theme & settings for {selectedDomain}...</div>;
  }

  if (error) {
    return <div className="text-center text-red-500 pt-10">{error}</div>;
  }

  return (
    <div className="space-y-6 h-full flex flex-col">
      {/* Theming Section */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg font-semibold">Theming & Branding</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center space-x-4">
            <div className="w-16 h-16 bg-gray-200 flex items-center justify-center rounded">
              {themeConfig.logoUrl ? (
                <img src={themeConfig.logoUrl} alt="Logo Preview" className="max-w-full max-h-full object-contain" />
              ) : (
                <span className="text-xs text-gray-500">Logo</span>
              )}
            </div>
            <div>
              <Label htmlFor="logoUpload">Upload Logo</Label>
              <Input
                id="logoUpload"
                type="file"
                accept="image/*"
                onChange={handleLogoUpload}
                className="text-sm"
              />
            </div>
          </div>

          <div className="flex items-center space-x-4">
            <Label htmlFor="primaryColor">Primary Color</Label>
            <Input
              id="primaryColor"
              type="color"
              value={themeConfig.primaryColor}
              onChange={(e) => setThemeConfig(prev => ({ ...prev, primaryColor: e.target.value }))}
              className="w-10 h-10 p-0 border-none"
            />
            <span>{themeConfig.primaryColor}</span>
          </div>

          <div className="flex items-center space-x-4">
            <Label htmlFor="secondaryColor">Secondary Color</Label>
            <Input
              id="secondaryColor"
              type="color"
              value={themeConfig.secondaryColor}
              onChange={(e) => setThemeConfig(prev => ({ ...prev, secondaryColor: e.target.value }))}
              className="w-10 h-10 p-0 border-none"
            />
            <span>{themeConfig.secondaryColor}</span>
          </div>

          <Button onClick={handleThemeSave} className="w-full">Save Theme</Button>
        </CardContent>
      </Card>

      {/* Advanced Settings Section */}
      <Card className="flex-1 flex flex-col">
        <CardHeader>
          <CardTitle className="text-lg font-semibold">Advanced Settings</CardTitle>
        </CardHeader>
        <CardContent className="flex-1 overflow-y-auto pt-0">
          <Tabs defaultValue="flows" className="w-full">
            <TabsList className="grid w-full grid-cols-3">
              <TabsTrigger value="flows">Flows</TabsTrigger>
              <TabsTrigger value="mappers">Mappers</TabsTrigger>
              <TabsTrigger value="policies">Policies</TabsTrigger>
            </TabsList>
            <TabsContent value="flows" className="pt-4 text-sm text-gray-600">
              <div className="space-y-2">
                <h3 className="font-medium">Authentication Flows</h3>
                <p>Configure authentication flows in the native Keycloak console.</p>
              </div>
            </TabsContent>
            <TabsContent value="mappers" className="pt-4 text-sm text-gray-600">
              <div className="space-y-2">
                <h3 className="font-medium">Protocol Mappers</h3>
                <p>Configure protocol mappers in the native Keycloak console.</p>
              </div>
            </TabsContent>
            <TabsContent value="policies" className="pt-4 text-sm text-gray-600">
              <div className="space-y-2">
                <h3 className="font-medium">Authorization Policies</h3>
                <p>Configure authorization policies in the native Keycloak console.</p>
              </div>
            </TabsContent>
          </Tabs>

          <div className="mt-4 pt-4 border-t">
            <a
              href={`${process.env.NEXT_PUBLIC_KEYCLOAK_URL}/admin/${selectedDomain}/console`}
              target="_blank"
              rel="noopener noreferrer"
              className="text-sm text-blue-600 hover:underline"
            >
              Open Native Keycloak Console
            </a>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default ThemingAndAdvanced;
