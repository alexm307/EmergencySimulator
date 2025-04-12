UI Module Documentation
Table of Contents
Overview

Architecture and Components

Map Display

Emergency Details Panel

Resource Search Panel

Dispatch Form

Notification System

Automated, Manual, and Hybrid Aspects

Usage Instructions

Setup and Running

Interacting with the UI

Extending the UI Module

Troubleshooting and Support

1. Overview
This UI module is built with React using the Vite bundler and leverages React Leaflet for interactive mapping. It serves as the front-end interface for an emergency simulation and resource management system. It fetches live data from various API endpoints related to emergencies and resource searches, provides visual mapping of emergency locations (red markers) and available resources (blue markers), and facilitates dispatching actions through a form.

The UI module is designed to provide real-time visibility on emergencies and available resources, and it guides the user through dispatch decisions. A combination of automated data updates and manual user interactions creates a hybrid system for managing resources and emergencies.

2. Architecture and Components
Map Display
Technologies: React Leaflet, OpenStreetMap tiles.

Functionality:

Displays an interactive map with markers.

Red markers indicate emergency locations.

Blue markers (grouped by city) represent available resources for a particular type (fire, medical, police, rescue, utility).

Behavior:

The map automatically updates with markers based on the state changes from API calls.

Collapsible panels in the sidebar help organize data for clarity.

Emergency Details Panel
Description:

Lists all current emergencies fetched from the /calls/next API.

Each emergency is displayed in a card with details like city, county, coordinates, and resource requests.

User Interaction:

A "Next Emergency" button allows users to fetch and display new emergency events.

The panel is collapsible so the user can hide or show the details as needed.

Resource Search Panel
Description:

Offers buttons to trigger resource search requests for various resource types.

The search results are grouped by city and county to avoid duplication.

User Interaction:

When a search button is clicked, the UI calls the corresponding endpoint and updates the resource data.

Previous values for that particular resource type are overwritten instead of accumulated.

The panel is collapsible to manage screen space.

Dispatch Form
Purpose:

Allows the user to dispatch resources by providing source and target location details along with the quantity to be dispatched.

Payload Structure:

json
Copy
{
  "sourceCounty": "string",
  "sourceCity": "string",
  "targetCounty": "string",
  "targetCity": "string",
  "quantity": int
}
API Endpoints:

Dispatch requests are sent to endpoints like /fire/dispatch, /medical/dispatch, etc.

Result:

On submission, the dispatch form adjusts relevant emergency and resource states.

Marks with fulfilled quantities are removed automatically.

Notification System
Tool Used: react-toastify

Functionality:

Displays temporary toasts (notifications) at the top-right corner.

Shows a green toast on successful operations (like a successful dispatch) and a red toast when errors occur (e.g., API request failures).

3. Automated, Manual, and Hybrid Aspects
Automated:

The map updates automatically when the state changes (emergencies and resources).

Grouping of resource data based on city and county is handled automatically in the UI.

Toast notifications are triggered automatically upon success or failure of API requests.

Manual:

The user must manually trigger data fetching using buttons (e.g., "Next Emergency", "Search Fire", etc.).

The dispatch process is manually initiated by filling out the form.

Collapsible panels in the sidebar allow users to customize the view manually.

Hybrid:

The dispatch module is a hybrid; it requires manual input from the user while automatically updating the state (removing fulfilled emergencies/resources).

Resource searches combine automated grouping and data updating with manual trigger actions.

4. Usage Instructions
Setup and Running
Clone and Install Dependencies:

Clone the repository.

Run npm install to install all dependencies including React, React Leaflet, axios, and react-toastify.

Development Server:

Run npm run dev to start the Vite development server.

Open your browser and navigate to the provided URL (usually http://localhost:3000).

Interacting with the UI
Map Interaction:

View current emergencies (red markers) and resource groups (blue markers) on the map.

Hover over markers to see detailed popups.

Emergency Panel:

Click "Next Emergency" to fetch the next emergency event from the API.

Use the collapsible toggle to show/hide emergency details.

Resource Panel:

Click any resource search button (e.g., "Search Fire") to update the resources on the map and sidebar.

The resource panel groups data by city and can be collapsed or expanded via the toggle.

Dispatching:

Fill out the dispatch form with source and target locations, select resource type, and specify quantity.

On form submission, the app sends a dispatch request and automatically updates the state.

Success or error notifications appear as toast messages.

5. Extending the UI Module
Adding New Endpoints:
New endpoints can be integrated by following the patterns established in the resource search and dispatch functions.

Customizing the UI:
Styles are inline in the current version. For a production-level interface, consider migrating to a CSS framework or styled-components for enhanced maintainability.

Real-Time Updates:
For real-time functionality, consider integrating websockets or periodic polling for emergency and resource updates.

6. Troubleshooting and Support
API Errors:

Ensure your API endpoints are running on the expected port.

Check the browser console and toast notifications for error messages.

UI Layout Issues:

Verify CSS styles if content appears misaligned.

Adjust flex properties or container heights/widths as needed.

Contact:

For further assistance, please refer to the project’s issue tracker or contact the project maintainers.