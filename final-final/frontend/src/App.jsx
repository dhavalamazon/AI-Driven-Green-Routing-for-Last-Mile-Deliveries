import React, { useState } from "react";
import MapView from "./MapView";
import LocationSelector from "./LocationSelector";
import ResultsView from "./ResultsView";

export default function App() {
  const [routeData, setRouteData] = useState(null);
  const [selectedLocations, setSelectedLocations] = useState([]);
  const [vehicleType, setVehicleType] = useState("Car");
  const [fuelType, setFuelType] = useState("Petrol");
  const [deliveryTime, setDeliveryTime] = useState("09:00");
  const [optimizationLog, setOptimizationLog] = useState([]);
  const [isOptimizing, setIsOptimizing] = useState(false);

  // Determine traffic conditions based on time and location context
  function getTrafficConditions(time, locations) {
    const hour = parseInt(time.split(':')[0]);
    
    // If no locations selected yet, show generic pattern
    if (!locations || locations.length === 0) {
      if (hour >= 5 && hour < 7) return "Free flow";
      if (hour >= 7 && hour < 10) return "Heavy";
      if (hour >= 10 && hour < 16) return "Moderate";
      if (hour >= 16 && hour < 19) return "Heavy";
      return "Free flow";
    }
    
    console.log('DEBUG: Locations:', locations.length, 'Time:', time);
    
    // Analyze absolute location context first
    const avgLat = locations.reduce((sum, loc) => sum + loc.lat, 0) / locations.length;
    const avgLng = locations.reduce((sum, loc) => sum + loc.lon, 0) / locations.length;
    
    // Check if locations are in known urban centers
    const isUrbanCenter = (
      // Tier-1 cities (Metro cities) - Expanded ranges
      (avgLat > 12.7 && avgLat < 13.2 && avgLng > 77.4 && avgLng < 77.8) || // Bangalore (includes Electronic City, Whitefield)
      (avgLat > 18.9 && avgLat < 19.3 && avgLng > 72.7 && avgLng < 73.1) || // Mumbai (includes Navi Mumbai, Thane)
      (avgLat > 28.4 && avgLat < 28.8 && avgLng > 76.9 && avgLng < 77.4) || // Delhi (includes Gurgaon, Noida)
      (avgLat > 22.4 && avgLat < 22.8 && avgLng > 88.2 && avgLng < 88.5) || // Kolkata (includes Salt Lake, Howrah)
      (avgLat > 12.8 && avgLat < 13.3 && avgLng > 80.1 && avgLng < 80.4) || // Chennai (includes suburbs)
      (avgLat > 17.2 && avgLat < 17.6 && avgLng > 78.3 && avgLng < 78.6) || // Hyderabad (includes Cyberabad)
      
      // Tier-2 cities (Major urban centers) - Expanded ranges
      (avgLat > 18.3 && avgLat < 18.7 && avgLng > 73.7 && avgLng < 74.0) || // Pune (includes Pimpri-Chinchwad)
      (avgLat > 22.9 && avgLat < 23.2 && avgLng > 72.4 && avgLng < 72.7) || // Ahmedabad (includes suburbs)
      (avgLat > 26.7 && avgLat < 27.1 && avgLng > 75.6 && avgLng < 76.0) || // Jaipur (includes suburbs)
      (avgLat > 21.0 && avgLat < 21.4 && avgLng > 78.9 && avgLng < 79.2) || // Nagpur (expanded)
      (avgLat > 15.2 && avgLat < 15.6 && avgLng > 75.0 && avgLng < 75.3) || // Hubli-Dharwad
      (avgLat > 26.0 && avgLat < 26.4 && avgLng > 91.6 && avgLng < 91.9) || // Guwahati (expanded)
      (avgLat > 10.9 && avgLat < 11.3 && avgLng > 76.8 && avgLng < 77.2) || // Coimbatore (expanded)
      (avgLat > 8.3 && avgLat < 8.7 && avgLng > 76.8 && avgLng < 77.2) ||   // Thiruvananthapuram
      (avgLat > 9.8 && avgLat < 10.2 && avgLng > 76.1 && avgLng < 76.5) || // Kochi (expanded)
      (avgLat > 20.1 && avgLat < 20.5 && avgLng > 85.7 && avgLng < 86.1) || // Bhubaneswar
      
      false
    );
    
    // Calculate coordinate spread for density analysis
    const latSpread = Math.max(...locations.map(l => l.lat)) - Math.min(...locations.map(l => l.lat));
    const lngSpread = Math.max(...locations.map(l => l.lon)) - Math.min(...locations.map(l => l.lon));
    const totalSpread = latSpread + lngSpread;
    
    // Determine area type using both location and spread
    let areaType = "suburban";
    if (isUrbanCenter && totalSpread < 0.3) {
      areaType = "dense_urban";  // In city center AND reasonably concentrated
    } else if (isUrbanCenter && totalSpread < 0.5) {
      areaType = "suburban";     // In city but spread out
    } else if (!isUrbanCenter) {
      areaType = "rural";        // Outside all known cities
    }
    
    console.log('DEBUG: avgLat:', avgLat.toFixed(4), 'avgLng:', avgLng.toFixed(4));
    console.log('DEBUG: isUrbanCenter:', isUrbanCenter, 'totalSpread:', totalSpread.toFixed(4));
    console.log('DEBUG: areaType:', areaType, 'hour:', hour);
    
    // Adjust traffic patterns based on area type
    let traffic;
    if (areaType === "dense_urban") {
      if (hour >= 6 && hour < 10) traffic = "Heavy";
      else if (hour >= 10 && hour < 15) traffic = "Moderate";
      else if (hour >= 15 && hour < 20) traffic = "Heavy";
      else traffic = "Moderate";  // Still some traffic at night
    } else if (areaType === "rural") {
      if (hour >= 7 && hour < 9) traffic = "Moderate";
      else if (hour >= 17 && hour < 19) traffic = "Moderate";
      else traffic = "Free flow";
    } else {
      if (hour >= 6 && hour < 9) traffic = "Heavy";
      else if (hour >= 9 && hour < 16) traffic = "Moderate";
      else if (hour >= 16 && hour < 19) traffic = "Heavy";
      else traffic = "Free flow";
    }
    
    console.log('DEBUG: Final traffic:', traffic);
    return traffic;
  }

  async function optimizeRoute() {
    if (selectedLocations.length < 2) {
      alert("Please select at least 2 locations on the map");
      return;
    }

    setIsOptimizing(true);
    setOptimizationLog([]);
    setRouteData(null);
    
    // Add initial log entries
    const addLog = (message, type = 'info') => {
      setOptimizationLog(prev => [...prev, { message, type, timestamp: new Date().toLocaleTimeString() }]);
    };
    
    addLog('🚀 Starting AI route optimization...', 'info');
    addLog(`📍 Analyzing ${selectedLocations.length} delivery locations`, 'info');
    addLog(`🚛 Vehicle: ${vehicleType} (${fuelType})`, 'info');
    addLog(`🚦 Traffic: ${getTrafficConditions(deliveryTime, selectedLocations)}`, 'info');
    
    setTimeout(() => addLog('🧠 Generating route alternatives...', 'process'), 500);
    setTimeout(() => addLog('🗺️ Calculating real road distances...', 'process'), 1000);
    setTimeout(() => addLog('⚡ AI evaluating CO2 emissions...', 'process'), 1500);

    try {
      const res = await fetch("http://localhost:8000/optimize", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          stops: selectedLocations,
          vehicle_type: vehicleType,
          fuel_type: fuelType,
          traffic_conditions: getTrafficConditions(deliveryTime, selectedLocations)
        })
      });
      const data = await res.json();
      
      addLog(`✅ Optimization complete!`, 'success');
      addLog(`🎯 Best route: ${data.total_distance}km, ${data.predicted_co2}kg CO2`, 'success');
      
      setRouteData(data);
    } catch (error) {
      addLog(`❌ Error: ${error.message}`, 'error');
    } finally {
      setIsOptimizing(false);
    }
  }

  return (
    <div style={{ 
      minHeight: "100vh", 
      backgroundColor: "#f5f5f5", 
      padding: "20px 0"
    }}>
      <div style={{ 
        maxWidth: "1200px", 
        margin: "0 auto", 
        padding: "0 20px"
      }}>
        <header style={{
          textAlign: "center",
          marginBottom: "40px",
          backgroundColor: "white",
          padding: "30px",
          borderRadius: "15px",
          boxShadow: "0 4px 20px rgba(0,0,0,0.1)"
        }}>
          <h1 style={{ 
            color: "#2E7D32", 
            fontSize: "2.5rem", 
            marginBottom: "10px",
            fontWeight: "bold"
          }}>🌱 AI Green Routing System</h1>
          <p style={{
            color: "#666",
            fontSize: "1.1rem",
            margin: "0"
          }}>Optimize delivery routes for minimal CO₂ emissions using AI</p>
        </header>
      
        <div style={{ 
          display: "grid", 
          gridTemplateColumns: "1fr 1fr", 
          gap: "20px", 
          marginBottom: "30px"
        }}>
          <div style={{
            backgroundColor: "white",
            padding: "25px",
            borderRadius: "15px",
            boxShadow: "0 4px 15px rgba(0,0,0,0.1)"
          }}>
            <h3 style={{ color: "#2E7D32", marginBottom: "20px", fontSize: "1.3rem" }}>🚛 Vehicle Configuration</h3>
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "15px" }}>
        
              <div>
                <label style={{ display: "block", fontWeight: "600", marginBottom: "8px", color: "#333" }}>Vehicle Type:</label>
                <select value={vehicleType} onChange={(e) => setVehicleType(e.target.value)} style={{ 
                  width: "100%", 
                  padding: "12px", 
                  borderRadius: "8px", 
                  border: "2px solid #e0e0e0",
                  fontSize: "16px",
                  backgroundColor: "white"
                }}>
                  <option value="Car">🚗 Car</option>
                  <option value="Truck">🚛 Truck</option>
                  <option value="Bus">🚌 Bus</option>
                  <option value="Motorcycle">🏍️ Motorcycle</option>
                </select>
              </div>

              <div>
                <label style={{ display: "block", fontWeight: "600", marginBottom: "8px", color: "#333" }}>Fuel Type:</label>
                <select value={fuelType} onChange={(e) => setFuelType(e.target.value)} style={{ 
                  width: "100%", 
                  padding: "12px", 
                  borderRadius: "8px", 
                  border: "2px solid #e0e0e0",
                  fontSize: "16px",
                  backgroundColor: "white"
                }}>
                  <option value="Electric">⚡ Electric</option>
                  <option value="Hybrid">🔋 Hybrid</option>
                  <option value="Petrol">⛽ Petrol</option>
                  <option value="Diesel">🛢️ Diesel</option>
                </select>
              </div>

            </div>
            
            <div style={{ marginTop: "15px" }}>
              <label style={{ display: "block", fontWeight: "600", marginBottom: "8px", color: "#333" }}>Delivery Time:</label>
              {selectedLocations.length === 0 && (
                <p style={{ fontSize: "12px", color: "#666", margin: "0 0 8px 0" }}>
                  📍 Select locations first for location-aware traffic patterns
                </p>
              )}
              <div style={{ display: "flex", gap: "10px", alignItems: "center" }}>
                <input 
                  type="time" 
                  value={deliveryTime} 
                  onChange={(e) => setDeliveryTime(e.target.value)} 
                  style={{ 
                    padding: "12px", 
                    borderRadius: "8px", 
                    border: "2px solid #e0e0e0",
                    fontSize: "16px",
                    backgroundColor: "white",
                    width: "140px"
                  }}
                />
                <span style={{ 
                  padding: "6px 12px", 
                  backgroundColor: "#f0f8f0", 
                  borderRadius: "20px", 
                  fontSize: "13px", 
                  color: "#2E7D32",
                  fontWeight: "500"
                }}>
                  {getTrafficConditions(deliveryTime, selectedLocations) === "Free flow" ? "🟢 Free" : 
                   getTrafficConditions(deliveryTime, selectedLocations) === "Moderate" ? "🟡 Moderate" : "🔴 Heavy"}
                </span>
              </div>
            </div>
          </div>

          <div style={{
            backgroundColor: "white",
            padding: "25px",
            borderRadius: "15px",
            boxShadow: "0 4px 15px rgba(0,0,0,0.1)"
          }}>
            <h3 style={{ color: "#2E7D32", marginBottom: "15px", fontSize: "1.3rem" }}>📍 Select Locations</h3>
            <p style={{ fontSize: "16px", color: "#666", marginBottom: "20px" }}>
              Click on the map to add pickup and delivery locations 
              <span style={{ 
                backgroundColor: "#e8f5e8", 
                padding: "4px 8px", 
                borderRadius: "12px", 
                fontWeight: "bold", 
                color: "#2E7D32" 
              }}>({selectedLocations.length} selected)</span>
            </p>
            {selectedLocations.length > 0 && (
              <p style={{ fontSize: "14px", color: "#666", marginTop: "-10px", marginBottom: "15px" }}>
                🌆 Traffic patterns adapted to your delivery area
              </p>
            )}
            <LocationSelector 
              selectedLocations={selectedLocations}
              onLocationsChange={setSelectedLocations}
            />
          </div>
          
          {/* Live Optimization Log */}
          <div style={{
            backgroundColor: "white",
            padding: "25px",
            borderRadius: "15px",
            boxShadow: "0 4px 15px rgba(0,0,0,0.1)"
          }}>
            <h3 style={{ color: "#2E7D32", marginBottom: "15px", fontSize: "1.3rem" }}>🔄 Live Optimization Log</h3>
            <div style={{
              height: "300px",
              overflowY: "auto",
              backgroundColor: "#f8f9fa",
              padding: "15px",
              borderRadius: "8px",
              border: "1px solid #e9ecef"
            }}>
              {optimizationLog.length === 0 ? (
                <p style={{ color: "#666", fontStyle: "italic", margin: 0 }}>Click "AI Optimize Route" to see live progress...</p>
              ) : (
                optimizationLog.map((log, index) => (
                  <div key={index} style={{
                    marginBottom: "8px",
                    padding: "8px 12px",
                    borderRadius: "6px",
                    backgroundColor: log.type === 'success' ? '#d4edda' : 
                                   log.type === 'error' ? '#f8d7da' : 
                                   log.type === 'process' ? '#fff3cd' : '#e2e3e5',
                    borderLeft: `4px solid ${log.type === 'success' ? '#28a745' : 
                                             log.type === 'error' ? '#dc3545' : 
                                             log.type === 'process' ? '#ffc107' : '#6c757d'}`,
                    fontSize: "14px"
                  }}>
                    <span style={{ color: "#666", fontSize: "12px" }}>[{log.timestamp}]</span>
                    <br />
                    {log.message}
                  </div>
                ))
              )}
              {isOptimizing && (
                <div style={{ textAlign: "center", padding: "10px" }}>
                  <div style={{
                    display: "inline-block",
                    width: "20px",
                    height: "20px",
                    border: "3px solid #f3f3f3",
                    borderTop: "3px solid #4CAF50",
                    borderRadius: "50%",
                    animation: "spin 1s linear infinite"
                  }}></div>
                  <style>{`
                    @keyframes spin {
                      0% { transform: rotate(0deg); }
                      100% { transform: rotate(360deg); }
                    }
                  `}</style>
                </div>
              )}
            </div>
          </div>
        </div>

        <div style={{ textAlign: "center", marginBottom: "30px" }}>
          <button 
            onClick={optimizeRoute}
            disabled={selectedLocations.length < 2 || isOptimizing}
            style={{ 
              backgroundColor: selectedLocations.length < 2 || isOptimizing ? "#ccc" : "#4CAF50", 
              color: "white", 
              padding: "18px 40px", 
              border: "none", 
              borderRadius: "12px", 
              fontSize: "18px", 
              fontWeight: "bold",
              cursor: selectedLocations.length < 2 || isOptimizing ? "not-allowed" : "pointer",
              minWidth: "300px",
              boxShadow: selectedLocations.length >= 2 && !isOptimizing ? "0 4px 15px rgba(76, 175, 80, 0.3)" : "none",
              transition: "all 0.3s ease"
            }}
          >
            {isOptimizing ? '⏳ Optimizing...' : `🚀 AI Optimize Route (${selectedLocations.length} locations)`}
          </button>
        </div>

        {routeData && (
          <div style={{ marginTop: "30px" }}>
            <ResultsView data={routeData} />
            <div style={{
              backgroundColor: "white",
              padding: "30px",
              borderRadius: "15px",
              boxShadow: "0 4px 15px rgba(0,0,0,0.1)",
              marginTop: "20px"
            }}>
              <h2 style={{ 
                color: "#2E7D32", 
                marginBottom: "20px", 
                fontSize: "1.5rem",
                textAlign: "center"
              }}>🗺️ Interactive Route Map</h2>
              <MapView 
                route={routeData.best_route} 
                routeMapping={routeData.route_mapping}
                routeWaypoints={routeData.route_waypoints}
              />
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
