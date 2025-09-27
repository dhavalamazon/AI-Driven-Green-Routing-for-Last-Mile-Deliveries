"use client"

import { useDelivery } from "@/contexts/delivery-context"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Truck, Clock, Zap, MapPin, Settings, Play } from "lucide-react"

export function SearchBar() {
  const {
    vehicleType,
    setVehicleType,
    fuelType,
    setFuelType,
    deliveryTime,
    setDeliveryTime,
    selectedLocations,
    trafficConditions,
    optimizeRoute,
    isOptimizing
  } = useDelivery()

  const getTrafficColor = (traffic: string) => {
    switch (traffic) {
      case "Free flow": return "bg-green-500"
      case "Moderate": return "bg-yellow-500"
      case "Heavy": return "bg-red-500"
      default: return "bg-gray-500"
    }
  }

  const getTrafficIcon = (traffic: string) => {
    switch (traffic) {
      case "Free flow": return "🟢"
      case "Moderate": return "🟡"
      case "Heavy": return "🔴"
      default: return "⚪"
    }
  }

  return (
    <div className="flex flex-col gap-3 max-w-md">
      {/* Main Control Panel - Google Maps Style */}
      <Card className="shadow-lg border-0 bg-white/95 backdrop-blur-sm">
        <CardHeader className="pb-3">
          <CardTitle className="text-lg flex items-center gap-2 text-gray-800">
            <MapPin className="h-5 w-5 text-blue-600" />
            Amazon Delivery Route
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Location Status */}
          <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
              <span className="text-sm font-medium">Delivery Locations</span>
            </div>
            <Badge variant={selectedLocations.length >= 2 ? "default" : "secondary"}>
              {selectedLocations.length} selected
            </Badge>
          </div>

          {selectedLocations.length > 0 && (
            <div className="text-xs text-gray-600 px-3 py-2 bg-blue-50 rounded-lg">
              💡 Click map to add more locations, then optimize route
            </div>
          )}

          {/* Vehicle Configuration */}
          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-2">
              <label className="text-xs font-medium text-gray-700 flex items-center gap-1">
                <Truck className="h-3 w-3" />
                Vehicle
              </label>
              <Select value={vehicleType} onValueChange={setVehicleType}>
                <SelectTrigger className="h-9 text-sm">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="Car">🚗 Car</SelectItem>
                  <SelectItem value="Truck">🚛 Truck</SelectItem>
                  <SelectItem value="Bus">🚌 Bus</SelectItem>
                  <SelectItem value="Motorcycle">🏍️ Motorcycle</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <label className="text-xs font-medium text-gray-700 flex items-center gap-1">
                <Zap className="h-3 w-3" />
                Fuel Type
              </label>
              <Select value={fuelType} onValueChange={setFuelType}>
                <SelectTrigger className="h-9 text-sm">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="Electric">⚡ Electric</SelectItem>
                  <SelectItem value="Hybrid">🔋 Hybrid</SelectItem>
                  <SelectItem value="Petrol">⛽ Petrol</SelectItem>
                  <SelectItem value="Diesel">🛢️ Diesel</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          {/* Delivery Time & Traffic */}
          <div className="space-y-2">
            <label className="text-xs font-medium text-gray-700 flex items-center gap-1">
              <Clock className="h-3 w-3" />
              Delivery Time
            </label>
            <div className="flex gap-2">
              <Input
                type="time"
                value={deliveryTime}
                onChange={(e) => setDeliveryTime(e.target.value)}
                className="h-9 text-sm flex-1"
              />
              <Badge 
                className={`${getTrafficColor(trafficConditions)} text-white px-2 py-1 text-xs font-medium`}
              >
                {getTrafficIcon(trafficConditions)} {trafficConditions}
              </Badge>
            </div>
            {selectedLocations.length > 0 && (
              <div className="text-xs text-gray-600">
                🌆 Traffic adapted to your delivery area
              </div>
            )}
          </div>

          {/* Optimize Button */}
          <Button 
            onClick={optimizeRoute}
            disabled={selectedLocations.length < 2 || isOptimizing}
            className="w-full bg-green-600 hover:bg-green-700 text-white h-10 font-medium shadow-md"
          >
            {isOptimizing ? (
              <div className="flex items-center gap-2">
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                Optimizing...
              </div>
            ) : (
              <div className="flex items-center gap-2">
                <Play className="h-4 w-4" />
                AI Optimize Route ({selectedLocations.length})
              </div>
            )}
          </Button>

          {selectedLocations.length < 2 && (
            <div className="text-xs text-gray-500 text-center">
              Select at least 2 locations on the map to optimize
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
