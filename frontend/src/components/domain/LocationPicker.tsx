import React, { useState, useEffect, useCallback } from 'react'
import { createPortal } from 'react-dom'
import { MapContainer, TileLayer, Marker, useMapEvents, useMap } from 'react-leaflet'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import { MapPin, Search, X, Navigation } from 'lucide-react'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { config } from '@/lib/config'

// Crear un icono personalizado moderno
const createCustomIcon = () => {
  return L.divIcon({
    className: 'custom-marker-icon',
    html: `
      <div style="position: relative; width: 40px; height: 40px;">
        <svg width="40" height="40" viewBox="0 0 40 40" xmlns="http://www.w3.org/2000/svg">
          <!-- Sombra -->
          <ellipse cx="20" cy="37" rx="8" ry="3" fill="rgba(0,0,0,0.2)" />
          <!-- Pin principal -->
          <path d="M20 4 C13 4 8 9 8 16 C8 24 20 36 20 36 S32 24 32 16 C32 9 27 4 20 4 Z"
                fill="hsl(var(--primary))"
                stroke="white"
                stroke-width="2"/>
          <!-- Círculo interior -->
          <circle cx="20" cy="16" r="5" fill="white" />
          <!-- Punto central -->
          <circle cx="20" cy="16" r="2.5" fill="hsl(var(--primary))" />
        </svg>
      </div>
    `,
    iconSize: [40, 40],
    iconAnchor: [20, 36],
    popupAnchor: [0, -36],
  })
}

interface LocationPickerProps {
  onLocationSelect: (lat: number, lng: number) => void
  onClose: () => void
  initialLat?: number
  initialLng?: number
  className?: string
}

// Componente interno para manejar clicks en el mapa
const MapClickHandler: React.FC<{
  onLocationSelect: (lat: number, lng: number) => void
}> = ({ onLocationSelect }) => {
  useMapEvents({
    click: (e) => {
      onLocationSelect(e.latlng.lat, e.latlng.lng)
    },
  })
  return null
}

// Componente para centrar el mapa
const MapCenterController: React.FC<{ center: [number, number] }> = ({ center }) => {
  const map = useMap()

  useEffect(() => {
    map.setView(center, map.getZoom())
  }, [center, map])

  return null
}

const LocationPicker: React.FC<LocationPickerProps> = ({
  onLocationSelect,
  onClose,
  initialLat,
  initialLng,
  className = '',
}) => {
  const [selectedLat, setSelectedLat] = useState<number | null>(
    initialLat ?? config.ui.mapDefaultCenter[0]
  )
  const [selectedLng, setSelectedLng] = useState<number | null>(
    initialLng ?? config.ui.mapDefaultCenter[1]
  )
  const [manualLat, setManualLat] = useState(
    initialLat?.toFixed(6) ?? config.ui.mapDefaultCenter[0].toFixed(6)
  )
  const [manualLng, setManualLng] = useState(
    initialLng?.toFixed(6) ?? config.ui.mapDefaultCenter[1].toFixed(6)
  )
  const [isGettingLocation, setIsGettingLocation] = useState(false)
  const [mapKey, setMapKey] = useState(0)

  // Force map to re-render when opened
  useEffect(() => {
    setMapKey(prev => prev + 1)
  }, [])

  const handleMapClick = useCallback((lat: number, lng: number) => {
    setSelectedLat(lat)
    setSelectedLng(lng)
    setManualLat(lat.toFixed(6))
    setManualLng(lng.toFixed(6))
  }, [])

  const handleManualLatChange = (value: string) => {
    setManualLat(value)
    const parsed = parseFloat(value)
    if (!isNaN(parsed) && parsed >= -90 && parsed <= 90) {
      setSelectedLat(parsed)
    }
  }

  const handleManualLngChange = (value: string) => {
    setManualLng(value)
    const parsed = parseFloat(value)
    if (!isNaN(parsed) && parsed >= -180 && parsed <= 180) {
      setSelectedLng(parsed)
    }
  }

  const handleGetCurrentLocation = () => {
    if (!navigator.geolocation) {
      alert('Tu navegador no soporta geolocalización')
      return
    }

    setIsGettingLocation(true)
    navigator.geolocation.getCurrentPosition(
      (position) => {
        const lat = position.coords.latitude
        const lng = position.coords.longitude
        setSelectedLat(lat)
        setSelectedLng(lng)
        setManualLat(lat.toFixed(6))
        setManualLng(lng.toFixed(6))
        setIsGettingLocation(false)
      },
      (error) => {
        console.error('Error obteniendo ubicación:', error)
        alert('No se pudo obtener tu ubicación actual')
        setIsGettingLocation(false)
      },
      {
        enableHighAccuracy: true,
        timeout: 10000,
        maximumAge: 0,
      }
    )
  }

  const handleConfirm = () => {
    if (selectedLat !== null && selectedLng !== null) {
      onLocationSelect(selectedLat, selectedLng)
      onClose()
    }
  }

  const isValidSelection = selectedLat !== null && selectedLng !== null

  const pickerContent = (
    <div className={`fixed inset-0 z-[110] flex items-center justify-center bg-black/60 backdrop-blur-sm ${className}`}>
      <div className="bg-card border-2 border-border rounded-xl shadow-2xl w-full max-w-4xl h-[85vh] flex flex-col m-4 overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between p-5 border-b border-border">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-primary/10">
              <MapPin className="h-5 w-5 text-primary" />
            </div>
            <div>
              <h2 className="text-xl font-bold text-foreground">Seleccionar Ubicación</h2>
              <p className="text-sm text-muted-foreground">Haz click en el mapa o ingresa coordenadas</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-muted rounded-lg transition-colors"
          >
            <X className="h-5 w-5 text-muted-foreground" />
          </button>
        </div>

        {/* Controls */}
        <div className="p-5 border-b border-border bg-muted/20">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* Latitude */}
            <div>
              <label className="block text-sm font-medium text-foreground mb-2">
                Latitud
              </label>
              <Input
                type="text"
                value={manualLat}
                onChange={(e) => handleManualLatChange(e.target.value)}
                placeholder="-26.808300"
                className="font-mono"
              />
              <p className="text-xs text-muted-foreground mt-1">Entre -90 y 90</p>
            </div>

            {/* Longitude */}
            <div>
              <label className="block text-sm font-medium text-foreground mb-2">
                Longitud
              </label>
              <Input
                type="text"
                value={manualLng}
                onChange={(e) => handleManualLngChange(e.target.value)}
                placeholder="-65.217600"
                className="font-mono"
              />
              <p className="text-xs text-muted-foreground mt-1">Entre -180 y 180</p>
            </div>

            {/* Current Location Button */}
            <div className="flex items-end">
              <Button
                onClick={handleGetCurrentLocation}
                disabled={isGettingLocation}
                variant="outline"
                className="w-full"
              >
                <Navigation className={`h-4 w-4 mr-2 ${isGettingLocation ? 'animate-spin' : ''}`} />
                {isGettingLocation ? 'Obteniendo...' : 'Mi Ubicación'}
              </Button>
            </div>
          </div>

          {/* Selected coordinates display */}
          {isValidSelection && (
            <div className="mt-4 p-3 bg-status-info-light dark:bg-status-info-bg-light border border-status-info-border rounded-lg">
              <p className="text-sm text-status-info-text font-medium">
                <Search className="inline h-4 w-4 mr-1" />
                Ubicación seleccionada: {selectedLat.toFixed(6)}, {selectedLng.toFixed(6)}
              </p>
            </div>
          )}
        </div>

        {/* Map */}
        <div className="flex-1 w-full relative bg-muted overflow-hidden">
          <MapContainer
            key={mapKey}
            center={[selectedLat || config.ui.mapDefaultCenter[0], selectedLng || config.ui.mapDefaultCenter[1]]}
            zoom={13}
            style={{ height: '100%', width: '100%', minHeight: '400px' }}
            scrollWheelZoom={true}
            zoomControl={true}
          >
            <TileLayer
              url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
              attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
            />
            <MapClickHandler onLocationSelect={handleMapClick} />
            {selectedLat !== null && selectedLng !== null && (
              <>
                <Marker position={[selectedLat, selectedLng]} icon={createCustomIcon()} />
                <MapCenterController center={[selectedLat, selectedLng]} />
              </>
            )}
          </MapContainer>
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between p-5 border-t border-border bg-muted/20">
          <p className="text-sm text-muted-foreground">
            {isValidSelection
              ? 'Haz click en "Confirmar" para usar esta ubicación'
              : 'Selecciona una ubicación en el mapa o ingresa coordenadas'}
          </p>
          <div className="flex gap-3">
            <Button onClick={onClose} variant="outline">
              Cancelar
            </Button>
            <Button
              onClick={handleConfirm}
              disabled={!isValidSelection}
              className="bg-primary hover:bg-primary/90 text-white"
            >
              <MapPin className="h-4 w-4 mr-2" />
              Confirmar Ubicación
            </Button>
          </div>
        </div>
      </div>
    </div>
  )

  return createPortal(pickerContent, document.body)
}

export default LocationPicker
