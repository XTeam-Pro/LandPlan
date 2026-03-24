// Minimal type declarations for Yandex Maps JavaScript API v2.1
declare global {
  interface Window {
    ymaps: YMapsAPI
  }
}

interface YMapsAPI {
  ready(callback: (ymaps: YMapsAPI) => void): void
  Map: typeof YMap
  Placemark: typeof YPlacemark
  Clusterer: typeof YClusterer
  control: {
    ZoomControl: typeof ZoomControl
    SearchControl: typeof SearchControl
  }
  event: {
    add(obj: any, eventName: string, handler: (event: any) => void): void
    remove(obj: any, eventName: string, handler?: (event: any) => void): void
  }
}

interface YMap {
  new (container: HTMLElement | string, state: MapState, options?: MapOptions): IMap
}

interface IMap {
  getCenter(): [number, number]
  setCenter(center: [number, number], zoom?: number, options?: any): IMap
  getZoom(): number
  setZoom(zoom: number, options?: any): IMap
  geoObjects: any
  controls: any
  destroy(): void
  setType(type: string): void
  on(eventName: string, handler: (event: any) => void): void
  off(eventName: string, handler?: (event: any) => void): void
}

interface MapState {
  center?: [number, number]
  zoom?: number
  type?: string
}

interface MapOptions {
  avoidFractionalZoom?: boolean
  suppressMapOpenBlock?: boolean
  yandexMapDisablePoiInteractivity?: boolean
}

interface YPlacemark {
  new (geometry: [number, number], properties?: PlacemarkProperties, options?: PlacemarkOptions): IPlacemark
}

interface IPlacemark {
  getGeometry(): [number, number]
  setGeometry(geometry: [number, number]): IPlacemark
  properties: any
  options: any
  on(eventName: string, handler: (event: any) => void): void
  off(eventName: string, handler?: (event: any) => void): void
  getBounds(): any
  getMap(): IMap | null
}

interface PlacemarkProperties {
  balloonContent?: string
  balloonContentBody?: string
  balloonContentFooter?: string
  balloonContentHeader?: string
  clusterCaption?: string
  hintContent?: string
  iconContent?: string
  [key: string]: any
}

interface PlacemarkOptions {
  preset?: string
  iconColor?: string
  balloonAutoPan?: boolean
  draggable?: boolean
}

interface YClusterer {
  new (options?: ClustererOptions): IClusterer
}

interface IClusterer {
  add(object: IPlacemark | IPlacemark[]): IClusterer
  remove(object: IPlacemark | IPlacemark[]): IClusterer
  removeAll(): IClusterer
  getObjects(): IPlacemark[]
  getParent(): any
}

interface ClustererOptions {
  preset?: string
  iconColor?: string
  groupByCoordinates?: boolean
  clusterDisableClickZoom?: boolean
  clusterHideIconOnBalloonOpen?: boolean
  geoObjectHideIconOnBalloonOpen?: boolean
  zoomMargin?: number[]
}

interface ZoomControl {
  new (options?: any): any
}

interface SearchControl {
  new (options?: any): any
}

export {}
