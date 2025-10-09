import React, { useState, useEffect } from 'react'
import { Settings as SettingsIcon, Save, RotateCcw, Bell, Image, Lock } from 'lucide-react'
import { Card } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/Tabs'
import { Select } from '@/components/ui/Select'
import { Checkbox } from '@/components/ui/Checkbox'
import { Slider } from '@/components/ui/Slider'
import LoadingSpinner from '@/components/ui/LoadingSpinner'
import { config } from '@/lib/config'

interface AppSettings {
  // General
  language: string
  timezone: string
  date_format: string

  // Notifications
  email_notifications: boolean
  email_new_analysis: boolean
  email_validation_complete: boolean
  email_reports: boolean
  in_app_notifications: boolean

  // Analysis Defaults
  default_confidence_threshold: number
  default_include_gps: boolean
  auto_validate_high_confidence: boolean

  // Privacy
  profile_visibility: 'public' | 'private'
  share_analytics: boolean
}

const defaultSettings: AppSettings = {
  language: 'es',
  timezone: 'America/Argentina/Buenos_Aires',
  date_format: 'DD/MM/YYYY',
  email_notifications: true,
  email_new_analysis: true,
  email_validation_complete: false,
  email_reports: true,
  in_app_notifications: true,
  default_confidence_threshold: 0.7,
  default_include_gps: true,
  auto_validate_high_confidence: false,
  profile_visibility: 'private',
  share_analytics: false,
}

const SettingsPage: React.FC = () => {
  const [settings, setSettings] = useState<AppSettings>(defaultSettings)
  const [isLoading, setIsLoading] = useState(true)
  const [isSaving, setIsSaving] = useState(false)
  const [hasChanges, setHasChanges] = useState(false)

  useEffect(() => {
    fetchSettings()
  }, [])

  const fetchSettings = async () => {
    try {
      setIsLoading(true)

      const token = localStorage.getItem('token')
      const response = await fetch(`${config.api.baseUrl}/api/v1/users/me/settings`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })

      if (response.ok) {
        const data = await response.json()
        setSettings({ ...defaultSettings, ...data })
      }
    } catch (error) {
      console.error('Error fetching settings:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const handleSaveSettings = async () => {
    try {
      setIsSaving(true)

      const token = localStorage.getItem('token')
      const response = await fetch(`${config.api.baseUrl}/api/v1/users/me/settings`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(settings),
      })

      if (response.ok) {
        setHasChanges(false)
        alert('Configuración guardada exitosamente')
      } else {
        throw new Error('Error al guardar')
      }
    } catch (error) {
      console.error('Error saving settings:', error)
      alert('Error al guardar la configuración')
    } finally {
      setIsSaving(false)
    }
  }

  const handleResetSettings = () => {
    if (confirm('¿Estás seguro de restablecer todas las configuraciones a sus valores predeterminados?')) {
      setSettings(defaultSettings)
      setHasChanges(true)
    }
  }

  const updateSetting = <K extends keyof AppSettings>(key: K, value: AppSettings[K]) => {
    setSettings({ ...settings, [key]: value })
    setHasChanges(true)
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="text-center">
          <LoadingSpinner size="lg" />
          <p className="mt-4 text-sm text-gray-600">Cargando configuración...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-4xl font-bold text-gray-900">Configuración</h1>
          <p className="text-base text-gray-700 mt-2">
            Personaliza tu experiencia en Sentrix
          </p>
        </div>

        <div className="flex items-center gap-3">
          <Button
            onClick={handleResetSettings}
            variant="outline"
            className="gap-2"
          >
            <RotateCcw className="h-4 w-4" />
            Restablecer
          </Button>
          <Button
            onClick={handleSaveSettings}
            disabled={!hasChanges || isSaving}
            className="gap-2 bg-gradient-to-r from-primary-600 to-cyan-600"
          >
            <Save className="h-4 w-4" />
            {isSaving ? 'Guardando...' : 'Guardar Cambios'}
          </Button>
        </div>
      </div>

      {/* Settings Tabs */}
      <Tabs defaultValue="general">
        <TabsList>
          <TabsTrigger value="general" className="gap-2">
            <SettingsIcon className="h-4 w-4" />
            General
          </TabsTrigger>
          <TabsTrigger value="notifications" className="gap-2">
            <Bell className="h-4 w-4" />
            Notificaciones
          </TabsTrigger>
          <TabsTrigger value="analysis" className="gap-2">
            <Image className="h-4 w-4" />
            Análisis
          </TabsTrigger>
          <TabsTrigger value="privacy" className="gap-2">
            <Lock className="h-4 w-4" />
            Privacidad
          </TabsTrigger>
        </TabsList>

        {/* General Tab */}
        <TabsContent value="general" className="mt-6">
          <Card className="p-6">
            <h2 className="text-lg font-bold text-gray-900 mb-4">Configuración General</h2>

            <div className="space-y-6">
              {/* Language */}
              <Select
                label="Idioma"
                options={[
                  { value: 'es', label: 'Español' },
                  { value: 'en', label: 'English' },
                  { value: 'pt', label: 'Português' },
                ]}
                value={settings.language}
                onChange={(value) => updateSetting('language', value)}
              />

              {/* Timezone */}
              <Select
                label="Zona Horaria"
                options={[
                  { value: 'America/Argentina/Buenos_Aires', label: 'Buenos Aires (GMT-3)' },
                  { value: 'America/Sao_Paulo', label: 'São Paulo (GMT-3)' },
                  { value: 'America/Santiago', label: 'Santiago (GMT-3)' },
                  { value: 'America/Lima', label: 'Lima (GMT-5)' },
                  { value: 'America/Mexico_City', label: 'Ciudad de México (GMT-6)' },
                ]}
                value={settings.timezone}
                onChange={(value) => updateSetting('timezone', value)}
              />

              {/* Date Format */}
              <Select
                label="Formato de Fecha"
                options={[
                  { value: 'DD/MM/YYYY', label: 'DD/MM/YYYY (25/12/2024)' },
                  { value: 'MM/DD/YYYY', label: 'MM/DD/YYYY (12/25/2024)' },
                  { value: 'YYYY-MM-DD', label: 'YYYY-MM-DD (2024-12-25)' },
                ]}
                value={settings.date_format}
                onChange={(value) => updateSetting('date_format', value)}
              />
            </div>
          </Card>
        </TabsContent>

        {/* Notifications Tab */}
        <TabsContent value="notifications" className="mt-6">
          <Card className="p-6">
            <h2 className="text-lg font-bold text-gray-900 mb-4">Preferencias de Notificaciones</h2>

            <div className="space-y-6">
              {/* Email Notifications */}
              <div>
                <h3 className="text-sm font-semibold text-gray-900 mb-3">
                  Notificaciones por Email
                </h3>
                <div className="space-y-3">
                  <Checkbox
                    label="Habilitar notificaciones por email"
                    description="Recibe actualizaciones importantes en tu correo"
                    checked={settings.email_notifications}
                    onChange={(checked) => updateSetting('email_notifications', checked)}
                  />

                  {settings.email_notifications && (
                    <div className="ml-6 space-y-3 pt-2">
                      <Checkbox
                        label="Nuevo análisis completado"
                        description="Te avisamos cuando un análisis termina de procesarse"
                        checked={settings.email_new_analysis}
                        onChange={(checked) => updateSetting('email_new_analysis', checked)}
                      />
                      <Checkbox
                        label="Validación completada"
                        description="Notificación cuando se valida una detección"
                        checked={settings.email_validation_complete}
                        onChange={(checked) => updateSetting('email_validation_complete', checked)}
                      />
                      <Checkbox
                        label="Reportes generados"
                        description="Te notificamos cuando un reporte está listo para descargar"
                        checked={settings.email_reports}
                        onChange={(checked) => updateSetting('email_reports', checked)}
                      />
                    </div>
                  )}
                </div>
              </div>

              {/* In-App Notifications */}
              <div className="pt-4 border-t border-gray-200">
                <h3 className="text-sm font-semibold text-gray-900 mb-3">
                  Notificaciones en la Aplicación
                </h3>
                <Checkbox
                  label="Habilitar notificaciones en la app"
                  description="Muestra notificaciones dentro de la plataforma"
                  checked={settings.in_app_notifications}
                  onChange={(checked) => updateSetting('in_app_notifications', checked)}
                />
              </div>
            </div>
          </Card>
        </TabsContent>

        {/* Analysis Tab */}
        <TabsContent value="analysis" className="mt-6">
          <Card className="p-6">
            <h2 className="text-lg font-bold text-gray-900 mb-4">Configuración de Análisis</h2>

            <div className="space-y-6">
              {/* Confidence Threshold */}
              <div>
                <Slider
                  label="Umbral de Confianza Predeterminado"
                  value={settings.default_confidence_threshold * 100}
                  onChange={(value) => updateSetting('default_confidence_threshold', value / 100)}
                  min={50}
                  max={95}
                  step={5}
                  showValue={true}
                  formatValue={(v) => `${v.toFixed(0)}%`}
                />
                <p className="text-xs text-gray-600 mt-2">
                  Este valor se usará por defecto al crear nuevos análisis
                </p>
              </div>

              {/* GPS Default */}
              <div className="pt-4">
                <Checkbox
                  label="Incluir datos GPS por defecto"
                  description="Extrae automáticamente las coordenadas de las imágenes"
                  checked={settings.default_include_gps}
                  onChange={(checked) => updateSetting('default_include_gps', checked)}
                />
              </div>

              {/* Auto Validate */}
              <div>
                <Checkbox
                  label="Validar automáticamente detecciones de alta confianza"
                  description="Marca como validadas las detecciones con más del 90% de confianza"
                  checked={settings.auto_validate_high_confidence}
                  onChange={(checked) => updateSetting('auto_validate_high_confidence', checked)}
                />
              </div>
            </div>
          </Card>
        </TabsContent>

        {/* Privacy Tab */}
        <TabsContent value="privacy" className="mt-6">
          <Card className="p-6">
            <h2 className="text-lg font-bold text-gray-900 mb-4">Configuración de Privacidad</h2>

            <div className="space-y-6">
              {/* Profile Visibility */}
              <div>
                <Select
                  label="Visibilidad del Perfil"
                  options={[
                    { value: 'public', label: 'Público - Visible para todos los usuarios' },
                    { value: 'private', label: 'Privado - Solo visible para ti' },
                  ]}
                  value={settings.profile_visibility}
                  onChange={(value) => updateSetting('profile_visibility', value as 'public' | 'private')}
                />
              </div>

              {/* Analytics Sharing */}
              <div className="pt-4">
                <Checkbox
                  label="Compartir datos analíticos"
                  description="Ayuda a mejorar el sistema compartiendo datos anónimos de uso"
                  checked={settings.share_analytics}
                  onChange={(checked) => updateSetting('share_analytics', checked)}
                />
              </div>

              {/* Privacy Notice */}
              <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
                <h4 className="text-sm font-semibold text-blue-900 mb-2">
                  Sobre tu Privacidad
                </h4>
                <p className="text-xs text-blue-800 leading-relaxed">
                  Sentrix toma en serio la privacidad de tus datos. Toda la información
                  es encriptada y almacenada de forma segura. Nunca compartimos tus datos
                  personales con terceros sin tu consentimiento explícito.
                </p>
              </div>
            </div>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Save Reminder */}
      {hasChanges && (
        <div className="fixed bottom-6 right-6 bg-white border-2 border-primary-500 rounded-lg shadow-lg p-4 max-w-sm">
          <div className="flex items-start gap-3">
            <div className="shrink-0 w-10 h-10 bg-primary-100 rounded-full flex items-center justify-center">
              <Save className="h-5 w-5 text-primary-600" />
            </div>
            <div className="flex-1">
              <p className="text-sm font-semibold text-gray-900 mb-1">
                Tienes cambios sin guardar
              </p>
              <p className="text-xs text-gray-600 mb-3">
                No olvides guardar tus cambios antes de salir
              </p>
              <div className="flex gap-2">
                <Button
                  onClick={() => setHasChanges(false)}
                  size="sm"
                  variant="outline"
                >
                  Descartar
                </Button>
                <Button
                  onClick={handleSaveSettings}
                  size="sm"
                  disabled={isSaving}
                  className="bg-primary-600"
                >
                  Guardar
                </Button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default SettingsPage
