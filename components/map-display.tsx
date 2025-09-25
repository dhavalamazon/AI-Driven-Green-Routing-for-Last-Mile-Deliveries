"use client"

import { MapContainer, TileLayer, Marker, Popup, Polyline, ZoomControl } from 'react-leaflet'
import 'leaflet/dist/leaflet.css'
import locations from '../data/locations.json'

export function MapDisplay() {
  const { depot, deliveryStops, routes } = locations
  
  return (
    <div className="h-full w-full">
      <MapContainer
        center={[depot.lat, depot.lng]}
        zoom={13}
        className="h-full w-full"
        zoomControl={false}
      >
        <ZoomControl position="bottomleft" />
        <TileLayer
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        />
        
        {/* Depot Marker */}
        <Marker position={[depot.lat, depot.lng]}>
          <Popup>{depot.name}</Popup>
        </Marker>
        
        {/* Delivery Stop Markers */}
        {deliveryStops.map((stop) => (
          <Marker key={stop.id} position={[stop.lat, stop.lng]}>
            <Popup>{stop.name}</Popup>
          </Marker>
        ))}
        
        {/* Fastest Route */}
        <Polyline
          positions={routes.fastest}
          color="red"
          weight={3}
          dashArray="10, 10"
        />
        
        {/* Low Carbon Route */}
        <Polyline
          positions={routes.lowCarbon}
          color="#16a34a"
          weight={3}
        />
      </MapContainer>
    </div>
  )
}
