"use client"

import { useState } from "react"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { Truck, Package, Plus, X } from "lucide-react"

export function SearchBar() {
  const [depot, setDepot] = useState("")
  const [deliveries, setDeliveries] = useState<string[]>([])

  const addDelivery = () => {
    setDeliveries([...deliveries, ""])
  }

  const removeDelivery = (index: number) => {
    setDeliveries(deliveries.filter((_, i) => i !== index))
  }

  const updateDelivery = (index: number, value: string) => {
    const updated = [...deliveries]
    updated[index] = value
    setDeliveries(updated)
  }

  return (
    <div className="flex flex-col gap-2 p-4 bg-white rounded-lg shadow-md">
      <h3 className="text-sm font-medium text-gray-700 mb-1">Amazon Delivery Route</h3>
      
      <div className="relative">
        <Truck className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-orange-500" />
        <Input
          placeholder="Delivery Station/Depot"
          value={depot}
          onChange={(e) => setDepot(e.target.value)}
          className="pl-9 pr-4 py-2 rounded-md border border-input focus:ring-primary focus:border-primary"
        />
      </div>
      
      {deliveries.map((delivery, index) => (
        <div key={index} className="relative flex gap-2">
          <div className="flex-1 relative">
            <Package className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-blue-500" />
            <Input
              placeholder={`Delivery ${index + 1}`}
              value={delivery}
              onChange={(e) => updateDelivery(index, e.target.value)}
              className="pl-9 pr-4 py-2 rounded-md border border-input focus:ring-primary focus:border-primary"
            />
          </div>
          <Button
            variant="ghost"
            size="icon"
            onClick={() => removeDelivery(index)}
            className="text-red-500 hover:bg-red-50"
          >
            <X className="h-4 w-4" />
          </Button>
        </div>
      ))}
      
      <div className="flex justify-center">
        <Button
          variant="ghost"
          size="sm"
          onClick={addDelivery}
          className="text-blue-500 hover:bg-blue-50 gap-1"
        >
          <Plus className="h-4 w-4" />
          Add Delivery
        </Button>
      </div>
    </div>
  )
}
