"use client"

import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { VehicleSelector } from "@/components/vehicle-selector"
import { MetricsCard } from "@/components/metrics-card"
import { FuelTimeChart } from "@/components/fuel-time-chart"
import { ChevronDown, ChevronUp } from "lucide-react"

export function RouteComparisonPanel() {
  const [isPanelOpen, setIsPanelOpen] = useState(true)
  const [showFastestRoute, setShowFastestRoute] = useState(true)
  const [showFuelEfficientRoute, setShowFuelEfficientRoute] = useState(true)

  const togglePanel = () => setIsPanelOpen(!isPanelOpen)

  // Dummy data for demonstration
  const metrics = {
    fastest: { time: "2h 15m", fuel: 12.8, co2: 29.8, deliveries: 8 },
    lowCarbon: { time: "2h 35m", fuel: 9.4, co2: 21.9, deliveries: 8 },
    carbonSaved: "27%",
  }

  const chartData = [
    { name: "Fastest", fuel: metrics.fastest.fuel, time: 135, co2: metrics.fastest.co2 },
    { name: "Low Carbon", fuel: metrics.lowCarbon.fuel, time: 155, co2: metrics.lowCarbon.co2 },
  ]

  return (
    <div className="bg-white rounded-t-lg shadow-lg lg:rounded-l-lg lg:rounded-t-none h-full flex flex-col">
      <div className="flex justify-between items-center p-4 border-b lg:hidden">
        <h2 className="text-lg font-semibold">Route Details</h2>
        <Button variant="ghost" size="icon" onClick={togglePanel}>
          {isPanelOpen ? <ChevronDown className="h-5 w-5" /> : <ChevronUp className="h-5 w-5" />}
        </Button>
      </div>

      <div className={`flex-1 overflow-y-auto overflow-x-visible p-4 space-y-4 ${isPanelOpen ? "block" : "hidden"} lg:block`}>
        <VehicleSelector />

        <div className="grid grid-cols-2 gap-4">
          <MetricsCard title="Delivery Time" fastest={metrics.fastest.time} fuelEfficient={metrics.lowCarbon.time} />
          <MetricsCard
            title="Fuel Used"
            fastest={`${metrics.fastest.fuel} L`}
            fuelEfficient={`${metrics.lowCarbon.fuel} L`}
          />
          <MetricsCard
            title="CO₂ Emissions"
            fastest={`${metrics.fastest.co2} kg`}
            fuelEfficient={`${metrics.lowCarbon.co2} kg`}
          />
          <MetricsCard
            title="Deliveries"
            fastest={`${metrics.fastest.deliveries}`}
            fuelEfficient={`${metrics.lowCarbon.deliveries}`}
          />
          <Card className="col-span-2 bg-green-600 text-white shadow-sm">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium">Carbon Footprint Reduced</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{metrics.carbonSaved}</div>
            </CardContent>
          </Card>
        </div>

        <Card className="shadow-sm">
          <CardHeader>
            <CardTitle className="text-lg">Route Visibility</CardTitle>
          </CardHeader>
          <CardContent className="flex flex-col gap-2">
            <div className="flex items-center justify-between">
              <span>Fastest Route (Red)</span>
              <Button
                variant={showFastestRoute ? "default" : "outline"}
                onClick={() => setShowFastestRoute(!showFastestRoute)}
                className={showFastestRoute ? "bg-red-500 hover:bg-red-600 text-white" : ""}
              >
                {showFastestRoute ? "Hide" : "Show"}
              </Button>
            </div>
            <div className="flex items-center justify-between">
              <span>Low Carbon Route (Green)</span>
              <Button
                variant={showFuelEfficientRoute ? "default" : "outline"}
                onClick={() => setShowFuelEfficientRoute(!showFuelEfficientRoute)}
                className={showFuelEfficientRoute ? "bg-green-600 hover:bg-green-700 text-white" : ""}
              >
                {showFuelEfficientRoute ? "Hide" : "Show"}
              </Button>
            </div>
          </CardContent>
        </Card>

        <Card className="shadow-sm">
          <CardHeader>
            <CardTitle className="text-lg">Comparison Chart</CardTitle>
          </CardHeader>
          <CardContent>
            <FuelTimeChart data={chartData} />
          </CardContent>
        </Card>

        <Button className="w-full bg-green-600 hover:bg-green-700 text-white py-2 rounded-md shadow-sm">
          Optimize Delivery Route
        </Button>
      </div>
    </div>
  )
}
