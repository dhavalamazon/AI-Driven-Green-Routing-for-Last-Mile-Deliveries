import React from "react";

export default function ResultsView({ data }) {
  console.log('ResultsView received data:', data);
  if (!data) {
    console.log('No data provided to ResultsView');
    return null;
  }

  const bestRoute = data.best_route;
  const predictedCO2 = data.predicted_co2.toFixed(2);
  const totalDistance = data.total_distance;
  const trafficAnalysis = data.traffic_analysis;
  const routeFeatures = data.route_features;

  return (
    <div style={{ marginTop: "20px", padding: "15px", border: "2px solid #4CAF50", borderRadius: "8px", backgroundColor: "#f9f9f9" }}>
      <h3 style={{ color: "#2E7D32", marginBottom: "15px" }}>🎯 AI-Optimized Green Route</h3>
      
      {/* Main Results */}
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: "15px", marginBottom: "15px" }}>
        <div style={{ padding: "10px", backgroundColor: "#E8F5E8", borderRadius: "5px", textAlign: "center" }}>
          <strong style={{ color: "#1B5E20" }}>CO₂ Emissions</strong>
          <div style={{ fontSize: "24px", color: "#2E7D32" }}>{predictedCO2} kg</div>
        </div>
        <div style={{ padding: "10px", backgroundColor: "#E3F2FD", borderRadius: "5px", textAlign: "center" }}>
          <strong style={{ color: "#0D47A1" }}>Distance</strong>
          <div style={{ fontSize: "24px", color: "#1565C0" }}>{totalDistance} km</div>
        </div>
        <div style={{ padding: "10px", backgroundColor: "#FFF3E0", borderRadius: "5px", textAlign: "center" }}>
          <strong style={{ color: "#E65100" }}>Stops</strong>
          <div style={{ fontSize: "24px", color: "#F57C00" }}>{bestRoute.length}</div>
        </div>
      </div>

      {/* Shortest vs Greenest Comparison */}
      {data.shortest_route_comparison && (
        <div style={{ marginBottom: "15px", padding: "10px", backgroundColor: "#FFF8E1", borderRadius: "5px", border: "1px solid #FFB74D" }}>
          <h4 style={{ margin: "0 0 10px 0", color: "#E65100" }}>📊 Shortest vs Greenest Route Comparison</h4>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "15px" }}>
            <div style={{ padding: "8px", backgroundColor: "#FFEBEE", borderRadius: "4px" }}>
              <strong style={{ color: "#C62828" }}>📏 Shortest Route</strong>
              <div style={{ fontSize: "12px", marginTop: "5px" }}>
                <div>Route: {data.shortest_route_comparison.route_mapping.join(' → ')}</div>
                <div>Distance: {data.shortest_route_comparison.distance}km</div>
                <div>CO₂: {data.shortest_route_comparison.co2}kg</div>
              </div>
            </div>
            <div style={{ padding: "8px", backgroundColor: "#E8F5E8", borderRadius: "4px" }}>
              <strong style={{ color: "#2E7D32" }}>🌱 AI-Optimized Route</strong>
              <div style={{ fontSize: "12px", marginTop: "5px" }}>
                <div>Route: {data.route_mapping.join(' → ')}</div>
                <div>Distance: {data.total_distance}km</div>
                <div>CO₂: {data.predicted_co2}kg</div>
              </div>
            </div>
          </div>
          {data.shortest_route_comparison.is_different_route && data.shortest_route_comparison.co2_savings > 0 && (
            <div style={{ marginTop: "10px", padding: "8px", backgroundColor: "#E8F5E8", borderRadius: "3px", fontSize: "12px", color: "#2E7D32", textAlign: "center" }}>
              🌱 <strong>GREEN CHOICE:</strong> {data.shortest_route_comparison.green_choice_message}
            </div>
          )}
          {data.shortest_route_comparison.is_different_route && data.shortest_route_comparison.co2_savings <= 0 && (
            <div style={{ marginTop: "10px", padding: "8px", backgroundColor: "#FFF3E0", borderRadius: "3px", fontSize: "12px", color: "#E65100", textAlign: "center" }}>
              ℹ️ In current traffic conditions, shortest route is also the greenest
            </div>
          )}
          {!data.shortest_route_comparison.is_different_route && (
            <div style={{ marginTop: "10px", padding: "8px", backgroundColor: "#E3F2FD", borderRadius: "3px", fontSize: "12px", color: "#1565C0", textAlign: "center" }}>
              ℹ️ Same route chosen for both shortest and greenest
            </div>
          )}
        </div>
      )}

      {/* Input Features Used for AI Prediction */}
      {data.input_features && (
        <div style={{ marginBottom: "15px", padding: "10px", backgroundColor: "#FFF", borderRadius: "5px", border: "1px solid #ddd" }}>
          <h4 style={{ margin: "0 0 10px 0", color: "#333" }}>🤖 AI Model Input Features</h4>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: "10px", fontSize: "14px" }}>
            <div><strong>Vehicle:</strong> {data.input_features.vehicle_type}</div>
            <div><strong>Fuel:</strong> {data.input_features.fuel_type}</div>
            <div><strong>Traffic:</strong> {data.input_features.traffic_conditions}</div>
            <div><strong>Engine:</strong> {data.input_features.derived_engine_size}L (auto)</div>
            <div><strong>Speed:</strong> {data.input_features.derived_speed} km/h (auto)</div>
            <div><strong>Model:</strong> Neural Network</div>
          </div>
          <div style={{ marginTop: "10px", padding: "8px", backgroundColor: "#E3F2FD", borderRadius: "3px", fontSize: "12px", color: "#1565C0" }}>
            💡 <strong>Note:</strong> The AI learned from real data that smaller engines can be less efficient when working harder under certain conditions (speed, traffic, vehicle type).
          </div>
        </div>
      )}


    </div>
  );
}
