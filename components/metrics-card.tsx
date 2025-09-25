import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

interface MetricsCardProps {
  title: string
  fastest: string
  fuelEfficient: string
}

export function MetricsCard({ title, fastest, fuelEfficient }: MetricsCardProps) {
  return (
    <Card className="shadow-sm">
      <CardHeader className="pb-2">
        <CardTitle className="text-sm font-medium">{title}</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold">{fastest}</div>
        <p className="text-xs text-muted-foreground">
          Fuel-Efficient: <span className="text-primary">{fuelEfficient}</span>
        </p>
      </CardContent>
    </Card>
  )
}
