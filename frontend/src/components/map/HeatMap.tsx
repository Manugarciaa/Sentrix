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
  breedingSiteType?: string | null
  location?: string
  timestamp?: string
}

interface HeatMapProps {
  data: HeatMapData[]
  center?: [number, number]
  zoom?: number
  className?: string
  visualizationMode?: 'risk-level' | 'breeding-type'
}

// Define color gradients for each breeding site type
const breedingSiteGradients: Record<string, Record<number, string>> = {
  'Basura': {
    // Brown/orange tones for garbage
    0.0: '#8B4513',  // SaddleBrown
    0.3: '#A0522D',  // Sienna
    0.5: '#CD853F',  // Peru
    0.7: '#D2691E',  // Chocolate
    1.0: '#FF6347'   // Tomato (reddish-orange)
  },
  'Charcos/Cumulo de agua': {
    // Blue/cyan tones for water accumulation
    0.0: '#00CED1',  // DarkTurquoise
    0.3: '#1E90FF',  // DodgerBlue
    0.5: '#4169E1',  // RoyalBlue
    0.7: '#0000CD',  // MediumBlue
    1.0: '#00008B'   // DarkBlue
  },
  'Huecos': {
    // Purple/magenta tones for holes
    0.0: '#9370DB',  // MediumPurple
    0.3: '#8B008B',  // DarkMagenta
    0.5: '#9932CC',  // DarkOrchid
    0.7: '#8A2BE2',  // BlueViolet
    1.0: '#4B0082'   // Indigo
  },
  'Calles mal hechas': {
    // Gray/silver tones for bad roads
    0.0: '#A9A9A9',  // DarkGray
    0.3: '#808080',  // Gray
    0.5: '#696969',  // DimGray
    0.7: '#505050',  // Darker gray
    1.0: '#2F4F4F'   // DarkSlateGray
  },
  // Default gradient for points without breeding site type
  'default': {
    0.0: '#00ff00',  // Green for low risk
    0.3: '#ffff00',  // Yellow
    0.5: '#ff8000',  // Orange
    0.7: '#ff4000',  // Red-orange
    1.0: '#ff0000'   // Red for very high risk
  }
}

// Component to handle heat layers (multiple layers, one per breeding site type)
const HeatLayer: React.FC<{ data: HeatMapData[]; visualizationMode: 'risk-level' | 'breeding-type' }> = ({ data, visualizationMode }) => {
  const map = useMap()

  useEffect(() => {
    if (!data || !Array.isArray(data) || data.length === 0) {
      return
    }

    if (!isHeatLayerAvailable()) {
      console.error('L.heatLayer is not available. Make sure leaflet.heat is loaded.')
      return
    }

    const heatLayers: L.Layer[] = []

    if (visualizationMode === 'risk-level') {
      // Risk-level mode: Single layer with default gradient (green-yellow-red)
      const heatData = data.map(point => [
        point.latitude,
        point.longitude,
        point.intensity
      ])

      const heatLayer = L.heatLayer(heatData, {
        radius: 30,
        blur: 18,
        maxZoom: 17,
        gradient: breedingSiteGradients['default'],
        minOpacity: 0.4,
        max: 1.0
      })

      heatLayer.addTo(map)
      heatLayers.push(heatLayer)
    } else {
      // Breeding-type mode: Multiple layers, one per breeding site type
      const dataByType: Record<string, HeatMapData[]> = {}

      data.forEach(point => {
        const type = point.breedingSiteType || 'default'
        if (!dataByType[type]) {
          dataByType[type] = []
        }
        dataByType[type].push(point)
      })

      Object.entries(dataByType).forEach(([type, points]) => {
        // Convert data to heat layer format [lat, lng, intensity]
        const heatData = points.map(point => [
          point.latitude,
          point.longitude,
          point.intensity
        ])

        const gradient = breedingSiteGradients[type] || breedingSiteGradients['default']

        // Create heat layer with type-specific gradient
        const heatLayer = L.heatLayer(heatData, {
          radius: 30,
          blur: 18,
          maxZoom: 17,
          gradient: gradient,
          minOpacity: 0.4,
          max: 1.0
        })

        heatLayer.addTo(map)
        heatLayers.push(heatLayer)
      })
    }

    return () => {
      heatLayers.forEach(layer => map.removeLayer(layer))
    }
  }, [map, data, visualizationMode])

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
            ${point.breedingSiteType ? `<p class="text-sm text-gray-600">Tipo: <span class="font-medium">${point.breedingSiteType}</span></p>` : ''}
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
  className = "h-96 w-full",
  visualizationMode = 'breeding-type'
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
          <HeatLayer data={data} visualizationMode={visualizationMode} />
          <RiskMarkers data={data} showMarkers={showMarkers} />
        </MapContainer>
      </div>
    </div>
  )
}

export default HeatMap