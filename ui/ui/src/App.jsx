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

// (Optional) Fix Leaflet’s default icon paths for non‑custom markers.
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: new URL('leaflet/dist/images/marker-icon-2x.png', import.meta.url).href,
  iconUrl: new URL('leaflet/dist/images/marker-icon.png', import.meta.url).href,
  shadowUrl: new URL('leaflet/dist/images/marker-shadow.png', import.meta.url).href,
});

function App() {
  // State to store emergencies fetched from the /calls/next endpoint.
  const [emergencies, setEmergencies] = useState([]);

  // Function to handle the Next Emergency button click.
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
          center={[47.7324, 23.5332]} // Default center. Adjust as needed.
          zoom={13}
          style={{ height: '100%', width: '100%', borderRadius: '8px' }}
        >
          <TileLayer
            attribution="&copy; OpenStreetMap contributors"
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />
          {emergencies.map((emergency, index) => (
            <Marker
              key={index}
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

      {/* Right Column: Scrollable Emergency Card List */}
      <div
        style={{
          flex: 1,
          borderLeft: '1px solid #ccc',
          padding: '20px',
          overflowY: 'auto',
          backgroundColor: '#135',
        }}
      >
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
                backgroundColor: '#135',
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
