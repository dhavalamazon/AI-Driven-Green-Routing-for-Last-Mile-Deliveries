"use client"

import dynamic from 'next/dynamic'

// Dynamically import the MapDisplay component to avoid SSR issues with Leaflet
const MapDisplay = dynamic(() => import('./map-display').then(mod => ({ default: mod.MapDisplay })), {
  ssr: false,
  loading: () => (
    <div className="h-full w-full flex items-center justify-center bg-gray-100">
      <div className="text-center space-y-2">
        <div className="w-8 h-8 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto"></div>
        <div className="text-sm text-gray-600">Loading Map...</div>
      </div>
    </div>
  )
})

export { MapDisplay as DynamicMapDisplay }
