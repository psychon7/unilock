'use client';

import React, { useState, useEffect } from 'react';
import api from '@/services/api';
import { Button } from '@/components/ui/button';
import { showToast } from '@/lib/toast';
import { AxiosError } from 'axios';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";

interface ApplicationsAndProvidersProps {
  selectedDomain: string | null;
}

interface Application {
  id: string;
  clientId: string;
  name?: string;
  description?: string;
  enabled: boolean;
  publicClient: boolean;
  redirectUris: string[];
  rootUrl?: string;
  baseUrl?: string;
  adminUrl?: string;
}

interface IdentityProvider {
  alias: string;
  displayName?: string;
  providerId: string;
  enabled: boolean;
  config: {
    clientId?: string;
    clientSecret?: string;
    clientAuthMethod?: string;
    authorizationUrl?: string;
    tokenUrl?: string;
    userInfoUrl?: string;
    defaultScope?: string;
    [key: string]: string | undefined;
  };
  internalId?: string;
  addReadTokenRoleOnCreate: boolean;
  trustEmail: boolean;
  storeToken: boolean;
  firstBrokerLoginFlowAlias: string;
}

interface NewApplication {
  clientId: string;
  name: string;
  description?: string;
  publicClient: boolean;
  redirectUris: string[];
}

interface NewIdentityProvider {
  providerId: string;
  alias: string;
  displayName: string;
  config: {
    clientId: string;
    clientSecret: string;
  };
}

export const ApplicationsAndProviders: React.FC<ApplicationsAndProvidersProps> = ({ selectedDomain }) => {
  const [applications, setApplications] = useState<Application[]>([]);
  const [providers, setProviders] = useState<IdentityProvider[]>([]);
  const [loadingApps, setLoadingApps] = useState(false);
  const [loadingProviders, setLoadingProviders] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  // Add Application Modal State
  const [showAddApp, setShowAddApp] = useState(false);
  const [newApp, setNewApp] = useState<NewApplication>({
    clientId: '',
    name: '',
    description: '',
    publicClient: true,
    redirectUris: [''],
  });
  const [addingApp, setAddingApp] = useState(false);

  // Add Provider Modal State
  const [showAddProvider, setShowAddProvider] = useState(false);
  const [newProvider, setNewProvider] = useState<NewIdentityProvider>({
    providerId: 'google',
    alias: '',
    displayName: '',
    config: {
      clientId: '',
      clientSecret: '',
    },
  });
  const [addingProvider, setAddingProvider] = useState(false);
  const [confirmDialog, setConfirmDialog] = useState<{
    isOpen: boolean;
    title: string;
    description: string;
    action: () => Promise<void>;
  }>({
    isOpen: false,
    title: '',
    description: '',
    action: async () => {},
  });

  useEffect(() => {
    if (!selectedDomain) {
      setApplications([]);
      setProviders([]);
      setError(null);
      return;
    }

    const fetchData = async () => {
      setLoadingApps(true);
      setLoadingProviders(true);
      setError(null);
      try {
        const appsResponse = await api.get(`/api/v1/domains/${selectedDomain}/clients`);
        setApplications(appsResponse.data.clients);

        const providersResponse = await api.get(`/api/v1/domains/${selectedDomain}/identity-providers`);
        setProviders(providersResponse.data.providers);
      } catch (err) {
        console.error(`Error fetching data for domain ${selectedDomain}:`, err);
        setError(`Failed to load data for ${selectedDomain}.`);
        setApplications([]);
        setProviders([]);
      } finally {
        setLoadingApps(false);
        setLoadingProviders(false);
      }
    };

    fetchData();
  }, [selectedDomain]);

  interface FormErrors {
    clientId?: string;
    name?: string;
    redirectUris?: string;
    alias?: string;
    displayName?: string;
    providerId?: string;
    clientSecret?: string;
  }

  const [formErrors, setFormErrors] = useState<FormErrors>({});

  const validateApplication = (): boolean => {
    const errors: FormErrors = {};

    if (!newApp.clientId) {
      errors.clientId = 'Client ID is required';
    } else if (!/^[a-z0-9-]+$/.test(newApp.clientId)) {
      errors.clientId = 'Client ID can only contain lowercase letters, numbers, and hyphens';
    }

    if (!newApp.name) {
      errors.name = 'Display name is required';
    }

    if (newApp.redirectUris.some(uri => !uri)) {
      errors.redirectUris = 'All redirect URIs must be filled out';
    } else if (newApp.redirectUris.some(uri => !uri.startsWith('http://') && !uri.startsWith('https://'))) {
      errors.redirectUris = 'All redirect URIs must start with http:// or https://';
    }

    setFormErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const validateProvider = (): boolean => {
    const errors: FormErrors = {};

    if (!newProvider.alias) {
      errors.alias = 'Alias is required';
    } else if (!/^[a-z0-9-]+$/.test(newProvider.alias)) {
      errors.alias = 'Alias can only contain lowercase letters, numbers, and hyphens';
    }

    if (!newProvider.displayName) {
      errors.displayName = 'Display name is required';
    }

    if (!newProvider.config.clientId) {
      errors.clientId = 'Client ID is required';
    }

    if (!newProvider.config.clientSecret) {
      errors.clientSecret = 'Client Secret is required';
    }

    setFormErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleAddApplication = async () => {
    if (!selectedDomain) return;
    if (!validateApplication()) return;

    setAddingApp(true);
    try {
      await api.post(`/api/v1/domains/${selectedDomain}/clients`, newApp);
      showToast.success('Application added successfully');
      
      // Refresh applications list
      const response = await api.get(`/api/v1/domains/${selectedDomain}/clients`);
      setApplications(response.data.clients);
      
      // Reset form and close modal
      setNewApp({
        clientId: '',
        name: '',
        description: '',
        publicClient: true,
        redirectUris: [''],
      });
      setFormErrors({});
      setShowAddApp(false);
    } catch (err) {
      console.error('Failed to add application:', err);
      if (err instanceof AxiosError) {
        showToast.error(
          err.response?.data?.detail || 
          'Failed to add application. Please try again.'
        );
      } else {
        showToast.error('An unexpected error occurred. Please try again.');
      }
    } finally {
      setAddingApp(false);
    }
  };

  const handleDeleteApplication = (appId: string) => {
    setConfirmDialog({
      isOpen: true,
      title: 'Delete Application',
      description: 'Are you sure you want to delete this application? This action cannot be undone.',
      action: async () => {
        if (!selectedDomain) return;

        try {
          await api.delete(`/api/v1/domains/${selectedDomain}/clients/${appId}`);
          showToast.success('Application deleted successfully');
          
          // Refresh applications list
          const response = await api.get(`/api/v1/domains/${selectedDomain}/clients`);
          setApplications(response.data.clients);
        } catch (err) {
          console.error('Failed to delete application:', err);
          if (err instanceof AxiosError) {
            showToast.error(
              err.response?.data?.detail || 
              'Failed to delete application. Please try again.'
            );
          } else {
            showToast.error('An unexpected error occurred. Please try again.');
          }
        }
      },
    });
  };

  const handleToggleApplication = async (appId: string, enabled: boolean) => {
    if (!selectedDomain) return;

    try {
      await api.patch(`/api/v1/domains/${selectedDomain}/clients/${appId}/state`, { enabled: !enabled });
      showToast.success(`Application ${!enabled ? 'enabled' : 'disabled'} successfully`);
      
      // Refresh applications list
      const response = await api.get(`/api/v1/domains/${selectedDomain}/clients`);
      setApplications(response.data.clients);
    } catch (err) {
      console.error('Failed to toggle application state:', err);
      if (err instanceof AxiosError) {
        showToast.error(
          err.response?.data?.detail || 
          'Failed to update application state. Please try again.'
        );
      } else {
        showToast.error('An unexpected error occurred. Please try again.');
      }
    }
  };

  const handleAddProvider = async () => {
    if (!selectedDomain) return;
    if (!validateProvider()) return;

    setAddingProvider(true);
    try {
      await api.post(`/api/v1/domains/${selectedDomain}/identity-providers`, newProvider);
      showToast.success('Identity provider added successfully');
      
      // Refresh providers list
      const response = await api.get(`/api/v1/domains/${selectedDomain}/identity-providers`);
      setProviders(response.data.providers);
      
      // Reset form and close modal
      setNewProvider({
        providerId: 'google',
        alias: '',
        displayName: '',
        config: {
          clientId: '',
          clientSecret: '',
        },
      });
      setShowAddProvider(false);
    } catch (err) {
      console.error('Failed to add provider:', err);
      if (err instanceof AxiosError) {
        showToast.error(
          err.response?.data?.detail || 
          'Failed to add provider. Please try again.'
        );
      } else {
        showToast.error('An unexpected error occurred. Please try again.');
      }
    } finally {
      setAddingProvider(false);
    }
  };

  if (!selectedDomain) {
    return <div className="text-center text-gray-500 pt-10">Select a domain to see its applications and providers.</div>;
  }

  if (loadingApps || loadingProviders) {
    return <div className="text-center text-gray-500 pt-10">Loading data for {selectedDomain}...</div>;
  }

  if (error) {
    return <div className="text-center text-red-500 pt-10">{error}</div>;
  }

  return (
    <div className="space-y-6 h-full flex flex-col">
      <Dialog 
        open={confirmDialog.isOpen} 
        onOpenChange={(open) => !open && setConfirmDialog(prev => ({ ...prev, isOpen: false }))}
      >
        <DialogContent>
          <DialogHeader>
            <DialogTitle>{confirmDialog.title}</DialogTitle>
            <DialogDescription>
              {confirmDialog.description}
            </DialogDescription>
          </DialogHeader>
          <div className="flex justify-end space-x-2">
            <Button
              variant="ghost"
              onClick={() => setConfirmDialog(prev => ({ ...prev, isOpen: false }))}
            >
              Cancel
            </Button>
            <Button
              variant="destructive"
              onClick={async () => {
                await confirmDialog.action();
                setConfirmDialog(prev => ({ ...prev, isOpen: false }));
              }}
            >
              Confirm
            </Button>
          </div>
        </DialogContent>
      </Dialog>
      {/* Applications Section */}
      <Card className="flex-1 flex flex-col">
        <CardHeader className="flex flex-row items-center justify-between pb-2">
          <CardTitle className="text-lg font-semibold">Applications (Clients)</CardTitle>
          <Dialog open={showAddApp} onOpenChange={setShowAddApp}>
            <DialogTrigger asChild>
              <Button size="sm">+ Add App</Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Add Application</DialogTitle>
                <DialogDescription>
                  Add a new OIDC client application to this domain.
                </DialogDescription>
              </DialogHeader>
              <div className="space-y-4 py-4">
                <div>
                  <Label htmlFor="clientId">Client ID</Label>
                  <Input
                    id="clientId"
                    value={newApp.clientId}
                    onChange={(e) => setNewApp(prev => ({ ...prev, clientId: e.target.value }))}
                    placeholder="my-app"
                    className={formErrors.clientId ? 'border-red-500' : ''}
                  />
                  {formErrors.clientId && (
                    <p className="text-sm text-red-500 mt-1">{formErrors.clientId}</p>
                  )}
                  <p className="text-sm text-gray-500 mt-1">
                    A unique identifier for your application
                  </p>
                </div>
                <div>
                  <Label htmlFor="name">Display Name</Label>
                  <Input
                    id="name"
                    value={newApp.name}
                    onChange={(e) => setNewApp(prev => ({ ...prev, name: e.target.value }))}
                    placeholder="My Application"
                    className={formErrors.name ? 'border-red-500' : ''}
                  />
                  {formErrors.name && (
                    <p className="text-sm text-red-500 mt-1">{formErrors.name}</p>
                  )}
                </div>
                <div>
                  <Label htmlFor="description">Description (Optional)</Label>
                  <Input
                    id="description"
                    value={newApp.description}
                    onChange={(e) => setNewApp(prev => ({ ...prev, description: e.target.value }))}
                    placeholder="A brief description of your application"
                  />
                </div>
                <div>
                  <Label>Client Type</Label>
                  <div className="flex items-center space-x-2 mt-1">
                    <input
                      type="radio"
                      id="public"
                      checked={newApp.publicClient}
                      onChange={() => setNewApp(prev => ({ ...prev, publicClient: true }))}
                    />
                    <label htmlFor="public">Public (Mobile/SPA)</label>
                    <input
                      type="radio"
                      id="confidential"
                      checked={!newApp.publicClient}
                      onChange={() => setNewApp(prev => ({ ...prev, publicClient: false }))}
                    />
                    <label htmlFor="confidential">Confidential (Server)</label>
                  </div>
                </div>
                <div>
                  <Label>Redirect URIs</Label>
                  {formErrors.redirectUris && (
                    <p className="text-sm text-red-500 mb-2">{formErrors.redirectUris}</p>
                  )}
                  {newApp.redirectUris.map((uri, index) => (
                    <div key={index} className="flex items-center space-x-2 mt-2">
                      <Input
                        value={uri}
                        onChange={(e) => {
                          const newUris = [...newApp.redirectUris];
                          newUris[index] = e.target.value;
                          setNewApp(prev => ({ ...prev, redirectUris: newUris }));
                        }}
                        placeholder="https://example.com/callback"
                      />
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => {
                          const newUris = newApp.redirectUris.filter((_, i) => i !== index);
                          setNewApp(prev => ({ ...prev, redirectUris: newUris }));
                        }}
                      >
                        Remove
                      </Button>
                    </div>
                  ))}
                  <Button
                    variant="outline"
                    size="sm"
                    className="mt-2"
                    onClick={() => {
                      setNewApp(prev => ({
                        ...prev,
                        redirectUris: [...prev.redirectUris, '']
                      }));
                    }}
                  >
                    Add Redirect URI
                  </Button>
                </div>
                <div className="flex justify-end space-x-2 mt-4">
                  <Button
                    variant="ghost"
                    onClick={() => setShowAddApp(false)}
                    disabled={addingApp}
                  >
                    Cancel
                  </Button>
                  <Button
                    onClick={handleAddApplication}
                    disabled={addingApp}
                  >
                    {addingApp ? 'Adding...' : 'Add Application'}
                  </Button>
                </div>
              </div>
            </DialogContent>
          </Dialog>
        </CardHeader>
        <CardContent className="flex-1 overflow-y-auto pt-0">
          {applications.length === 0 ? (
            <p className="text-gray-500 text-sm">No applications configured for this domain.</p>
          ) : (
            <Accordion type="single" collapsible className="w-full">
              {applications.map(app => (
                <AccordionItem value={app.id} key={app.id}>
                  <AccordionTrigger>{app.name || app.clientId} ({app.clientId})</AccordionTrigger>
                  <AccordionContent className="text-sm space-y-2">
                    <div className="space-y-2">
                      <div className="flex justify-between items-center">
                        <p><strong>Status:</strong> {app.enabled ? 'Enabled' : 'Disabled'}</p>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleToggleApplication(app.id, app.enabled)}
                        >
                          {app.enabled ? 'Disable' : 'Enable'}
                        </Button>
                      </div>
                      <p><strong>Type:</strong> {app.publicClient ? 'Public' : 'Confidential'}</p>
                      {app.description && <p><strong>Description:</strong> {app.description}</p>}
                      <p><strong>Redirect URIs:</strong></p>
                      <ul className="list-disc list-inside pl-4">
                        {app.redirectUris?.map((uri, index) => <li key={index}>{uri}</li>)}
                        {app.redirectUris.length === 0 && <li>(None)</li>}
                      </ul>
                      <div className="flex justify-end pt-2">
                        <Button
                          variant="destructive"
                          size="sm"
                          onClick={() => handleDeleteApplication(app.id)}
                        >
                          Delete Application
                        </Button>
                      </div>
                    </div>
                  </AccordionContent>
                </AccordionItem>
              ))}
            </Accordion>
          )}
        </CardContent>
      </Card>

      {/* Identity Providers Section */}
      <Card className="flex-1 flex flex-col">
        <CardHeader className="flex flex-row items-center justify-between pb-2">
          <CardTitle className="text-lg font-semibold">Identity Providers</CardTitle>
          <Dialog open={showAddProvider} onOpenChange={setShowAddProvider}>
            <DialogTrigger asChild>
              <Button size="sm">+ Add Provider</Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Add Identity Provider</DialogTitle>
                <DialogDescription>
                  Configure a new social or enterprise identity provider.
                </DialogDescription>
              </DialogHeader>
              <div className="space-y-4 py-4">
                <div>
                  <Label htmlFor="providerId">Provider Type</Label>
                  <select
                    id="providerId"
                    value={newProvider.providerId}
                    onChange={(e) => setNewProvider(prev => ({ ...prev, providerId: e.target.value }))}
                    className="w-full mt-1 px-3 py-2 border border-gray-300 rounded-md"
                  >
                    <option value="google">Google</option>
                    <option value="github">GitHub</option>
                    <option value="facebook">Facebook</option>
                    <option value="microsoft">Microsoft</option>
                    <option value="saml">SAML</option>
                  </select>
                </div>
                <div>
                  <Label htmlFor="alias">Alias</Label>
                  <Input
                    id="alias"
                    value={newProvider.alias}
                    onChange={(e) => setNewProvider(prev => ({ ...prev, alias: e.target.value }))}
                    placeholder="my-google-idp"
                    className={formErrors.alias ? 'border-red-500' : ''}
                  />
                  {formErrors.alias && (
                    <p className="text-sm text-red-500 mt-1">{formErrors.alias}</p>
                  )}
                  <p className="text-sm text-gray-500 mt-1">
                    A unique identifier for this provider
                  </p>
                </div>
                <div>
                  <Label htmlFor="displayName">Display Name</Label>
                  <Input
                    id="displayName"
                    value={newProvider.displayName}
                    onChange={(e) => setNewProvider(prev => ({ ...prev, displayName: e.target.value }))}
                    placeholder="Google SSO"
                    className={formErrors.displayName ? 'border-red-500' : ''}
                  />
                  {formErrors.displayName && (
                    <p className="text-sm text-red-500 mt-1">{formErrors.displayName}</p>
                  )}
                </div>
                <div>
                  <Label htmlFor="clientId">Client ID</Label>
                  <Input
                    id="clientId"
                    value={newProvider.config.clientId}
                    onChange={(e) => setNewProvider(prev => ({
                      ...prev,
                      config: { ...prev.config, clientId: e.target.value }
                    }))}
                    placeholder="OAuth Client ID from provider"
                    className={formErrors.clientId ? 'border-red-500' : ''}
                  />
                  {formErrors.clientId && (
                    <p className="text-sm text-red-500 mt-1">{formErrors.clientId}</p>
                  )}
                </div>
                <div>
                  <Label htmlFor="clientSecret">Client Secret</Label>
                  <Input
                    id="clientSecret"
                    type="password"
                    value={newProvider.config.clientSecret}
                    onChange={(e) => setNewProvider(prev => ({
                      ...prev,
                      config: { ...prev.config, clientSecret: e.target.value }
                    }))}
                    placeholder="OAuth Client Secret from provider"
                    className={formErrors.clientSecret ? 'border-red-500' : ''}
                  />
                  {formErrors.clientSecret && (
                    <p className="text-sm text-red-500 mt-1">{formErrors.clientSecret}</p>
                  )}
                </div>
                <div className="flex justify-end space-x-2 mt-4">
                  <Button
                    variant="ghost"
                    onClick={() => setShowAddProvider(false)}
                    disabled={addingProvider}
                  >
                    Cancel
                  </Button>
                  <Button
                    onClick={handleAddProvider}
                    disabled={addingProvider}
                  >
                    {addingProvider ? 'Adding...' : 'Add Provider'}
                  </Button>
                </div>
              </div>
            </DialogContent>
          </Dialog>
        </CardHeader>
        <CardContent className="flex-1 overflow-y-auto pt-0">
          {providers.length === 0 ? (
            <p className="text-gray-500 text-sm">No identity providers configured.</p>
          ) : (
            <ul className="space-y-2">
              {providers.map(provider => (
                <li key={provider.alias} className="flex justify-between items-center p-2 border rounded">
                  <div className="flex flex-col">
                    <span className="font-medium">{provider.displayName || provider.alias}</span>
                    <span className="text-sm text-gray-500">{provider.providerId}</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <button
                      onClick={async () => {
                        try {
                          await api.patch(
                            `/api/v1/domains/${selectedDomain}/identity-providers/${provider.alias}/state`,
                            { enabled: !provider.enabled }
                          );
                          // Refresh the providers list
                          const response = await api.get(`/api/v1/domains/${selectedDomain}/identity-providers`);
                          setProviders(response.data.providers);
                          showToast.success(
                            `${provider.displayName || provider.alias} has been ${!provider.enabled ? 'enabled' : 'disabled'}`
                          );
                        } catch (err: unknown) {
                          console.error('Failed to toggle provider state:', err);
                          if (err instanceof AxiosError) {
                            showToast.error(
                              err.response?.data?.detail || 
                              'Failed to update provider state. Please try again.'
                            );
                          } else {
                            showToast.error('An unexpected error occurred. Please try again.');
                          }
                        }
                      }}
                      className={`
                        px-3 py-1 rounded-full text-sm font-medium transition-colors
                        ${provider.enabled 
                          ? 'bg-green-100 text-green-800 hover:bg-green-200' 
                          : 'bg-gray-100 text-gray-800 hover:bg-gray-200'
                        }
                      `}
                    >
                      {provider.enabled ? 'Enabled' : 'Disabled'}
                    </button>
                    <button
                      onClick={() => {
                        // TODO: Open provider settings modal
                      }}
                      className="p-1 text-gray-500 hover:text-gray-700"
                      title="Settings"
                    >
                      <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                        <path fillRule="evenodd" d="M11.49 3.17c-.38-1.56-2.6-1.56-2.98 0a1.532 1.532 0 01-2.286.948c-1.372-.836-2.942.734-2.106 2.106.54.886.061 2.042-.947 2.287-1.561.379-1.561 2.6 0 2.978a1.532 1.532 0 01.947 2.287c-.836 1.372.734 2.942 2.106 2.106a1.532 1.532 0 012.287.947c.379 1.561 2.6 1.561 2.978 0a1.533 1.533 0 012.287-.947c1.372.836 2.942-.734 2.106-2.106a1.533 1.533 0 01.947-2.287c1.561-.379 1.561-2.6 0-2.978a1.532 1.532 0 01-.947-2.287c.836-1.372-.734-2.942-2.106-2.106a1.532 1.532 0 01-2.287-.947zM10 13a3 3 0 100-6 3 3 0 000 6z" clipRule="evenodd" />
                      </svg>
                    </button>
                  </div>
                </li>
              ))}
            </ul>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default ApplicationsAndProviders;
