import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

export function VehicleSelector() {
  return (
    <Card className="shadow-sm">
      <CardHeader className="pb-2">
        <CardTitle className="text-lg">Vehicle Type</CardTitle>
      </CardHeader>
      <CardContent>
        <Select defaultValue="car">
          <SelectTrigger className="w-full">
            <SelectValue placeholder="Select vehicle type" />
          </SelectTrigger>
          <SelectContent>
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
