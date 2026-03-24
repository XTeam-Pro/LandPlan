import { create } from 'zustand'
import { Land, LandDetail, LandsFilterRequest, RecommendationsResponse } from '@/types'
import { landsApi } from '@/api/lands'

interface LandsStore {
  lands: Land[]
  total: number
  filters: LandsFilterRequest
  selectedLand: LandDetail | null
  recommendations: RecommendationsResponse | null
  isLoading: boolean
  error: string | null

  setFilters: (filters: Partial<LandsFilterRequest>) => void
  fetchLands: () => Promise<void>
  selectLand: (id: number) => Promise<void>
  clearSelectedLand: () => void
}

export const useLandsStore = create<LandsStore>((set, get) => ({
  lands: [],
  total: 0,
  filters: {
    page: 1,
    limit: 20,
    bbox_radius_km: 10,
  },
  selectedLand: null,
  recommendations: null,
  isLoading: false,
  error: null,

  setFilters: (newFilters: Partial<LandsFilterRequest>) => {
    const current = get().filters
    set({
      filters: {
        ...current,
        ...newFilters,
        page: 1, // Reset to first page when filters change
      },
    })
    get().fetchLands()
  },

  fetchLands: async () => {
    set({ isLoading: true, error: null })
    try {
      const filters = get().filters
      const response = await landsApi.list(filters)
      set({
        lands: response.items,
        total: response.total,
        isLoading: false,
      })
    } catch (error: any) {
      const message = error.response?.data?.error || error.message || 'Ошибка загрузки участков'
      set({ error: message, isLoading: false })
    }
  },

  selectLand: async (id: number) => {
    set({ isLoading: true, error: null, recommendations: null })
    try {
      const landDetail = await landsApi.getById(id)
      set({ selectedLand: landDetail, isLoading: false })

      // Load recommendations separately — don't block land display
      try {
        const recommendations = await landsApi.getRecommendations(id)
        set({ recommendations })
      } catch {
        // Recommendations failed — land detail still shows
        console.warn('Failed to load recommendations for land', id)
      }
    } catch (error: any) {
      const message = error.response?.data?.error || error.message || 'Ошибка загрузки информации об участке'
      set({ error: message, isLoading: false })
    }
  },

  clearSelectedLand: () => {
    set({ selectedLand: null, recommendations: null })
  },
}))
