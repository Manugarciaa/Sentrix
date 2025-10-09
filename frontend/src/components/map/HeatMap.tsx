import React, { useEffect, useState } from 'react'
import { MapContainer, TileLayer, useMap } from 'react-leaflet'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import 'leaflet.heat'

// Extend the L namespace to include heatLayer
declare global {
  // eslint-disable-next-line @typescript-eslint/no-namespace
  namespace L {
    function heatLayer(latlngs: number[][], options?: Record<string, unknown>): Layer
  }
}

// Verificar si heatLayer está disponible
const isHeatLayerAvailable = () => {
  return typeof L !== 'undefined' && typeof L.heatLayer === 'function'
}

interface HeatMapData {
  latitude: number
  longitude: number
  intensity: number
  riskLevel: 'ALTO' | 'MEDIO' | 'BAJO'
  detectionCount: number
  location?: string
  timestamp?: string
}

interface HeatMapProps {
  data: HeatMapData[]
  center?: [number, number]
  zoom?: number
  className?: string
}

// Component to handle heat layer
const HeatLayer: React.FC<{ data: HeatMapData[] }> = ({ data }) => {
  const map = useMap()

  useEffect(() => {
    console.log('HeatLayer data:', data)
    console.log('Is heatLayer available:', isHeatLayerAvailable())
    
    if (!data || !Array.isArray(data) || data.length === 0) {
      console.log('No data available for heat layer')
      return
    }

    if (!isHeatLayerAvailable()) {
      console.error('L.heatLayer is not available. Make sure leaflet.heat is loaded.')
      return
    }

    // Convert data to heat layer format [lat, lng, intensity]
    const heatData = data.map(point => [
      point.latitude,
      point.longitude,
      point.intensity
    ])
    
    console.log('Heat data converted:', heatData)

    // Create heat layer with enhanced colors for B&W background
    const heatLayer = L.heatLayer(heatData, {
      radius: 30,
      blur: 18,
      maxZoom: 17,
      gradient: {
        0.0: '#00ff00',  // Verde brillante para bajo riesgo
        0.3: '#ffff00',  // Amarillo brillante
        0.5: '#ff8000',  // Naranja intenso
        0.7: '#ff4000',  // Rojo-naranja
        1.0: '#ff0000'   // Rojo intenso para muy alto riesgo
      },
      minOpacity: 0.4,
      max: 1.0
    })

    heatLayer.addTo(map)

    return () => {
      map.removeLayer(heatLayer)
    }
  }, [map, data])

  return null
}

// Component for risk markers
const RiskMarkers: React.FC<{ data: HeatMapData[]; showMarkers: boolean }> = ({
  data,
  showMarkers
}) => {
  const map = useMap()

  useEffect(() => {
    if (!showMarkers || !data || !Array.isArray(data)) return

    const markers: L.Marker[] = []

    data.forEach(point => {
      const color = point.riskLevel === 'ALTO' ? '#ef4444' :
                   point.riskLevel === 'MEDIO' ? '#f59e0b' : '#22c55e'

      const icon = L.divIcon({
        html: `<div style="
          background-color: ${color};
          width: 20px;
          height: 20px;
          border-radius: 50%;
          border: 2px solid white;
          box-shadow: 0 2px 4px rgba(0,0,0,0.3);
        "></div>`,
        iconSize: [20, 20],
        className: 'custom-div-icon'
      })

      const marker = L.marker([point.latitude, point.longitude], { icon })
        .bindPopup(`
          <div class="p-2">
            <h3 class="font-semibold">${point.location || 'Ubicación'}</h3>
            <p class="text-sm text-gray-600">Riesgo: <span class="font-medium" style="color: ${color}">${point.riskLevel}</span></p>
            <p class="text-sm text-gray-600">Detecciones: ${point.detectionCount}</p>
            <p class="text-sm text-gray-600">Intensidad: ${(point.intensity * 100).toFixed(1)}%</p>
            ${point.timestamp ? `<p class="text-xs text-gray-500">${new Date(point.timestamp).toLocaleDateString('es-PE')}</p>` : ''}
          </div>
        `)

      marker.addTo(map)
      markers.push(marker)
    })

    return () => {
      markers.forEach(marker => map.removeLayer(marker))
    }
  }, [map, data, showMarkers])

  return null
}

const HeatMap: React.FC<HeatMapProps> = ({
  data,
  center = [-26.8083, -65.2176], // Tucumán, Argentina
  zoom = 12,
  className = "h-96 w-full"
}) => {
  const [showMarkers] = useState(false)

  // Fix for default markers
  useEffect(() => {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    delete (L.Icon.Default.prototype as any)._getIconUrl
    L.Icon.Default.mergeOptions({
      iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
      iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
      shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
    })
  }, [])

  return (
    <div className={className}>
      <div className="h-full w-full rounded-lg border border-gray-200 overflow-hidden">
        <MapContainer
          center={center}
          zoom={zoom}
          className="h-full w-full"
          scrollWheelZoom={true}
        >
          {/* Standard OpenStreetMap */}
          <TileLayer
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          />
          <HeatLayer data={data} />
          <RiskMarkers data={data} showMarkers={showMarkers} />
        </MapContainer>
      </div>
    </div>
  )
}

export default HeatMap