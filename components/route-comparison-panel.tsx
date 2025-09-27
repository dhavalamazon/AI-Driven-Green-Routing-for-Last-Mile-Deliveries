"use client"

import { useState } from "react"
import { useDelivery } from "@/contexts/delivery-context"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Separator } from "@/components/ui/separator"
import { ChevronDown, ChevronUp, MapPin, Clock, Fuel, Zap } from "lucide-react"

export function RouteComparisonPanel() {
  const [isPanelOpen, setIsPanelOpen] = useState(true)
  const {
    routeData,
    optimizationLog,
    isOptimizing,
    selectedLocations,
    vehicleType,
    fuelType,
    trafficConditions,
    clearOptimization
  } = useDelivery()

  const togglePanel = () => setIsPanelOpen(!isPanelOpen)

  const getLogTypeStyles = (type: string) => {
    switch (type) {
      case 'success': return 'bg-green-50 border-green-200 text-green-800'
      case 'error': return 'bg-red-50 border-red-200 text-red-800'
      case 'process': return 'bg-yellow-50 border-yellow-200 text-yellow-800'
      default: return 'bg-blue-50 border-blue-200 text-blue-800'
    }
  }

  return (
    <div className="bg-white rounded-t-lg shadow-lg lg:rounded-l-lg lg:rounded-t-none h-full flex flex-col">
      <div className="flex justify-between items-center p-4 border-b lg:hidden">
        <h2 className="text-lg font-semibold">Route Analysis</h2>
        <Button variant="ghost" size="icon" onClick={togglePanel}>
          {isPanelOpen ? <ChevronDown className="h-5 w-5" /> : <ChevronUp className="h-5 w-5" />}
        </Button>
      </div>

      <div className={`flex-1 overflow-y-auto p-4 space-y-4 ${isPanelOpen ? "block" : "hidden"} lg:block`}>
        
        {/* Current Configuration */}
        <Card className="shadow-sm">
          <CardHeader className="pb-3">
            <CardTitle className="text-base flex items-center gap-2">
              <MapPin className="h-4 w-4" />
              Current Setup
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">Locations</span>
              <Badge variant={selectedLocations.length >= 2 ? "default" : "secondary"}>
                {selectedLocations.length} selected
              </Badge>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">Vehicle</span>
              <span className="text-sm font-medium">{vehicleType} ({fuelType})</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">Traffic</span>
              <Badge className={
                trafficConditions === "Free flow" ? "bg-green-500" :
                trafficConditions === "Moderate" ? "bg-yellow-500" : "bg-red-500"
              }>
                {trafficConditions}
              </Badge>
            </div>
          </CardContent>
        </Card>

        {/* Optimization Results */}
        {routeData && (
          <Card className="shadow-sm border-green-200">
            <CardHeader className="pb-3 bg-green-50">
              <CardTitle className="text-base flex items-center gap-2 text-green-800">
                <Zap className="h-4 w-4" />
                Optimized Route Results
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4 pt-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="text-center p-3 bg-blue-50 rounded-lg">
                  <div className="text-2xl font-bold text-blue-600">
                    {routeData.total_distance}km
                  </div>
                  <div className="text-xs text-blue-600">Total Distance</div>
                </div>
                <div className="text-center p-3 bg-green-50 rounded-lg">
                  <div className="text-2xl font-bold text-green-600">
                    {routeData.predicted_co2}kg
                  </div>
                  <div className="text-xs text-green-600">CO₂ Emissions</div>
                </div>
              </div>
              
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">Route Order:</span>
                  <span className="font-medium">
                    {routeData.route_mapping.join(' → ')}
                  </span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">Delivery Stops:</span>
                  <span className="font-medium">{routeData.best_route.length}</span>
                </div>
              </div>

              <Button 
                onClick={clearOptimization}
                variant="outline" 
                size="sm" 
                className="w-full"
              >
                Clear & Start New
              </Button>
            </CardContent>
          </Card>
        )}

        {/* Live Optimization Log */}
        <Card className="shadow-sm">
          <CardHeader className="pb-3">
            <CardTitle className="text-base flex items-center gap-2">
              <Clock className="h-4 w-4" />
              Live Optimization Log
              {isOptimizing && (
                <div className="w-3 h-3 border border-blue-500 border-t-transparent rounded-full animate-spin ml-2"></div>
              )}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-64 overflow-y-auto space-y-2">
              {optimizationLog.length === 0 ? (
                <div className="text-sm text-gray-500 italic text-center py-8">
                  Select locations and click optimize to see live progress...
                </div>
              ) : (
                optimizationLog.map((log, index) => (
                  <div
                    key={index}
                    className={`text-xs p-2 rounded border ${getLogTypeStyles(log.type)}`}
                  >
                    <div className="flex justify-between items-start mb-1">
                      <span className="font-mono text-xs opacity-70">
                        [{log.timestamp}]
                      </span>
                    </div>
                    <div>{log.message}</div>
                  </div>
                ))
              )}
              {isOptimizing && (
                <div className="text-center py-2">
                  <div className="inline-flex items-center gap-2 text-blue-600">
                    <div className="w-4 h-4 border-2 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
                    <span className="text-sm">Processing...</span>
                  </div>
                </div>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Instructions */}
        {selectedLocations.length === 0 && (
          <Card className="shadow-sm border-blue-200">
            <CardContent className="pt-4">
              <div className="text-center space-y-2">
                <div className="text-sm font-medium text-blue-800">
                  🚀 Getting Started
                </div>
                <div className="text-xs text-blue-600 space-y-1">
                  <div>1. Click on the map to add delivery locations</div>
                  <div>2. Configure your vehicle settings</div>
                  <div>3. Click "AI Optimize Route" to find the best path</div>
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {selectedLocations.length > 0 && selectedLocations.length < 2 && (
          <Card className="shadow-sm border-yellow-200">
            <CardContent className="pt-4">
              <div className="text-center space-y-2">
                <div className="text-sm font-medium text-yellow-800">
                  📍 Add More Locations
                </div>
                <div className="text-xs text-yellow-600">
                  You need at least 2 locations to optimize a route.
                  Click on the map to add more delivery stops.
                </div>
              </div>
            </CardContent>
          </Card>
        )}

      </div>
    </div>
  )
}
