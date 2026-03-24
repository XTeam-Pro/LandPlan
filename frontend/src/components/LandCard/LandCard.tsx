import { Land } from '@/types'
import '../../styles/LandCard.css'

interface LandCardProps {
  land: Land
  isSelected?: boolean
  onClick: (id: number) => void
}

const dealTypeRu: Record<string, string> = {
  purchase: 'Покупка',
  lease: 'Аренда',
  rent: 'Сдача в наём',
  auction: 'Аукцион',
}

const listingTypeLabel: Record<string, string> = {
  owner: 'от собственника',
  agency: 'от агентства',
}

export default function LandCard({ land, isSelected, onClick }: LandCardProps) {
  return (
    <div
      className={`land-card ${isSelected ? 'selected' : ''}`}
      onClick={() => onClick(land.id)}
    >
      {/* Photo thumbnail */}
      {land.photos && land.photos.length > 0 ? (
        <div className="land-card-photo">
          <img src={land.photos[0]} alt={land.title} />
        </div>
      ) : (
        <div className="land-card-photo land-card-photo-placeholder">
          <span>{land.has_building ? '🏠' : '🌿'}</span>
        </div>
      )}

      <div className="land-card-body">
        {/* Badges */}
        <div className="land-card-badges">
          {land.listing_type && listingTypeLabel[land.listing_type] && (
            <span className={`listing-badge listing-${land.listing_type}`}>
              {listingTypeLabel[land.listing_type]}
            </span>
          )}
          {land.deal_type && (
            <span className={`deal-type deal-${land.deal_type}`}>
              {dealTypeRu[land.deal_type] || land.deal_type}
            </span>
          )}
          {land.has_building && (
            <span className="building-badge">с домом</span>
          )}
        </div>

        {/* Cadastral number — first line */}
        {land.cadastral_number && (
          <p className="land-cadastral">Кад. № {land.cadastral_number}</p>
        )}

        <h4 className="land-card-title">{land.title}</h4>
        <p className="land-address">{land.address}</p>

        <div className="land-info-row">
          {land.price != null && (
            <div className="info-item">
              <span className="label">Цена</span>
              <span className="value">{land.price.toLocaleString()} ₽</span>
            </div>
          )}
          {land.area != null && (
            <div className="info-item">
              <span className="label">Площадь</span>
              <span className="value">{land.area.toLocaleString()} м²</span>
            </div>
          )}
        </div>

        <div className="land-footer">
          <small>
            {new Date(land.updated_at).toLocaleDateString('ru-RU')}
          </small>
        </div>
      </div>
    </div>
  )
}
