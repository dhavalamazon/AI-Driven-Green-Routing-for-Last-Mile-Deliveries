import React from "react";
import { MapContainer, TileLayer, Marker, Polyline, Popup } from "react-leaflet";
import "leaflet/dist/leaflet.css";

// Helper to convert route array to [lat, lon] format
const routeToLatLng = (route) => route.map(stop => [stop.lat, stop.lon]);

export default function MapView({ route }) {
  if (!route || route.length === 0) return <div>No route to display</div>;

  const positions = routeToLatLng(route);

  return (
    <MapContainer center={positions[0]} zoom={13} style={{ height: "400px", width: "100%" }}>
      <TileLayer
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        attribution='&copy; OpenStreetMap contributors'
      />
      {positions.map((pos, index) => (
        <Marker key={index} position={pos}>
          <Popup>Stop {index + 1}</Popup>
        </Marker>
      ))}
      <Polyline positions={positions} color="green" />
    </MapContainer>
  );
}
