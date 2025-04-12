import React, { useState } from 'react';
import axios from 'axios';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

// Set the base URL for your API endpoints.
const API_BASE_URL = 'http://localhost:5000';

// Create a custom red icon for emergency markers.
const redIcon = new L.Icon({
  iconUrl:
    'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-red.png',
  shadowUrl: new URL('leaflet/dist/images/marker-shadow.png', import.meta.url).href,
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
});

// Create a custom blue icon for resource markers.
const blueIcon = new L.Icon({
  iconUrl:
    'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-blue.png',
  shadowUrl: new URL('leaflet/dist/images/marker-shadow.png', import.meta.url).href,
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
});

// (Optional) Fix Leaflet’s default icon paths for non‑custom markers.
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: new URL('leaflet/dist/images/marker-icon-2x.png', import.meta.url).href,
  iconUrl: new URL('leaflet/dist/images/marker-icon.png', import.meta.url).href,
  shadowUrl: new URL('leaflet/dist/images/marker-shadow.png', import.meta.url).href,
});

function App() {
  // State to store emergencies from the /calls/next endpoint.
  const [emergencies, setEmergencies] = useState([]);
  // State to store resource markers (from resource search endpoints).
  const [resourceMarkers, setResourceMarkers] = useState([]);

  // Function to fetch and add a new emergency.
  const fetchNextEmergency = () => {
    axios
      .get(`${API_BASE_URL}/calls/next`)
      .then((response) => {
        // Expecting payload with city, county, coordinates and requests info.
        const newEmergency = response.data;
        setEmergencies((prev) => [...prev, newEmergency]);
      })
      .catch((error) => {
        console.error('Error fetching next emergency:', error);
      });
  };

  // Function to call a resource search endpoint and add markers.
  const searchResource = (resourceType) => {
    axios
      .get(`${API_BASE_URL}/${resourceType}/search`)
      .then((response) => {
        const markers = response.data.map((item) => ({
          ...item,
          resourceType,
        }));
        setResourceMarkers((prev) => [...prev, ...markers]);
      })
      .catch((error) => {
        console.error(`Error fetching ${resourceType} resources:`, error);
      });
  };

  // Group resource markers by city and county to aggregate their quantities.
  const groupedResources = resourceMarkers.reduce((acc, curr) => {
    // Group key based on city and county.
    const key = `${curr.city}-${curr.county}`;
    if (!acc[key]) {
      acc[key] = {
        city: curr.city,
        county: curr.county,
        latitude: curr.latitude,
        longitude: curr.longitude,
        resources: {}
      };
    }
    // Sum up quantities for each resource type.
    if (acc[key].resources[curr.resourceType]) {
      acc[key].resources[curr.resourceType] += curr.quantity;
    } else {
      acc[key].resources[curr.resourceType] = curr.quantity;
    }
    return acc;
  }, {});

  // Convert grouped object into an array.
  const groupedResourceArray = Object.values(groupedResources);

  // Common style for resource search buttons.
  const buttonStyle = {
    margin: '5px',
    padding: '8px 12px',
    backgroundColor: '#fff',
    color: '#333',
    border: 'none',
    borderRadius: '4px',
    cursor: 'pointer',
  };

  return (
    <div
      className="dashboard-container"
      style={{
        display: 'flex',
        height: '100vh',
        width: '100vw',
        overflow: 'hidden',
      }}
    >
      {/* Left Column: Map Container */}
      <div style={{ flex: 3, position: 'relative', padding: '10px' }}>
        <MapContainer
          center={[47.7324, 23.5332]} // Default center.
          zoom={13}
          style={{ height: '100%', width: '100%', borderRadius: '8px' }}
        >
          <TileLayer
            attribution="&copy; OpenStreetMap contributors"
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />

          {/* Red markers for emergencies */}
          {emergencies.map((emergency, index) => (
            <Marker
              key={`emergency-${index}`}
              position={[emergency.latitude, emergency.longitude]}
              icon={redIcon}
            >
              <Popup>
                <strong>
                  {emergency.city}, {emergency.county}
                </strong>
                <br />
                {emergency.requests.map((req, idx) => (
                  <div key={idx}>
                    {req.Type}: {req.Quantity}
                  </div>
                ))}
              </Popup>
            </Marker>
          ))}

          {/* Blue markers for grouped resource searches */}
          {groupedResourceArray.map((res, index) => (
            <Marker
              key={`resource-${index}`}
              position={[res.latitude, res.longitude]}
              icon={blueIcon}
            >
              <Popup>
                <strong>
                  {res.city}, {res.county}
                </strong>
                <br />
                {Object.entries(res.resources).map(([type, qty], idx) => (
                  <div key={idx}>
                    <em>{type.toUpperCase()}</em>: {qty}
                  </div>
                ))}
              </Popup>
            </Marker>
          ))}
        </MapContainer>
        {/* Next Emergency Button */}
        <button
          onClick={fetchNextEmergency}
          style={{
            position: 'absolute',
            top: 20,
            left: 20,
            zIndex: 1000,
            padding: '10px 15px',
            backgroundColor: '#ff4d4d',
            color: '#fff',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer',
          }}
        >
          Next Emergency
        </button>
      </div>

      {/* Right Column: Scrollable Sidebar */}
      <div
        style={{
          flex: 1,
          borderLeft: '1px solid #ccc',
          padding: '20px',
          overflowY: 'auto',
          backgroundColor: '#135',
          color: '#fff',
        }}
      >
        {/* Resource Search Section */}
        <div style={{ marginBottom: '20px' }}>
          <h2>Resource Search</h2>
          <div>
            <button onClick={() => searchResource('fire')} style={buttonStyle}>
              Search Fire
            </button>
            <button onClick={() => searchResource('medical')} style={buttonStyle}>
              Search Medical
            </button>
            <button onClick={() => searchResource('police')} style={buttonStyle}>
              Search Police
            </button>
            <button onClick={() => searchResource('utility')} style={buttonStyle}>
              Search Utility
            </button>
            <button onClick={() => searchResource('rescue')} style={buttonStyle}>
              Search Rescue
            </button>
          </div>
        </div>

        {/* Resource Results Section (Grouped by City) */}
        <div style={{ marginBottom: '20px' }}>
          <h3>Grouped Resource Results</h3>
          {groupedResourceArray.length === 0 ? (
            <p>No resource search results yet.</p>
          ) : (
            groupedResourceArray.map((res, index) => (
              <div
                key={index}
                style={{
                  marginBottom: '10px',
                  padding: '10px',
                  border: '1px solid #ddd',
                  borderRadius: '4px',
                  backgroundColor: '#fff',
                  color: '#333',
                }}
              >
                <h4 style={{ margin: '0 0 5px 0' }}>
                  {res.city}, {res.county}
                </h4>
                <div>
                  {Object.entries(res.resources).map(([type, qty], idx) => (
                    <p key={idx} style={{ margin: '2px 0' }}>
                      <strong>{type.toUpperCase()}:</strong> {qty}
                    </p>
                  ))}
                </div>
              </div>
            ))
          )}
        </div>

        <hr style={{ margin: '20px 0', borderColor: '#fff' }} />

        {/* Emergency Details Section */}
        <h2>Emergency Details</h2>
        {emergencies.length === 0 ? (
          <p>No emergencies yet. Press "Next Emergency" to fetch one.</p>
        ) : (
          emergencies.map((emergency, index) => (
            <div
              key={index}
              style={{
                marginBottom: '15px',
                padding: '15px',
                border: '1px solid #ddd',
                borderRadius: '6px',
                backgroundColor: '#fff',
                color: '#333',
              }}
            >
              <h3 style={{ margin: '0 0 5px 0' }}>
                {emergency.city}, {emergency.county}
              </h3>
              <p style={{ margin: '0 0 5px 0' }}>
                <strong>Coordinates:</strong> {emergency.latitude}, {emergency.longitude}
              </p>
              <div>
                <strong>Requests:</strong>
                <ul style={{ paddingLeft: '20px', margin: '5px 0' }}>
                  {emergency.requests.map((req, idx) => (
                    <li key={idx}>
                      {req.Type}: {req.Quantity}
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}

export default App;
