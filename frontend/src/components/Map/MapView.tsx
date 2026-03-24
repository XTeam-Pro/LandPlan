import { useEffect, useRef, useState, useCallback } from 'react'
import { Land } from '@/types'
import '../../styles/MapView.css'

interface MapViewProps {
  lands: Land[]
  selectedLandId?: number
  onLandSelect: (id: number) => void
}

declare global {
  interface Window {
    ymaps?: any
  }
}

export default function MapView({ lands, selectedLandId, onLandSelect }: MapViewProps) {
  const mapRef = useRef<HTMLDivElement>(null)
  const mapInstanceRef = useRef<any>(null)
  const clustererRef = useRef<any>(null)
  const [mapLoaded, setMapLoaded] = useState(false)
  const [useCanvas, setUseCanvas] = useState(false)

  const createPlacemarks = useCallback(() => {
    const ymaps = window.ymaps
    if (!ymaps || !mapInstanceRef.current) return

    // Remove old clusterer
    if (clustererRef.current) {
      mapInstanceRef.current.geoObjects.remove(clustererRef.current)
    }

    const clusterer = new ymaps.Clusterer({
      preset: 'islands#invertedVioletClusterIcons',
      groupByCoordinates: false,
      clusterDisableClickZoom: false,
      clusterHideIconOnBalloonOpen: false,
      geoObjectHideIconOnBalloonOpen: false,
    })

    const placemarks = lands
      .filter((land) => land.latitude && land.longitude)
      .map((land) => {
        const isSelected = land.id === selectedLandId
        const placemark = new ymaps.Placemark(
          [land.latitude, land.longitude],
          {
            balloonContentHeader: land.title,
            balloonContentBody: `
              <div style="font-size:13px">
                <p>${land.address || ''}</p>
                ${land.price ? `<p><b>Цена:</b> ${land.price.toLocaleString()} ₽</p>` : ''}
                ${land.area ? `<p><b>Площадь:</b> ${land.area} м²</p>` : ''}
                ${land.deal_type ? `<p><b>Тип сделки:</b> ${{purchase:'Покупка',lease:'Аренда',rent:'Сдача в наём',auction:'Аукцион'}[land.deal_type] || land.deal_type}</p>` : ''}
              </div>
            `,
            hintContent: land.title,
          },
          {
            preset: isSelected
              ? 'islands#redDotIcon'
              : 'islands#violetDotIcon',
          }
        )

        placemark.events.add('click', () => {
          onLandSelect(land.id)
        })

        return placemark
      })

    clusterer.add(placemarks)
    mapInstanceRef.current.geoObjects.add(clusterer)
    clustererRef.current = clusterer

    // Fit bounds if there are placemarks
    if (placemarks.length > 0) {
      const bounds = clusterer.getBounds()
      if (bounds) {
        mapInstanceRef.current.setBounds(bounds, {
          checkZoomRange: true,
          zoomMargin: 40,
        })
      }
    }
  }, [lands, selectedLandId, onLandSelect])

  useEffect(() => {
    let timeoutId: NodeJS.Timeout

    const initMap = () => {
      if (!window.ymaps || !mapRef.current) return

      window.ymaps.ready(() => {
        if (mapInstanceRef.current) return // already initialized

        try {
          const map = new window.ymaps.Map(mapRef.current, {
            center: [55.751574, 37.573856], // Moscow default
            zoom: 5,
            controls: ['zoomControl', 'searchControl', 'typeSelector', 'fullscreenControl'],
          })

          mapInstanceRef.current = map
          setMapLoaded(true)
        } catch (error) {
          console.error('Failed to initialize Yandex Maps:', error)
          setUseCanvas(true)
          setMapLoaded(true)
        }
      })
    }

    const checkYmaps = setInterval(() => {
      if (window.ymaps) {
        clearInterval(checkYmaps)
        clearTimeout(timeoutId)
        initMap()
      }
    }, 100)

    // Fallback after 5 seconds
    timeoutId = setTimeout(() => {
      clearInterval(checkYmaps)
      if (!mapInstanceRef.current) {
        console.warn('Yandex Maps API did not load, using canvas fallback')
        setUseCanvas(true)
        setMapLoaded(true)
      }
    }, 5000)

    return () => {
      clearInterval(checkYmaps)
      clearTimeout(timeoutId)
      if (mapInstanceRef.current) {
        mapInstanceRef.current.destroy()
        mapInstanceRef.current = null
      }
    }
  }, [])

  // Update placemarks when lands or selection changes
  useEffect(() => {
    if (mapLoaded && !useCanvas && mapInstanceRef.current) {
      createPlacemarks()
    }
  }, [mapLoaded, useCanvas, createPlacemarks])

  if (useCanvas) {
    return (
      <div className="map-container">
        <CanvasMapFallback
          lands={lands}
          selectedLandId={selectedLandId}
          onLandSelect={onLandSelect}
        />
      </div>
    )
  }

  return (
    <div className="map-container">
      {!mapLoaded && (
        <div style={{
          position: 'absolute',
          top: '50%',
          left: '50%',
          transform: 'translate(-50%, -50%)',
          color: '#666',
          fontSize: '1rem',
        }}>
          Загрузка карты...
        </div>
      )}
      <div ref={mapRef} style={{ width: '100%', height: '100%' }} />
    </div>
  )
}

function CanvasMapFallback({
  lands,
  selectedLandId,
  onLandSelect,
}: {
  lands: Land[]
  selectedLandId?: number
  onLandSelect: (id: number) => void
}) {
  return (
    <div style={{ width: '100%', height: '100%', display: 'flex', flexDirection: 'column' }}>
      <div style={{
        padding: '1rem',
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        color: 'white',
        fontSize: '0.9rem'
      }}>
        Карта (упрощённый вид — Yandex Maps не загрузились)
      </div>
      <div style={{
        flex: 1,
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))',
        gap: '0.75rem',
        padding: '1rem',
        overflowY: 'auto',
        background: '#fafafa'
      }}>
        {lands.length > 0 ? (
          lands.map((land) => (
            <div
              key={land.id}
              onClick={() => onLandSelect(land.id)}
              style={{
                padding: '1rem',
                background: selectedLandId === land.id ? '#e8eaf6' : 'white',
                border: selectedLandId === land.id ? '2px solid #667eea' : '1px solid #e0e0e0',
                borderRadius: '6px',
                cursor: 'pointer',
                transition: 'all 0.2s',
                boxShadow: selectedLandId === land.id ? '0 4px 12px rgba(102, 126, 234, 0.2)' : 'none'
              }}
            >
              <h4 style={{ margin: '0 0 0.5rem 0', fontSize: '0.95rem', color: '#333' }}>
                {land.title}
              </h4>
              <p style={{ margin: '0.25rem 0', fontSize: '0.8rem', color: '#666' }}>
                {land.address}
              </p>
              {land.price && (
                <p style={{ margin: '0.25rem 0', fontSize: '0.8rem', color: '#667eea', fontWeight: 'bold' }}>
                  {land.price.toLocaleString()} ₽
                </p>
              )}
              {land.area && (
                <p style={{ margin: '0.25rem 0', fontSize: '0.8rem', color: '#666' }}>
                  {land.area} м²
                </p>
              )}
              <p style={{ margin: '0.25rem 0', fontSize: '0.75rem', color: '#888' }}>
                {land.deal_type || 'Н/Д'}
              </p>
            </div>
          ))
        ) : (
          <div style={{
            gridColumn: '1 / -1',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: '#999',
            minHeight: '200px'
          }}>
            Участки не найдены
          </div>
        )}
      </div>
    </div>
  )
}
