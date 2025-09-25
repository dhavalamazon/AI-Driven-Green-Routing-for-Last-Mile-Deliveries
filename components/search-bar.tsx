"use client"

import { useState } from "react"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { ArrowUpDown, MapPin } from "lucide-react"

export function SearchBar() {
  const [origin, setOrigin] = useState("")
  const [destination, setDestination] = useState("")

  const handleSwap = () => {
    setOrigin(destination)
    setDestination(origin)
  }

  return (
    <div className="flex flex-col gap-2 p-4 bg-white rounded-lg shadow-md">
      <div className="relative">
        <MapPin className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
        <Input
          placeholder="Origin"
          value={origin}
          onChange={(e) => setOrigin(e.target.value)}
          className="pl-9 pr-4 py-2 rounded-md border border-input focus:ring-primary focus:border-primary"
        />
      </div>
      <div className="flex justify-center">
        <Button
          variant="ghost"
          size="icon"
          onClick={handleSwap}
          className="text-muted-foreground hover:bg-accent hover:text-accent-foreground"
        >
          <ArrowUpDown className="h-4 w-4" />
        </Button>
      </div>
      <div className="relative">
        <MapPin className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
        <Input
          placeholder="Destination"
          value={destination}
          onChange={(e) => setDestination(e.target.value)}
          className="pl-9 pr-4 py-2 rounded-md border border-input focus:ring-primary focus:border-primary"
        />
      </div>
    </div>
  )
}
