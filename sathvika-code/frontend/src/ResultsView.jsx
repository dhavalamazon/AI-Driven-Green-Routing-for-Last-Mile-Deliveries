import React from "react";

export default function ResultsView({ data }) {
  if (!data) return null;

  const bestRoute = data.best_route;
  const predictedCO2 = data.predicted_co2.toFixed(2);

  return (
    <div style={{ marginTop: "20px", padding: "10px", border: "1px solid #ccc" }}>
      <h3>AI-Optimized Route</h3>
      <p><strong>Predicted CO₂:</strong> {predictedCO2} kg</p>
      <p><strong>Total Stops:</strong> {bestRoute.length}</p>
      <p><strong>Route Order:</strong> {bestRoute.map((stop, idx) => `Stop${idx+1}`).join(" → ")}</p>
    </div>
  );
}
