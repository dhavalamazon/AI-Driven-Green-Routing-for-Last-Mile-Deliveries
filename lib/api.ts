export interface Location {
  lat: number
  lon: number
  name?: string
}

export interface OptimizeRequest {
  stops: Location[]
  vehicle_type: string
  fuel_type: string
  traffic_conditions: string
}

export interface OptimizeResponse {
  best_route: Location[]
  route_waypoints: Location[]
  route_mapping: number[]
  predicted_co2: number
  total_distance: number
  input_features: {
    vehicle_type: string
    fuel_type: string
    traffic_conditions: string
    derived_engine_size: number
    derived_speed: number
  }
}

const API_BASE_URL = "http://localhost:8000"

export async function optimizeRoute(request: OptimizeRequest): Promise<OptimizeResponse> {
  const response = await fetch(`${API_BASE_URL}/optimize`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(request),
  })

  if (!response.ok) {
    throw new Error(`API Error: ${response.statusText}`)
  }

  return response.json()
}

// Determine traffic conditions based on time and location context
export function getTrafficConditions(time: string, locations: Location[]): string {
  const hour = parseInt(time.split(':')[0])
  
  // If no locations selected yet, show generic pattern
  if (!locations || locations.length === 0) {
    if (hour >= 5 && hour < 7) return "Free flow"
    if (hour >= 7 && hour < 10) return "Heavy"
    if (hour >= 10 && hour < 16) return "Moderate"
    if (hour >= 16 && hour < 19) return "Heavy"
    return "Free flow"
  }
  
  // Analyze absolute location context first
  const avgLat = locations.reduce((sum, loc) => sum + loc.lat, 0) / locations.length
  const avgLng = locations.reduce((sum, loc) => sum + loc.lon, 0) / locations.length
  
  // Check if locations are in known urban centers (India focused)
  const isUrbanCenter = (
    // Tier-1 cities (Metro cities) - Expanded ranges
    (avgLat > 12.7 && avgLat < 13.2 && avgLng > 77.4 && avgLng < 77.8) || // Bangalore
    (avgLat > 18.9 && avgLat < 19.3 && avgLng > 72.7 && avgLng < 73.1) || // Mumbai
    (avgLat > 28.4 && avgLat < 28.8 && avgLng > 76.9 && avgLng < 77.4) || // Delhi
    (avgLat > 22.4 && avgLat < 22.8 && avgLng > 88.2 && avgLng < 88.5) || // Kolkata
    (avgLat > 12.8 && avgLat < 13.3 && avgLng > 80.1 && avgLng < 80.4) || // Chennai
    false
  )
  
  // Calculate coordinate spread for density analysis
  const latSpread = Math.max(...locations.map(l => l.lat)) - Math.min(...locations.map(l => l.lat))
  const lngSpread = Math.max(...locations.map(l => l.lon)) - Math.min(...locations.map(l => l.lon))
  const totalSpread = latSpread + lngSpread
  
  // Determine area type using both location and spread
  let areaType = "suburban"
  if (isUrbanCenter && totalSpread < 0.3) {
    areaType = "dense_urban"
  } else if (isUrbanCenter && totalSpread < 0.5) {
    areaType = "suburban"
  } else if (!isUrbanCenter) {
    areaType = "rural"
  }
  
  // Adjust traffic patterns based on area type
  let traffic
  if (areaType === "dense_urban") {
    if (hour >= 6 && hour < 10) traffic = "Heavy"
    else if (hour >= 10 && hour < 15) traffic = "Moderate"  
    else if (hour >= 15 && hour < 20) traffic = "Heavy"
    else traffic = "Moderate"
  } else if (areaType === "rural") {
    if (hour >= 7 && hour < 9) traffic = "Moderate"
    else if (hour >= 17 && hour < 19) traffic = "Moderate"
    else traffic = "Free flow"
  } else {
    if (hour >= 6 && hour < 9) traffic = "Heavy"
    else if (hour >= 9 && hour < 16) traffic = "Moderate"
    else if (hour >= 16 && hour < 19) traffic = "Heavy"
    else traffic = "Free flow"
  }
  
  return traffic
}
