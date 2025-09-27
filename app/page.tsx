import { SearchBar } from "@/components/search-bar"
import { DynamicMapDisplay } from "@/components/dynamic-map"
import { RouteComparisonPanel } from "@/components/route-comparison-panel"

export default function Home() {
  return (
    <div className="flex flex-col h-screen lg:flex-row">
      {/* Search Bar */}
      <div className="absolute top-4 left-4 right-4 z-[1001] lg:top-6 lg:left-6 lg:right-auto lg:w-1/3">
        <SearchBar />
      </div>

      {/* Map Display */}
      <div className="flex-1">
        <DynamicMapDisplay />
      </div>

      {/* Route Comparison Panel */}
      <div className="absolute bottom-0 left-0 right-0 z-[1001] lg:relative lg:w-1/3 lg:max-w-md lg:h-full lg:shadow-lg lg:rounded-l-lg bg-background">
        <RouteComparisonPanel />
      </div>
    </div>
  )
}
