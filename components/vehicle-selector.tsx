"use client"

import { useState } from "react"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

export function VehicleSelector() {
  const [selectedVehicle, setSelectedVehicle] = useState("car")

  const handleVehicleChange = (value: string) => {
    setSelectedVehicle(value)
    // You can add additional logic here, like updating global state or calling an API
  }

  return (
    <Card className="shadow-sm">
      <CardHeader className="pb-2">
        <CardTitle className="text-lg">Vehicle Type</CardTitle>
      </CardHeader>
      <CardContent>
        <Select value={selectedVehicle} onValueChange={handleVehicleChange}>
          <SelectTrigger className="w-full">
            <SelectValue placeholder="Select vehicle type" />
          </SelectTrigger>
          <SelectContent className="z-[9999]">
            <SelectItem value="car">Car</SelectItem>
            <SelectItem value="suv">SUV</SelectItem>
            <SelectItem value="truck">Truck</SelectItem>
            <SelectItem value="ev">EV</SelectItem>
          </SelectContent>
        </Select>
      </CardContent>
    </Card>
  )
}
