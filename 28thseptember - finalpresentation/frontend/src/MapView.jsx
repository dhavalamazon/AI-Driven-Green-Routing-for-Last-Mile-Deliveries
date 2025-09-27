import React from "react";
import { MapContainer, TileLayer, Marker, Polyline, Popup } from "react-leaflet";
import L from "leaflet";
import "leaflet/dist/leaflet.css";

// Helper to convert route array to [lat, lon] format
const routeToLatLng = (route) => route.map(stop => [stop.lat, stop.lon]);

// Create numbered markers
const createNumberedIcon = (number) => {
  return L.divIcon({
    html: `<div style="
      background-color: #4CAF50;
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

export default function MapView({ route, routeMapping, routeWaypoints }) {
  if (!route || route.length === 0) return <div>No route to display</div>;

  const positions = routeToLatLng(route);
  const waypointPositions = routeWaypoints ? routeToLatLng(routeWaypoints) : positions;

  // Generate route order text using original input stop numbers
  const routeOrderText = routeMapping ? 
    routeMapping.map(originalIndex => `Stop ${originalIndex}`).join(" → ") :
    route.map((_, index) => `Stop ${index + 1}`).join(" → ");

  return (
    <div>
      <div style={{
        backgroundColor: "#e8f5e8",
        padding: "15px",
        borderRadius: "8px",
        marginBottom: "15px",
        border: "1px solid #4CAF50"
      }}>
        <h3 style={{ margin: "0 0 10px 0", color: "#2E7D32", fontSize: "16px" }}>
          🗺️ Optimized Route Order:
        </h3>
        <div style={{ 
          fontSize: "14px", 
          fontWeight: "bold", 
          color: "#1B5E20",
          wordBreak: "break-word"
        }}>
          {routeOrderText}
        </div>
        <div style={{ 
          fontSize: "12px", 
          color: "#666", 
          marginTop: "5px"
        }}>
          Total stops: {route.length} | Green markers show the AI-optimized sequence
        </div>
      </div>

      <MapContainer center={positions[0]} zoom={12} style={{ height: "500px", width: "100%", borderRadius: "10px" }}>
        <TileLayer
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          attribution='&copy; OpenStreetMap contributors'
        />
        {positions.map((pos, index) => {
          const originalStopNumber = routeMapping ? routeMapping[index] : index + 1;
          return (
            <Marker 
              key={index} 
              position={pos}
              icon={createNumberedIcon(originalStopNumber)}
            >
              <Popup>
                <div style={{ textAlign: "center" }}>
                  <strong>Stop {originalStopNumber}</strong><br/>
                  <small>Lat: {pos[0].toFixed(4)}</small><br/>
                  <small>Lon: {pos[1].toFixed(4)}</small><br/>
                  {index === 0 && <span style={{ color: "green", fontWeight: "bold" }}>🚀 START</span>}
                  {index === positions.length - 1 && <span style={{ color: "red", fontWeight: "bold" }}>🏁 END</span>}
                </div>
              </Popup>
            </Marker>
          );
        })}
        <Polyline 
          positions={waypointPositions} 
          color="#4CAF50" 
          weight={4}
          opacity={0.8}
        />
      </MapContainer>
    </div>
  );
}
