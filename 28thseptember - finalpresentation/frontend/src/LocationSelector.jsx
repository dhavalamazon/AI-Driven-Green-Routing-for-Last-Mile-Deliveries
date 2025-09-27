import React from "react";
import { MapContainer, TileLayer, Marker, Popup, useMapEvents } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import L from "leaflet";

// Create numbered markers for selection
const createNumberedIcon = (number) => {
  return L.divIcon({
    html: `<div style="
      background-color: #2196F3;
      color: white;
      border-radius: 50%;
      width: 30px;
      height: 30px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: bold;
      font-size: 14px;
      border: 2px solid white;
      box-shadow: 0 2px 4px rgba(0,0,0,0.3);
    ">${number}</div>`,
    className: 'custom-div-icon',
    iconSize: [30, 30],
    iconAnchor: [15, 15]
  });
};

function LocationMarker({ selectedLocations, onLocationsChange }) {
  useMapEvents({
    click(e) {
      const newLocation = {
        lat: e.latlng.lat,
        lon: e.latlng.lng
      };
      onLocationsChange([...selectedLocations, newLocation]);
    },
  });

  return null;
}

export default function LocationSelector({ selectedLocations, onLocationsChange }) {
  const clearLocations = () => {
    onLocationsChange([]);
  };

  const removeLocation = (index) => {
    const newLocations = selectedLocations.filter((_, i) => i !== index);
    onLocationsChange(newLocations);
  };

  // Default center on Bangalore
  const defaultCenter = [12.9716, 77.5946];

  return (
    <div>
      <div style={{ marginBottom: "10px", display: "flex", gap: "10px", alignItems: "center", flexWrap: "wrap" }}>
        <button 
          onClick={() => onLocationsChange([
            {lat: 12.8456, lon: 77.6603}, // Electronic City (Start)
            {lat: 12.9716, lon: 77.5946}, // UB City Mall (Dense City Center)
            {lat: 12.9698, lon: 77.6500}, // Indiranagar (Heavy Traffic Zone)
            {lat: 12.8200, lon: 77.7200}, // Sarjapur Road (Highway Route)
            {lat: 12.9500, lon: 77.7000}, // Marathahalli (Highway Exit)
            {lat: 13.0358, lon: 77.5970}  // Hebbal (Final Destination)
          ])}
          style={{
            backgroundColor: "#4CAF50",
            color: "white",
            padding: "8px 16px",
            border: "none",
            borderRadius: "4px",
            cursor: "pointer",
            fontSize: "14px"
          }}
        >
          Load Bangalore Demo
        </button>
        <button 
          onClick={clearLocations}
          style={{
            backgroundColor: "#f44336",
            color: "white",
            padding: "8px 16px",
            border: "none",
            borderRadius: "4px",
            cursor: "pointer",
            fontSize: "14px"
          }}
        >
          Clear All
        </button>
        <span style={{ fontSize: "14px", color: "#666" }}>
          Click on map to add locations
        </span>
      </div>

      <MapContainer 
        center={defaultCenter} 
        zoom={12} 
        style={{ height: "300px", width: "100%", marginBottom: "15px" }}
      >
        <TileLayer
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          attribution='&copy; OpenStreetMap contributors'
        />
        
        <LocationMarker 
          selectedLocations={selectedLocations}
          onLocationsChange={onLocationsChange}
        />
        
        {selectedLocations.map((location, index) => (
          <Marker 
            key={index} 
            position={[location.lat, location.lon]}
            icon={createNumberedIcon(index + 1)}
          >
            <Popup>
              <div style={{ textAlign: "center" }}>
                <strong>Stop {index + 1}</strong><br/>
                <small>Lat: {location.lat.toFixed(4)}</small><br/>
                <small>Lon: {location.lon.toFixed(4)}</small><br/>
                <button 
                  onClick={() => removeLocation(index)}
                  style={{
                    backgroundColor: "#f44336",
                    color: "white",
                    padding: "4px 8px",
                    border: "none",
                    borderRadius: "3px",
                    cursor: "pointer",
                    fontSize: "12px",
                    marginTop: "5px"
                  }}
                >
                  Remove
                </button>
              </div>
            </Popup>
          </Marker>
        ))}
      </MapContainer>

      {selectedLocations.length > 0 && (
        <div style={{ 
          backgroundColor: "#f0f8ff", 
          padding: "10px", 
          borderRadius: "5px",
          fontSize: "14px"
        }}>
          <strong>Selected Locations ({selectedLocations.length}):</strong>
          <ul style={{ margin: "5px 0", paddingLeft: "20px" }}>
            {selectedLocations.map((location, index) => (
              <li key={index}>
                Stop {index + 1}: {location.lat.toFixed(4)}, {location.lon.toFixed(4)}
                <button 
                  onClick={() => removeLocation(index)}
                  style={{
                    backgroundColor: "#f44336",
                    color: "white",
                    padding: "2px 6px",
                    border: "none",
                    borderRadius: "3px",
                    cursor: "pointer",
                    fontSize: "11px",
                    marginLeft: "10px"
                  }}
                >
                  ×
                </button>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}