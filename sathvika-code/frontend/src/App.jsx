import React, { useState } from "react";
import MapView from "./MapView";
import ResultsView from "./ResultsView";

export default function App() {
  const [routeData, setRouteData] = useState(null);
  const [traffic, setTraffic] = useState(0.5);
  const [vehicle, setVehicle] = useState("ICE");

  async function optimizeRoute() {
    const res = await fetch("http://localhost:8000/optimize", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        stops: [
          {lat:37.7749,lon:-122.4194},
          {lat:37.7849,lon:-122.4094},
          {lat:37.7649,lon:-122.4294},
          {lat:37.7549,lon:-122.4194},
          {lat:37.7449,lon:-122.4094}
        ],
        vehicle_type: vehicle,
        traffic_level: traffic
      })
    });
    const data = await res.json();
    setRouteData(data);
  }

  return (
    <div style={{ padding: "20px" }}>
      <h2>AI Green Routing Demo</h2>

      <div style={{ marginBottom: "10px" }}>
        <label>Traffic Level: {traffic}</label>
        <input
          type="range"
          min="0"
          max="1"
          step="0.05"
          value={traffic}
          onChange={(e) => setTraffic(parseFloat(e.target.value))}
        />
      </div>

      <div style={{ marginBottom: "10px" }}>
        <label>Vehicle Type: </label>
        <select value={vehicle} onChange={(e) => setVehicle(e.target.value)}>
          <option value="ICE">ICE</option>
          <option value="EV">EV</option>
        </select>
      </div>

      <button onClick={optimizeRoute}>AI Optimize Route</button>

      {routeData && <ResultsView data={routeData} />}
      {routeData && <MapView route={routeData.best_route} />}
    </div>
  );
}
