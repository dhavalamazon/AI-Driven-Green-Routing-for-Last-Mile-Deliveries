"use client"

import { Bar, BarChart, XAxis, YAxis, CartesianGrid, Legend, ResponsiveContainer } from "recharts"
import { ChartContainer, ChartTooltip, ChartTooltipContent } from "@/components/ui/chart"

interface ChartData {
  name: string
  fuel: number
  time: number // in minutes
}

interface FuelTimeChartProps {
  data: ChartData[]
}

export function FuelTimeChart({ data }: FuelTimeChartProps) {
  return (
    <ChartContainer
      config={{
        fuel: {
          label: "Fuel Usage (L)",
          color: "hsl(var(--primary))",
        },
        time: {
          label: "Travel Time (min)",
          color: "hsl(var(--secondary))",
        },
      }}
      className="h-[200px] w-full"
    >
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="name" />
          <YAxis yAxisId="left" orientation="left" stroke="hsl(var(--primary))" />
          <YAxis yAxisId="right" orientation="right" stroke="hsl(var(--secondary))" />
          <ChartTooltip content={<ChartTooltipContent />} />
          <Legend />
          <Bar yAxisId="left" dataKey="fuel" fill="var(--color-fuel)" name="Fuel Usage (L)" />
          <Bar yAxisId="right" dataKey="time" fill="var(--color-time)" name="Travel Time (min)" />
        </BarChart>
      </ResponsiveContainer>
    </ChartContainer>
  )
}
