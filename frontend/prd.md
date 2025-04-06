Below is a comprehensive documentation for building the frontend of a simplified Keycloak management platform. This frontend provides a user-friendly interface for creating and managing realms (domains), applications, identity providers, theming, and more—while still remaining compatible with Keycloak’s native console for advanced operations. The documentation assumes a React-based SPA but can be adapted to Vue, Angular, or another framework if desired.

⸻

Table of Contents
	1.	Overview & Objectives
	2.	Tech Stack & Prerequisites
	3.	Directory Structure
	4.	Initial Project Setup
	•	4.1 Creating the React App
	•	4.2 Installing Dependencies
	•	4.3 Environment Variables & Configuration
	5.	Core Architecture
	•	5.1 API Layer (Axios/Fetch)
	•	5.2 Routing & Navigation
	•	5.3 State Management (Optional)
	•	5.4 Error Handling & Notifications
	6.	UI Modules & Pages
	•	6.1 Dashboard Page
	•	6.2 Domain Management
	•	6.3 Applications & Identity Providers
	•	6.4 Theming & Branding
	•	6.5 Advanced/Expert Mode Views
	7.	Implementing Wizards
	•	7.1 Add Domain Wizard
	•	7.2 Add Application Wizard
	•	7.3 Add Identity Provider Wizard
	8.	Authentication & Security
	•	8.1 Protecting Admin Routes (If Using the Same UI for Admin Login)
	•	8.2 Handling OAuth2 Flows (Optional)
	9.	Styling & Theming
	•	9.1 Global Styles & Theming
	•	9.2 Custom Components & Form Patterns
	10.	Testing the Frontend
	•	10.1 Unit Tests (Jest)
	•	10.2 Integration/E2E Tests (Cypress or Playwright)
	11.	Deployment
	•	11.1 Dockerizing the SPA
	•	11.2 Serving Behind a Reverse Proxy
	•	11.3 Environment Overrides
	12.	Best Practices & Next Steps

⸻

1. Overview & Objectives
	•	Goal: Provide a user-friendly interface that abstracts Keycloak’s complexity.
	•	Key Features:
	•	Managing “domains” (realms)
	•	Adding and configuring OIDC “applications” (Keycloak clients)
	•	Enabling social and enterprise identity providers
	•	Theming/branding Keycloak login pages
	•	Viewing advanced Keycloak settings in a read-only or “expert mode”

Key Requirements:
	•	Simple, consistent layout with easy wizards.
	•	Clear error handling with actionable messages (translating Keycloak’s raw errors into user-friendly language).

⸻

2. Tech Stack & Prerequisites
	1.	React (v18+), created with Vite, Create React App, or similar.
	2.	TypeScript (recommended for type safety).
	3.	Axios for HTTP requests (or fetch, but Axios is common for interceptors/error handling).
	4.	React Router (v6+) for routing.
	5.	State Management – optional (e.g., Redux, Zustand, or React Context) if the app grows large.
	6.	UI Library – optional (Material UI, Ant Design, or custom components) for a polished look.

Prerequisites:
	•	Basic knowledge of React, npm/Yarn, and modern ES6+ JavaScript or TypeScript.
	•	A running FastAPI backend (described in the previous documentation) reachable at some base URL (e.g., http://localhost:8000/).

⸻

3. Directory Structure

A suggested structure for clarity and maintainability:

admin-ui/
├─ public/
│   └─ index.html
├─ src/
│   ├─ App.tsx
│   ├─ main.tsx               # Entry point for React
│   ├─ router/
│   │   └─ index.tsx          # React Router setup
│   ├─ pages/
│   │   ├─ Dashboard.tsx
│   │   ├─ DomainDetails.tsx
│   │   ├─ AddDomainWizard.tsx
│   │   ├─ AddAppWizard.tsx
│   │   ├─ ...
│   ├─ components/
│   │   ├─ NavBar.tsx
│   │   ├─ FormField.tsx
│   │   ├─ ...
│   ├─ services/
│   │   └─ api.ts             # Axios instance & interceptors
│   ├─ hooks/
│   ├─ utils/
│   ├─ styles/
│   │   └─ global.css
│   └─ ...
├─ .env                        # environment variables (optional)
├─ package.json
├─ vite.config.ts (or webpack)
└─ tsconfig.json

	•	pages/: Each top-level route or wizard step.
	•	components/: Reusable UI components (e.g., form inputs, modals, tables).
	•	services/api.ts: Centralized Axios instance for calling the FastAPI microservice.
	•	styles/: Global stylesheet and possibly a theming system.

⸻

4. Initial Project Setup

4.1 Creating the React App
	•	Using Vite (recommended for fast builds):

npm create vite@latest admin-ui --template react-ts
cd admin-ui
npm install


	•	This generates a basic TypeScript/React structure.

4.2 Installing Dependencies

Inside admin-ui:

npm install react-router-dom axios
# optional:
npm install --save styled-components or material-ui

4.3 Environment Variables & Configuration
	•	For local dev, you can create a .env:

VITE_API_BASE_URL=http://localhost:8000


	•	In your code, read it using import.meta.env.VITE_API_BASE_URL (if using Vite).

⸻

5. Core Architecture

5.1 API Layer (Axios/Fetch)

Create src/services/api.ts to set up an Axios instance:

import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
});

// Optional: intercept responses to handle errors globally
api.interceptors.response.use(
  (response) => response,
  (error) => {
    // transform Keycloak or FastAPI error messages
    const errMsg = error.response?.data?.detail || error.message;
    return Promise.reject(errMsg);
  }
);

export default api;

5.2 Routing & Navigation

Use React Router v6 in router/index.tsx:

import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Dashboard from '../pages/Dashboard';
import DomainDetails from '../pages/DomainDetails';
import AddDomainWizard from '../pages/AddDomainWizard';

export default function AppRouter() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/domains/:domainId" element={<DomainDetails />} />
        <Route path="/domains/new" element={<AddDomainWizard />} />
      </Routes>
    </BrowserRouter>
  );
}

5.3 State Management (Optional)
	•	For smaller apps, store data in local component states or minimal React Context.
	•	For larger, more complex flows (multiple wizards, caching domain info), consider Redux Toolkit or Zustand.

5.4 Error Handling & Notifications
	•	A global error boundary or context can catch thrown errors.
	•	Alternatively, use a library like react-toastify for pop-up notifications when the Axios interceptor detects an error.

⸻

6. UI Modules & Pages

6.1 Dashboard Page
	•	Lists existing domains (retrieved from GET /domains).
	•	A “Create New Domain” button navigates to the AddDomainWizard.
	•	Could also show some usage stats (like total realms, total apps).

// Dashboard.tsx
import React, { useEffect, useState } from 'react';
import api from '../services/api';
import { Link } from 'react-router-dom';

const Dashboard: React.FC = () => {
  const [domains, setDomains] = useState<any[]>([]);

  useEffect(() => {
    api.get('/domains').then((res) => setDomains(res.data));
  }, []);

  return (
    <div>
      <h1>Domains</h1>
      <Link to="/domains/new">Add Domain</Link>
      <ul>
        {domains.map((d) => (
          <li key={d.id}>
            <Link to={`/domains/${d.id}`}>{d.display_name || d.name}</Link>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default Dashboard;

6.2 Domain Management
	•	DomainDetails.tsx: Displays domain-specific data:
	•	List of applications (Keycloak clients)
	•	List of identity providers
	•	Theming options
	•	A link/button to “Create Application” or “Add Identity Provider.”

Example layout:

// DomainDetails.tsx
import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import api from '../services/api';

const DomainDetails: React.FC = () => {
  const { domainId } = useParams();
  const [domainInfo, setDomainInfo] = useState<any>(null);

  useEffect(() => {
    api.get(`/domains/${domainId}`).then((res) => setDomainInfo(res.data));
  }, [domainId]);

  if (!domainInfo) return <div>Loading...</div>;

  return (
    <div>
      <h2>{domainInfo.displayName || domainInfo.name}</h2>
      {/* display domain-level info */}
      {/* link to add apps, IDPs, theming */}
    </div>
  );
};

export default DomainDetails;

6.3 Applications & Identity Providers
	•	Typically, you have separate pages or modals to create an application or IDP.
	•	The UI calls routes like POST /domains/:domainId/apps or POST /domains/:domainId/idps/google.

6.4 Theming & Branding
	•	A page or modal allowing users to set colors, logos, or text, then calling POST /domains/:domainId/theme.
	•	Provide a live preview if possible (use an <iframe> or a sample Keycloak login page snapshot).

6.5 Advanced/Expert Mode Views
	•	A section that lists advanced Keycloak settings (protocol mappers, advanced flows) in read-only form.
	•	Provide a direct link to the “native Keycloak console” if they want to edit them.

⸻

7. Implementing Wizards

Most interactions revolve around user-friendly wizard flows to hide Keycloak’s complexity.

7.1 Add Domain Wizard
	•	Step 1: User inputs domain name, display name.
	•	Step 2 (optional): Configure initial theme or social login?
	•	Step 3: Confirm & Submit → calls POST /domains.

Example:

// AddDomainWizard.tsx
import React, { useState } from 'react';
import api from '../services/api';
import { useNavigate } from 'react-router-dom';

const AddDomainWizard: React.FC = () => {
  const [domainName, setDomainName] = useState('');
  const [displayName, setDisplayName] = useState('');
  const navigate = useNavigate();

  const handleSubmit = () => {
    api.post('/domains', { domain_name: domainName, display_name: displayName })
      .then((res) => {
        // navigate to the newly created domain details
        navigate(`/domains/${res.data.domain_id}`);
      })
      .catch((err) => alert('Error creating domain: ' + err));
  };

  return (
    <div>
      <h1>Add Domain</h1>
      <label>Domain Name</label>
      <input value={domainName} onChange={e => setDomainName(e.target.value)} />
      <label>Display Name</label>
      <input value={displayName} onChange={e => setDisplayName(e.target.value)} />
      <button onClick={handleSubmit}>Create</button>
    </div>
  );
};

export default AddDomainWizard;

7.2 Add Application Wizard
	•	Steps to gather app name, redirect URIs, public or confidential.
	•	Then calls POST /domains/:domainId/apps.

7.3 Add Identity Provider Wizard
	•	User picks a provider (Google, GitHub, LinkedIn).
	•	Enters client ID/secret.
	•	The UI calls POST /domains/:domainId/idps/google with the necessary fields.

⸻

8. Authentication & Security

8.1 Protecting Admin Routes

If the Admin UI itself is behind Keycloak login, you can:
	1.	Create a Keycloak client specifically for your admin UI.
	2.	Use Keycloak JS adapter or a library like react-keycloak to manage sessions.
	3.	Protect routes in React Router with an <AuthRoute> that checks if the user is authenticated and has the admin role.

8.2 Handling OAuth2 Flows (Optional)
	•	If you want the admin UI to be “publicly” accessible but only certain routes are protected, implement your own login or rely on Keycloak-based login flows.

⸻

9. Styling & Theming

9.1 Global Styles & Theming
	•	Import a global stylesheet in main.tsx or use CSS modules.
	•	For consistency, define a theme object with colors, fonts, etc., pass it via ThemeProvider (styled-components) or a context.

9.2 Custom Components & Form Patterns
	•	Create a library of reusable form inputs, wizard steps, or a <PageLayout> component to standardize the look & feel.
	•	Use a UI kit if you want a more polished, consistent experience (Material UI, Ant Design, Chakra UI, etc.).

⸻

10. Testing the Frontend

10.1 Unit Tests (Jest)
	•	Use React Testing Library to test individual components or wizards.
	•	Example:

// AddDomainWizard.test.tsx
import { render, screen, fireEvent } from '@testing-library/react';
import AddDomainWizard from './AddDomainWizard';
import api from '../services/api';

jest.mock('../services/api');

test('creates domain on submit', async () => {
  (api.post as jest.Mock).mockResolvedValueOnce({ data: { domain_id: 123 } });
  render(<AddDomainWizard />);
  fireEvent.change(screen.getByLabelText(/Domain Name/i), { target: { value: 'myrealm' } });
  // ...
  fireEvent.click(screen.getByText(/Create/i));
  expect(api.post).toHaveBeenCalledWith('/domains', {
    domain_name: 'myrealm',
    display_name: ''
  });
});

10.2 Integration/E2E Tests (Cypress or Playwright)
	•	Spin up the FastAPI + Keycloak + Admin UI in Docker Compose.
	•	Use Cypress to script a test flow: “Go to dashboard → create domain → check domain detail page → verify realm exists in Keycloak.”

⸻

11. Deployment

11.1 Dockerizing the SPA
	1.	Add a Dockerfile in admin-ui/:

FROM node:18 as build
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]


	2.	Build image:

docker build -t admin-ui:latest .



11.2 Serving Behind a Reverse Proxy
	•	In production, you likely have an Nginx or similar proxy handling SSL termination.
	•	Make sure the SPA can reach the FastAPI backend at the correct internal or external URL.

11.3 Environment Overrides
	•	If you need different API endpoints in staging vs. production, you can pass environment variables or serve a config.js file that the SPA reads on startup.

⸻

12. Best Practices & Next Steps
	1.	Enhance Wizards: Provide more advanced configuration steps for SAML, custom flows, etc.
	2.	User-Friendly Error Messages: Map Keycloak’s raw error codes to descriptive text in your UI.
	3.	Internationalization (i18n): If supporting multiple languages, consider react-i18next or a similar library.
	4.	Advanced Analytics: Show user login stats, error rates, or realm usage dashboards.
	5.	Custom Theming: Add a live preview for Keycloak login themes, store multiple theme variants.
	6.	Community & Docs: Provide tutorials, a docs site, and foster a community forum (Discord, GitHub Discussions) for user feedback and contributions.

⸻
Imagine a single-page “cockpit” that consolidates all Keycloak management tasks into one screen, so a user—whether novice or power user—never has to navigate away or guess where to find settings. Below is a conceptual layout, described top to bottom (or left to right), showcasing how everything can be unified yet remain simple:

⸻

Single-Screen Layout Concept

1. Top Navigation Bar (Minimal)
	•	Brand/Logo on the far left (e.g., “Unified Auth Panel”).
	•	Profile Icon (top-right) for admin user info (logout, profile).
	•	A Search/Filter field (optional) if you have many “domains/realms.”

2. Primary Content Split into Three Main Columns
	1.	(Left Column) “Domain Selector & Basic Info”
	•	A dropdown or vertical list of “Domains” (a.k.a. realms) you manage.
	•	Each entry displays a domain name and a short descriptor.
	•	“+ Add Domain” button at the bottom for creating a new domain.
	•	Selecting a domain instantly updates the center/right columns with relevant data.
	2.	(Center Column) “Applications & Identity Providers”
	•	Applications Section (upper half)
	•	Shows a scannable list of applications (Keycloak clients) for the selected domain.
	•	Each application entry can expand (accordion-style) to show redirect URIs, client secret, or toggles (public/confidential).
	•	A “+ Add App” button to create a new application.
	•	Identity Providers Section (lower half)
	•	Lists configured IDPs (e.g., Google, GitHub, SAML providers).
	•	Each IDP row has a small toggle to enable/disable or to edit keys/secrets.
	•	A “+ Add Provider” button triggers a quick wizard overlay for picking a social/enterprise provider.
	3.	(Right Column) “Theming & Advanced”
	•	Theming/Branding Panel (top)
	•	Shows a mini preview (logo, primary color) for the domain’s login screen.
	•	Color Pickers and a Logo Upload field.
	•	A “Save/Apply” button automatically updates the Keycloak theme.
	•	Advanced/Expert Settings (bottom)
	•	Collapsible or tabbed area revealing advanced Keycloak options (protocol mappers, flows, policies) in read-only or minimal edit form.
	•	A link: “Open Native Keycloak Console” for anything beyond the simplified scope.

3. Overlay Wizards (Modals)
	•	When clicking “+ Add Domain,” “+ Add App,” or “+ Add Provider,” a single-step or multi-step overlay appears in the center of the screen (dimming the background).
	•	The user completes each step (e.g., domain name, app type, provider credentials) without leaving the page.
	•	Submitting automatically closes the modal and updates the relevant column’s list.

4. Notifications & Error Handling
	•	Toast messages or small alert banners appear at the top/middle of the screen upon successes (e.g., “Application Created”) or errors (e.g., “Invalid Provider Credentials”).
	•	All error messages are phrased in a user-friendly manner, so novices understand the issue without diving into Keycloak logs.

5. Responsiveness & Scalability
	•	On smaller screens, the layout can collapse:
	•	Domain Selector → a dropdown at the top left.
	•	Center & Right Columns → stacked sections, preserving the same sections but in vertical flow.

⸻

Why This Single-Screen Approach Works
	•	Immediate Context: Selecting a domain on the left instantly shows its apps/IDPs in the middle, plus theming & advanced options on the right. No multi-page confusion.
	•	All-in-One Management: From this single cockpit, an admin can do the entire Keycloak setup: create realms (domains), add apps, enable social logins, tweak branding, or jump to advanced settings.
	•	Minimal Clicks: Overlay modals let users complete tasks in-line without navigating away, so the user flow is contained within one intuitive page.
	•	Clear Separation of Key Areas: Domains on the left, Apps/IDPs in the center, Theming/Advanced on the right—organizing tasks without burying them under multiple menus.

By merging everything into one screen with carefully designed columns and overlay wizards, the platform remains powerful but looks and feels simple and immediate. This layout caters to both beginners (easy to discover essential tasks) and power users (quick glance of advanced domain-level data).