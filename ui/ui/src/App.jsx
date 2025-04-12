import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

// Set the base URL for your API endpoints.
const API_BASE_URL = 'http://localhost:4000'; // Adjust as needed

// Fix Leaflet default icon issue for Vite:
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: new URL('leaflet/dist/images/marker-icon-2x.png', import.meta.url).href,
  iconUrl: new URL('leaflet/dist/images/marker-icon.png', import.meta.url).href,
  shadowUrl: new URL('leaflet/dist/images/marker-shadow.png', import.meta.url).href,
});

// --------------------
// MapView Component
// --------------------
function MapView() {
  const [locations, setLocations] = useState([]);

  // Fetch all locations for pins from /locations endpoint.
  useEffect(() => {
    axios.get(`${API_BASE_URL}/locations`)
      .then(response => setLocations(response.data))
      .catch(error => console.error("Error fetching locations:", error));
  }, []);

  return (
    <div>
      <h2>Locations Map</h2>
      <MapContainer center={[51.505, -0.09]} zoom={13} style={{ height: '600px', width: '100%' }}>
        <TileLayer
          attribution="&copy; OpenStreetMap contributors"
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        {locations.map((loc, index) => (
          <Marker position={[loc.lat, loc.lng]} key={index}>
            <Popup>
              {loc.name || "Location"} <br /> ({loc.lat}, {loc.lng})
            </Popup>
          </Marker>
        ))}
      </MapContainer>
    </div>
  );
}

// --------------------
// AmbulanceSearch Component
// --------------------
function AmbulanceSearch() {
  const [ambulanceData, setAmbulanceData] = useState([]);
  const [city, setCity] = useState('');
  const [cityData, setCityData] = useState(null);

  // Get general ambulance availability.
  useEffect(() => {
    axios.get(`${API_BASE_URL}/medical/search`)
      .then(response => setAmbulanceData(response.data))
      .catch(error => console.error("Error fetching ambulance data:", error));
  }, []);

  // Search ambulance data by city.
  const searchByCity = () => {
    axios.get(`${API_BASE_URL}/medical/searchbycity`, { params: { city } })
      .then(response => setCityData(response.data))
      .catch(error => console.error("Error fetching ambulance data by city:", error));
  };

  return (
    <div>
      <h2>Ambulance Availability</h2>
      <h3>All Ambulances:</h3>
      <ul>
        {ambulanceData.map((item, index) => (
          <li key={index}>
            {item.location}: {item.available} ambulances available
          </li>
        ))}
      </ul>
      <h3>Search by City:</h3>
      <input
        type="text"
        value={city}
        onChange={(e) => setCity(e.target.value)}
        placeholder="Enter city name"
      />
      <button onClick={searchByCity}>Search</button>
      {cityData && (
        <div>
          <h4>Results for {city}:</h4>
          <p>{cityData.available} ambulances available.</p>
        </div>
      )}
    </div>
  );
}

// --------------------
// DispatchForm Component
// --------------------
function DispatchForm() {
  const [source, setSource] = useState('');
  const [destination, setDestination] = useState('');
  const [ambulances, setAmbulances] = useState(1);
  const [result, setResult] = useState(null);

  // Post dispatch request to /medical/dispatch endpoint.
  const handleDispatch = (e) => {
    e.preventDefault();
    axios.post(`${API_BASE_URL}/medical/dispatch`, {
      source,
      destination,
      ambulances,
    })
    .then(response => setResult(response.data))
    .catch(error => console.error("Error dispatching ambulances:", error));
  };

  return (
    <div>
      <h2>Dispatch Ambulances</h2>
      <form onSubmit={handleDispatch}>
        <div>
          <label>Source Location:</label>
          <input
            type="text"
            value={source}
            onChange={(e) => setSource(e.target.value)}
            placeholder="Enter source location"
            required
          />
        </div>
        <div>
          <label>Destination Location:</label>
          <input
            type="text"
            value={destination}
            onChange={(e) => setDestination(e.target.value)}
            placeholder="Enter destination location"
            required
          />
        </div>
        <div>
          <label>Number of Ambulances:</label>
          <input
            type="number"
            value={ambulances}
            onChange={(e) => setAmbulances(e.target.value)}
            min="1"
            required
          />
        </div>
        <button type="submit">Dispatch</button>
      </form>
      {result && (
        <div>
          <h4>Dispatch Result:</h4>
          <pre>{JSON.stringify(result, null, 2)}</pre>
        </div>
      )}
    </div>
  );
}

// --------------------
// EmergencyCalls Component
// --------------------
function EmergencyCalls() {
  const [nextCall, setNextCall] = useState(null);
  const [queue, setQueue] = useState([]);

  // Fetch next emergency call and the pending call queue.
  useEffect(() => {
    axios.get(`${API_BASE_URL}/calls/next`)
      .then(response => setNextCall(response.data))
      .catch(error => console.error("Error fetching next call:", error));

    axios.get(`${API_BASE_URL}/calls/queue`)
      .then(response => setQueue(response.data))
      .catch(error => console.error("Error fetching call queue:", error));
  }, []);

  return (
    <div>
      <h2>Emergency Calls</h2>
      <div>
        <h3>Next Emergency Call:</h3>
        {nextCall ? (
          <div>
            <p>Location: {nextCall.location}</p>
            <p>Ambulances Required: {nextCall.ambulancesNeeded}</p>
          </div>
        ) : (
          <p>No upcoming emergency call.</p>
        )}
      </div>
      <div>
        <h3>Call Queue:</h3>
        <ul>
          {queue.length > 0 ? queue.map((call, index) => (
            <li key={index}>
              Location: {call.location} | Ambulances Required: {call.ambulancesNeeded} | Status: {call.status}
            </li>
          )) : <p>No pending emergency calls.</p>}
        </ul>
      </div>
    </div>
  );
}

// --------------------
// App Component (Tab-based UI)
// --------------------
function App() {
  const [activeTab, setActiveTab] = useState('map');

  return (
    <div className="App">
      <h1>Emergency Simulation Dashboard</h1>
      <nav style={{ marginBottom: '20px' }}>
        <button onClick={() => setActiveTab('map')}>Map</button>
        <button onClick={() => setActiveTab('ambulance')}>Ambulance Search</button>
        <button onClick={() => setActiveTab('dispatch')}>Dispatch</button>
        <button onClick={() => setActiveTab('calls')}>Emergency Calls</button>
      </nav>
      <div style={{ padding: '20px' }}>
        {activeTab === 'map' && <MapView />}
        {activeTab === 'ambulance' && <AmbulanceSearch />}
        {activeTab === 'dispatch' && <DispatchForm />}
        {activeTab === 'calls' && <EmergencyCalls />}
      </div>
    </div>
  );
}

export default App;
