import React, { useState } from 'react';
import axios from 'axios';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { ToastContainer, toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

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
  // State to store resource markers from resource search endpoints.
  const [resourceMarkers, setResourceMarkers] = useState([]);
  // State toggles for the collapsible lists.
  const [showResourceList, setShowResourceList] = useState(true);
  const [showEmergencyList, setShowEmergencyList] = useState(true);

  // Function to fetch and add a new emergency.
  const fetchNextEmergency = () => {
    axios
      .get(`${API_BASE_URL}/calls/next`)
      .then((response) => {
        // Expected payload: { city, county, latitude, longitude, requests: [ { Type, Quantity }, ... ] }
        const newEmergency = response.data;
        setEmergencies((prev) => [...prev, newEmergency]);
      })
      .catch((error) => {
        console.error('Error fetching next emergency:', error);
        toast.error("Error fetching next emergency!");
      });
  };

  // Function to fetch resource markers from a given resource search endpoint.
  // Changes: Filter out markers for the same resource type so that we overwrite previous values.
  const searchResource = (resourceType) => {
    axios
      .get(`${API_BASE_URL}/${resourceType}/search`)
      .then((response) => {
        // Each item: { county, city, latitude, longitude, quantity }
        const markers = response.data.map((item) => ({
          ...item,
          resourceType,
        }));
        setResourceMarkers((prev) => {
          // Remove any markers of the same resource type.
          const filtered = prev.filter((marker) => marker.resourceType !== resourceType);
          return [...filtered, ...markers];
        });
      })
      .catch((error) => {
        console.error(`Error fetching ${resourceType} resources:`, error);
        toast.error(`Error fetching ${resourceType} resources!`);
      });
  };

  // Group resource markers by city and county (for display and for the map).
  const groupedResources = resourceMarkers.reduce((acc, curr) => {
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
    if (acc[key].resources[curr.resourceType]) {
      acc[key].resources[curr.resourceType] += curr.quantity;
    } else {
      acc[key].resources[curr.resourceType] = curr.quantity;
    }
    return acc;
  }, {});
  const groupedResourceArray = Object.values(groupedResources);

  // Handle the result of a successful dispatch form submission.
  const handleDispatchSuccess = ({ resourceType, sourceCounty, sourceCity, targetCounty, targetCity, quantity }) => {
    // Update emergencies: Adjust request values on emergencies whose target city/county matches.
    setEmergencies((prev) =>
      prev
        .map((emergency) => {
          if (
            emergency.city.toLowerCase() === targetCity.toLowerCase() &&
            emergency.county.toLowerCase() === targetCounty.toLowerCase()
          ) {
            const updatedRequests = emergency.requests.map((req) => {
              if (req.Type.toLowerCase() === resourceType.toLowerCase()) {
                const newQty = req.Quantity - quantity;
                return { ...req, Quantity: newQty < 0 ? 0 : newQty };
              }
              return req;
            });
            return { ...emergency, requests: updatedRequests };
          }
          return emergency;
        })
        .filter((emergency) => emergency.requests.some((req) => req.Quantity > 0))
    );

    // Update resourceMarkers: Decrease quantity for markers at the source that match the resource type.
    setResourceMarkers((prev) =>
      prev
        .map((marker) => {
          if (
            marker.resourceType.toLowerCase() === resourceType.toLowerCase() &&
            marker.city.toLowerCase() === sourceCity.toLowerCase() &&
            marker.county.toLowerCase() === sourceCounty.toLowerCase()
          ) {
            const newQty = marker.quantity - quantity;
            return { ...marker, quantity: newQty < 0 ? 0 : newQty };
          }
          return marker;
        })
        .filter((marker) => marker.quantity > 0)
    );
  };

  // A common style for the resource search buttons.
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
      {/* ToastContainer to display notifications */}
      <ToastContainer position="top-right" autoClose={5000} />

      {/* Left Column: Map Container */}
      <div style={{ flex: 3, position: 'relative', padding: '10px' }}>
        <MapContainer
          center={[47.7324, 23.5332]} // Default center.
          zoom={10}
          style={{ height: '100%', width: '100%', borderRadius: '8px' }}
        >
          <TileLayer
            attribution="&copy; OpenStreetMap contributors"
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />
          {/* Red markers for emergencies */}
          {emergencies.map((emergency, index) => (
            <Marker key={`emergency-${index}`} position={[emergency.latitude, emergency.longitude]} icon={redIcon}>
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
            <Marker key={`resource-${index}`} position={[res.latitude, res.longitude]} icon={blueIcon}>
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
            right: 20,
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
          <h3
            style={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
            }}
          >
            Grouped Resources
            <button
              onClick={() => setShowResourceList(!showResourceList)}
              style={{
                backgroundColor: 'transparent',
                border: 'none',
                color: '#fff',
                fontSize: '1.2rem',
                cursor: 'pointer',
              }}
            >
              {showResourceList ? '–' : '+'}
            </button>
          </h3>
          {showResourceList && (
            groupedResourceArray.length === 0 ? (
              <p>No resource search results yet.</p>
            ) : (
              groupedResourceArray.map((res, index) => (
                <div
                  key={index}
                  style={{
                    marginBottom: '10px',
                    padding: '10px',
                    border: '1px solid #ddd',
                    borderRadius: '8px',
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
            )
          )}
        </div>

        <hr style={{ margin: '20px 0', borderColor: '#fff' }} />

        {/* Emergency Details Section */}
        <div style={{ marginBottom: '20px' }}>
          <h2
            style={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
            }}
          >
            Emergency Details
            <button
              onClick={() => setShowEmergencyList(!showEmergencyList)}
              style={{
                backgroundColor: 'transparent',
                border: 'none',
                color: '#fff',
                fontSize: '1.2rem',
                cursor: 'pointer',
              }}
            >
              {showEmergencyList ? '–' : '+'}
            </button>
          </h2>
          {showEmergencyList && (
            emergencies.length === 0 ? (
              <p>No emergencies yet. Press "Next Emergency" to fetch one.</p>
            ) : (
              emergencies.map((emergency, index) => (
                <div
                  key={index}
                  style={{
                    marginBottom: '15px',
                    padding: '15px',
                    border: '1px solid #ddd',
                    borderRadius: '8px',
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
            )
          )}
        </div>

        {/* Dispatch Form Section */}
        <DispatchForm onDispatchSuccess={handleDispatchSuccess} />
      </div>
    </div>
  );
}

// DispatchForm Component: Collects dispatch details and posts to the appropriate endpoint.
function DispatchForm({ onDispatchSuccess }) {
  const [resourceType, setResourceType] = useState('fire');
  const [sourceCounty, setSourceCounty] = useState('');
  const [sourceCity, setSourceCity] = useState('');
  const [targetCounty, setTargetCounty] = useState('');
  const [targetCity, setTargetCity] = useState('');
  const [quantity, setQuantity] = useState(1);

  const handleSubmit = (e) => {
    e.preventDefault();
    const payload = {
      sourceCounty,
      sourceCity,
      targetCounty,
      targetCity,
      quantity: parseInt(quantity, 10),
    };
    axios
      .post(`${API_BASE_URL}/${resourceType}/dispatch`, payload)
      .then((response) => {
        // Upon successful dispatch, update the local state via the callback.
        onDispatchSuccess({ resourceType, sourceCounty, sourceCity, targetCounty, targetCity, quantity: parseInt(quantity, 10) });
        toast.success("Dispatch succeeded!");
        // Clear the form fields.
        setSourceCounty('');
        setSourceCity('');
        setTargetCounty('');
        setTargetCity('');
        setQuantity(1);
      })
      .catch((error) => {
        console.error('Dispatch error:', error);
        toast.error("Dispatch failed!");
      });
  };

  return (
    <div style={{ marginTop: '20px', padding: '10px', backgroundColor: '#fff', color: '#333', borderRadius: '4px' }}>
      <h3>Dispatch Resources</h3>
      <form onSubmit={handleSubmit}>
        <div style={{ marginBottom: '8px' }}>
          <label>Resource Type: </label>
          <select value={resourceType} onChange={(e) => setResourceType(e.target.value)} style={{ marginLeft: '5px' }}>
            <option value="fire">Fire</option>
            <option value="medical">Medical</option>
            <option value="police">Police</option>
            <option value="rescue">Rescue</option>
            <option value="utility">Utility</option>
          </select>
        </div>
        <div style={{ marginBottom: '8px' }}>
          <label>Source County: </label>
          <input type="text" value={sourceCounty} onChange={(e) => setSourceCounty(e.target.value)} style={{ marginLeft: '5px' }} />
        </div>
        <div style={{ marginBottom: '8px' }}>
          <label>Source City: </label>
          <input type="text" value={sourceCity} onChange={(e) => setSourceCity(e.target.value)} style={{ marginLeft: '5px' }} />
        </div>
        <div style={{ marginBottom: '8px' }}>
          <label>Target County: </label>
          <input type="text" value={targetCounty} onChange={(e) => setTargetCounty(e.target.value)} style={{ marginLeft: '5px' }} />
        </div>
        <div style={{ marginBottom: '8px' }}>
          <label>Target City: </label>
          <input type="text" value={targetCity} onChange={(e) => setTargetCity(e.target.value)} style={{ marginLeft: '5px' }} />
        </div>
        <div style={{ marginBottom: '8px' }}>
          <label>Quantity: </label>
          <input type="number" value={quantity} onChange={(e) => setQuantity(e.target.value)} style={{ marginLeft: '5px', width: '60px' }} min="1" />
        </div>
        <button type="submit" style={{ padding: '8px 12px', backgroundColor: '#007bff', color: '#fff', border: 'none', borderRadius: '4px', cursor: 'pointer' }}>
          Dispatch
        </button>
      </form>
    </div>
  );
}

export default App;
