export function MapDisplay() {
  return (
    <div className="relative h-full w-full bg-gray-200 flex items-center justify-center text-gray-500">
      <p className="text-lg">Amazon Delivery Route Map</p>
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-full h-full">
        {/* Fastest Route: Red Dashed Line */}
        <svg className="absolute inset-0 w-full h-full" viewBox="0 0 100 100" preserveAspectRatio="none">
          <path d="M20 50 L35 30 L55 25 L75 35 L85 20 L90 40 L20 50" stroke="red" strokeDasharray="4" fill="none" strokeWidth="2" />
          {/* Delivery stops */}
          <circle cx="35" cy="30" r="2" fill="red" />
          <circle cx="55" cy="25" r="2" fill="red" />
          <circle cx="75" cy="35" r="2" fill="red" />
          <circle cx="85" cy="20" r="2" fill="red" />
          <circle cx="90" cy="40" r="2" fill="red" />
        </svg>
        {/* Low Carbon Route: Green Solid Line */}
        <svg className="absolute inset-0 w-full h-full" viewBox="0 0 100 100" preserveAspectRatio="none">
          <path d="M20 50 L30 60 L45 70 L60 75 L75 65 L85 55 L20 50" stroke="#16a34a" fill="none" strokeWidth="2" />
          {/* Delivery stops */}
          <circle cx="30" cy="60" r="2" fill="#16a34a" />
          <circle cx="45" cy="70" r="2" fill="#16a34a" />
          <circle cx="60" cy="75" r="2" fill="#16a34a" />
          <circle cx="75" cy="65" r="2" fill="#16a34a" />
          <circle cx="85" cy="55" r="2" fill="#16a34a" />
        </svg>
        {/* Depot marker */}
        <svg className="absolute inset-0 w-full h-full" viewBox="0 0 100 100" preserveAspectRatio="none">
          <rect x="17" y="47" width="6" height="6" fill="orange" stroke="white" strokeWidth="1" rx="1" />
        </svg>
      </div>
    </div>
  )
}
