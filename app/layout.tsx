import type React from "react"
import type { Metadata } from "next"
import { GeistSans } from "geist/font/sans"
import { GeistMono } from "geist/font/mono"
import "./globals.css"
import { DeliveryProvider } from "@/contexts/delivery-context"

export const metadata: Metadata = {
  title: "AI Green Routing - Amazon Delivery",
  description: "AI-powered delivery route optimization for minimal CO₂ emissions",
  generator: "v0.app",
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="en" className={`${GeistSans.variable} ${GeistMono.variable} antialiased`}>
      <body className="font-sans">
        <DeliveryProvider>
          {children}
        </DeliveryProvider>
      </body>
    </html>
  )
}
