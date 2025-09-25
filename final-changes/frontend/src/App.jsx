import React, { useState } from "react";
import MapView from "./MapView";
import LocationSelector from "./LocationSelector";
import ResultsView from "./ResultsView";

export default function App() {
  const [routeData, setRouteData] = useState(null);
  const [selectedLocations, setSelectedLocations] = useState([]);
  const [vehicleType, setVehicleType] = useState("Car");
  const [fuelType, setFuelType] = useState("Petrol");
  const [trafficConditions, setTrafficConditions] = useState("Moderate");

  async function optimizeRoute() {
    if (selectedLocations.length < 2) {
      alert("Please select at least 2 locations on the map");
      return;
    }

    const res = await fetch("http://localhost:8000/optimize", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        stops: selectedLocations,
        vehicle_type: vehicleType,
        fuel_type: fuelType,
        traffic_conditions: trafficConditions
      })
    });
    const data = await res.json();
    console.log('API Response:', data);
    setRouteData(data);
  }

  return (
    <div style={{ padding: "20px", maxWidth: "800px" }}>
      <h2 style={{ color: "#2E7D32", marginBottom: "20px" }}>🌱 AI Green Routing System</h2>
      
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "15px", marginBottom: "20px", padding: "15px", backgroundColor: "#f9f9f9", borderRadius: "8px" }}>
        
        <div>
          <label style={{ display: "block", fontWeight: "bold", marginBottom: "5px" }}>Vehicle Type:</label>
          <select value={vehicleType} onChange={(e) => setVehicleType(e.target.value)} style={{ width: "100%", padding: "8px" }}>
            <option value="Car">Car</option>
            <option value="Truck">Truck</option>
            <option value="Bus">Bus</option>
            <option value="Motorcycle">Motorcycle</option>
          </select>
        </div>

        <div>
          <label style={{ display: "block", fontWeight: "bold", marginBottom: "5px" }}>Fuel Type:</label>
          <select value={fuelType} onChange={(e) => setFuelType(e.target.value)} style={{ width: "100%", padding: "8px" }}>
            <option value="Electric">Electric</option>
            <option value="Hybrid">Hybrid</option>
            <option value="Petrol">Petrol</option>
            <option value="Diesel">Diesel</option>
          </select>
        </div>

        <div style={{ gridColumn: "span 2" }}>
          <label style={{ display: "block", fontWeight: "bold", marginBottom: "5px" }}>Traffic Conditions:</label>
          <select value={trafficConditions} onChange={(e) => setTrafficConditions(e.target.value)} style={{ width: "100%", padding: "8px" }}>
            <option value="Free flow">Free Flow</option>
            <option value="Moderate">Moderate</option>
            <option value="Heavy">Heavy</option>
          </select>
        </div>
      </div>

      <div style={{ marginBottom: "20px" }}>
        <h3 style={{ color: "#2E7D32", marginBottom: "10px" }}>📍 Select Locations</h3>
        <p style={{ fontSize: "14px", color: "#666", marginBottom: "10px" }}>Click on the map to add pickup and delivery locations ({selectedLocations.length} selected)</p>
        <LocationSelector 
          selectedLocations={selectedLocations}
          onLocationsChange={setSelectedLocations}
        />
      </div>

      <button 
        onClick={optimizeRoute}
        disabled={selectedLocations.length < 2}
        style={{ 
          backgroundColor: selectedLocations.length < 2 ? "#ccc" : "#4CAF50", 
          color: "white", 
          padding: "12px 24px", 
          border: "none", 
          borderRadius: "5px", 
          fontSize: "16px", 
          cursor: selectedLocations.length < 2 ? "not-allowed" : "pointer",
          width: "100%"
        }}
      >
        🚀 AI Optimize Route ({selectedLocations.length} locations)
      </button>

      {routeData && <ResultsView data={routeData} />}
      {routeData && <MapView route={routeData.best_route} routeMapping={routeData.route_mapping} />}
    </div>
  );
}
