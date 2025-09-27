"use client"

import React, { createContext, useContext, useState, ReactNode } from 'react'
import { Location, OptimizeResponse, optimizeRoute, getTrafficConditions } from '@/lib/api'

interface DeliveryContextType {
  // Location management
  selectedLocations: Location[]
  setSelectedLocations: (locations: Location[]) => void
  depot: Location | null
  setDepot: (depot: Location | null) => void
  
  // Vehicle configuration
  vehicleType: string
  setVehicleType: (type: string) => void
  fuelType: string
  setFuelType: (type: string) => void
  deliveryTime: string
  setDeliveryTime: (time: string) => void
  
  // Optimization state
  isOptimizing: boolean
  routeData: OptimizeResponse | null
  optimizationLog: Array<{ message: string; type: string; timestamp: string }>
  
  // Actions
  addLocation: (location: Location) => void
  removeLocation: (index: number) => void
  optimizeRoute: () => Promise<void>
  clearOptimization: () => void
  
  // Computed values
  trafficConditions: string
}

const DeliveryContext = createContext<DeliveryContextType | undefined>(undefined)

export function DeliveryProvider({ children }: { children: ReactNode }) {
  const [selectedLocations, setSelectedLocations] = useState<Location[]>([])
  const [depot, setDepot] = useState<Location | null>(null)
  const [vehicleType, setVehicleType] = useState("Car")
  const [fuelType, setFuelType] = useState("Petrol")
  const [deliveryTime, setDeliveryTime] = useState("09:00")
  const [isOptimizing, setIsOptimizing] = useState(false)
  const [routeData, setRouteData] = useState<OptimizeResponse | null>(null)
  const [optimizationLog, setOptimizationLog] = useState<Array<{ message: string; type: string; timestamp: string }>>([])

  const trafficConditions = getTrafficConditions(deliveryTime, selectedLocations)

  const addLocation = (location: Location) => {
    setSelectedLocations(prev => [...prev, location])
  }

  const removeLocation = (index: number) => {
    setSelectedLocations(prev => prev.filter((_, i) => i !== index))
  }

  const addLog = (message: string, type = 'info') => {
    setOptimizationLog(prev => [...prev, { 
      message, 
      type, 
      timestamp: new Date().toLocaleTimeString() 
    }])
  }

  const handleOptimizeRoute = async () => {
    if (selectedLocations.length < 2) {
      alert("Please select at least 2 locations on the map")
      return
    }

    setIsOptimizing(true)
    setOptimizationLog([])
    setRouteData(null)
    
    addLog('🚀 Starting AI route optimization...', 'info')
    addLog(`📍 Analyzing ${selectedLocations.length} delivery locations`, 'info')
    addLog(`🚛 Vehicle: ${vehicleType} (${fuelType})`, 'info')
    addLog(`🚦 Traffic: ${trafficConditions}`, 'info')
    
    setTimeout(() => addLog('🧠 Generating route alternatives...', 'process'), 500)
    setTimeout(() => addLog('🗺️ Calculating real road distances...', 'process'), 1000)
    setTimeout(() => addLog('⚡ AI evaluating CO2 emissions...', 'process'), 1500)

    try {
      const response = await optimizeRoute({
        stops: selectedLocations,
        vehicle_type: vehicleType,
        fuel_type: fuelType,
        traffic_conditions: trafficConditions
      })
      
      addLog(`✅ Optimization complete!`, 'success')
      addLog(`🎯 Best route: ${response.total_distance}km, ${response.predicted_co2}kg CO2`, 'success')
      
      setRouteData(response)
    } catch (error) {
      addLog(`❌ Error: ${error instanceof Error ? error.message : 'Unknown error'}`, 'error')
    } finally {
      setIsOptimizing(false)
    }
  }

  const clearOptimization = () => {
    setRouteData(null)
    setOptimizationLog([])
  }

  const value: DeliveryContextType = {
    selectedLocations,
    setSelectedLocations,
    depot,
    setDepot,
    vehicleType,
    setVehicleType,
    fuelType,
    setFuelType,
    deliveryTime,
    setDeliveryTime,
    isOptimizing,
    routeData,
    optimizationLog,
    addLocation,
    removeLocation,
    optimizeRoute: handleOptimizeRoute,
    clearOptimization,
    trafficConditions
  }

  return (
    <DeliveryContext.Provider value={value}>
      {children}
    </DeliveryContext.Provider>
  )
}

export function useDelivery() {
  const context = useContext(DeliveryContext)
  if (context === undefined) {
    throw new Error('useDelivery must be used within a DeliveryProvider')
  }
  return context
}
