import React, { useEffect, useState } from 'react'
import { MapContainer, TileLayer, useMap } from 'react-leaflet'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import 'leaflet.heat'

// Extend the L namespace to include heatLayer
declare global {
  namespace L {
    function heatLayer(latlngs: number[][], options?: any): any
  }
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
    if (!data || data.length === 0) return

    // Convert data to heat layer format [lat, lng, intensity]
    const heatData = data.map(point => [
      point.latitude,
      point.longitude,
      point.intensity
    ])

    // Create heat layer with custom options
    const heatLayer = L.heatLayer(heatData, {
      radius: 25,
      blur: 15,
      maxZoom: 17,
      gradient: {
        0.0: '#00ff00',  // Verde para bajo riesgo
        0.4: '#ffff00',  // Amarillo para medio riesgo
        0.7: '#ff8000',  // Naranja para alto riesgo
        1.0: '#ff0000'   // Rojo para muy alto riesgo
      }
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
    if (!showMarkers || !data) return

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
  const [showMarkers, setShowMarkers] = useState(false)

  // Fix for default markers
  useEffect(() => {
    delete (L.Icon.Default.prototype as any)._getIconUrl
    L.Icon.Default.mergeOptions({
      iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
      iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
      shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
    })
  }, [])

  return (
    <div className={className}>
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-lg font-semibold text-gray-900">Mapa de Calor - Detecciones de Criaderos</h3>
          <p className="text-sm text-gray-600">
            Mostrando {data.length} ubicaciones con detecciones
          </p>
        </div>
        <div className="flex items-center space-x-4">
          <label className="flex items-center">
            <input
              type="checkbox"
              checked={showMarkers}
              onChange={(e) => setShowMarkers(e.target.checked)}
              className="mr-2"
            />
            <span className="text-sm">Mostrar marcadores</span>
          </label>
        </div>
      </div>

      {/* Map Legend */}
      <div className="mb-4 p-3 bg-white rounded-lg border border-gray-200">
        <h4 className="text-sm font-medium text-gray-900 mb-2">Leyenda</h4>
        <div className="flex flex-wrap gap-4 text-xs">
          <div className="flex items-center">
            <div className="w-4 h-4 bg-green-500 rounded mr-2"></div>
            <span>Bajo Riesgo</span>
          </div>
          <div className="flex items-center">
            <div className="w-4 h-4 bg-yellow-500 rounded mr-2"></div>
            <span>Medio Riesgo</span>
          </div>
          <div className="flex items-center">
            <div className="w-4 h-4 bg-orange-500 rounded mr-2"></div>
            <span>Alto Riesgo</span>
          </div>
          <div className="flex items-center">
            <div className="w-4 h-4 bg-red-500 rounded mr-2"></div>
            <span>Muy Alto Riesgo</span>
          </div>
        </div>
      </div>

      <MapContainer
        center={center}
        zoom={zoom}
        className="h-full w-full rounded-lg border border-gray-200"
        scrollWheelZoom={true}
      >
        <TileLayer
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        />
        <HeatLayer data={data} />
        <RiskMarkers data={data} showMarkers={showMarkers} />
      </MapContainer>
    </div>
  )
}

export default HeatMap