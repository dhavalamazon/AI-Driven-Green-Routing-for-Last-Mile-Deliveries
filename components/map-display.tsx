"use client"

import { useEffect, useRef } from 'react'
import { MapContainer, TileLayer, Marker, Popup, Polyline, ZoomControl, useMapEvents } from 'react-leaflet'
import { useDelivery } from "@/contexts/delivery-context"
import { Icon, LatLngBounds } from 'leaflet'
import 'leaflet/dist/leaflet.css'

// Fix for default markers in Leaflet with Next.js
delete (Icon.Default.prototype as any)._getIconUrl
Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
})

// Custom marker icons
const createCustomIcon = (color: string, number?: number) => new Icon({
  iconUrl: `https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-${color}.png`,
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41]
})

const blueIcon = createCustomIcon('blue')
const greenIcon = createCustomIcon('green')
const redIcon = createCustomIcon('red')

function MapClickHandler() {
  const { addLocation } = useDelivery()
  
  useMapEvents({
    click: (e) => {
      const { lat, lng } = e.latlng
      addLocation({
        lat: lat,
        lon: lng,
        name: `Location ${Date.now()}`
      })
    }
  })
  
  return null
}

function FitBoundsHandler() {
  const { selectedLocations, routeData } = useDelivery()
  const mapRef = useRef<any>(null)
  
  const map = useMapEvents({})
  
  useEffect(() => {
    if (selectedLocations.length > 0) {
      const bounds = new LatLngBounds(
        selectedLocations.map(location => [location.lat, location.lon])
      )
      if (routeData?.route_waypoints && routeData.route_waypoints.length > 0) {
        routeData.route_waypoints.forEach(point => {
          bounds.extend([point.lat, point.lon])
        })
      }
      map.fitBounds(bounds, { padding: [20, 20] })
    }
  }, [selectedLocations, routeData, map])
  
  return null
}

export function MapDisplay() {
  const { selectedLocations, routeData, removeLocation } = useDelivery()
  
  // Default center (Bangalore, India - Amazon's major delivery hub)
  const defaultCenter: [number, number] = [12.9716, 77.5946]
  
  return (
    <div className="h-full w-full relative">
      <MapContainer
        center={defaultCenter}
        zoom={13}
        className="h-full w-full"
        zoomControl={false}
        style={{ background: '#f0f9ff' }}
      >
        <ZoomControl position="bottomleft" />
        
        {/* Google Maps style tile layer */}
        <TileLayer
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          className="map-tiles"
        />
        
        {/* Map click handler for adding locations */}
        <MapClickHandler />
        <FitBoundsHandler />
        
        {/* Selected Location Markers */}
        {selectedLocations.map((location, index) => (
          <Marker 
            key={index} 
            position={[location.lat, location.lon]}
            icon={index === 0 ? greenIcon : blueIcon}
          >
            <Popup>
              <div className="text-center space-y-2">
                <div className="font-semibold">
                  {index === 0 ? '📍 Start Location' : `🎯 Delivery ${index}`}
                </div>
                <div className="text-xs text-gray-600">
                  {location.lat.toFixed(4)}, {location.lon.toFixed(4)}
                </div>
                <button
                  onClick={() => removeLocation(index)}
                  className="text-red-500 hover:text-red-700 text-xs underline"
                >
                  Remove Location
                </button>
              </div>
            </Popup>
          </Marker>
        ))}
        
        {/* Optimized Route */}
        {routeData?.route_waypoints && routeData.route_waypoints.length > 1 && (
          <Polyline
            positions={routeData.route_waypoints.map(point => [point.lat, point.lon])}
            color="#16a34a"
            weight={4}
            opacity={0.8}
            className="route-line"
          />
        )}
        
        {/* Route markers for optimized stops */}
        {routeData?.best_route && routeData.best_route.map((location, index) => (
          <Marker 
            key={`route-${index}`} 
            position={[location.lat, location.lon]}
            icon={redIcon}
          >
            <Popup>
              <div className="text-center space-y-2">
                <div className="font-semibold">
                  🚚 Stop {index + 1}
                </div>
                <div className="text-xs text-gray-600">
                  Optimized Route Order
                </div>
                <div className="text-xs text-green-600">
                  {location.lat.toFixed(4)}, {location.lon.toFixed(4)}
                </div>
              </div>
            </Popup>
          </Marker>
        ))}
      </MapContainer>
      
      {/* Map Instructions Overlay */}
      {selectedLocations.length === 0 && (
        <div className="absolute top-4 left-1/2 transform -translate-x-1/2 z-[1000] bg-white/90 backdrop-blur-sm px-4 py-2 rounded-lg shadow-lg">
          <div className="text-sm text-gray-700 text-center">
            <div className="font-medium">🗺️ Click anywhere on the map to add delivery locations</div>
            <div className="text-xs text-gray-500 mt-1">Start with your depot/warehouse, then add delivery stops</div>
          </div>
        </div>
      )}
      
      {/* Route Info Overlay */}
      {routeData && (
        <div className="absolute top-4 right-4 z-[1000] bg-green-600 text-white px-4 py-2 rounded-lg shadow-lg">
          <div className="text-sm font-medium">
            ✅ Optimized Route: {routeData.total_distance}km
          </div>
          <div className="text-xs opacity-90">
            CO₂: {routeData.predicted_co2}kg
          </div>
        </div>
      )}
      
      <style jsx>{`
        .map-tiles {
          filter: contrast(1.1) saturate(1.1);
        }
        .route-line {
          filter: drop-shadow(2px 2px 4px rgba(0,0,0,0.3));
        }
      `}</style>
    </div>
  )
}
