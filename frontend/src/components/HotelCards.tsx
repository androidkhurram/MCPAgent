import type { HotelCard } from '../api/client'

interface HotelCardsProps {
  hotels: HotelCard[]
}

function formatReviews(count?: number | null): string | null {
  if (count == null || Number.isNaN(count)) return null
  return `${count.toLocaleString()} reviews`
}

export function HotelCards({ hotels }: HotelCardsProps) {
  if (!hotels.length) return null

  return (
    <section className="hotel-results" aria-label="Hotel recommendations">
      <h2>Suggested hotels ({hotels.length})</h2>
      <ul className="hotel-list">
        {hotels.map((hotel) => {
          const reviews = formatReviews(hotel.review_count)
          return (
            <li key={`${hotel.name}-${hotel.link}`} className="hotel-card">
              <div className="hotel-card-header">
                <h3>{hotel.name}</h3>
                {hotel.price_hint ? (
                  <span className="price-hint">{hotel.price_hint}</span>
                ) : (
                  <span className="price-hint muted">Price not listed</span>
                )}
              </div>
              <div className="hotel-meta">
                {hotel.rating ? (
                  <span className="rating">{hotel.rating}</span>
                ) : (
                  <span className="rating muted">Rating n/a</span>
                )}
                {reviews ? <span className="reviews">{reviews}</span> : null}
              </div>
              {hotel.address ? <p className="address">{hotel.address}</p> : null}
              {hotel.why ? <p className="why">{hotel.why}</p> : null}
              {hotel.snippet ? <p className="snippet">{hotel.snippet}</p> : null}
              {hotel.link ? (
                <a href={hotel.link} target="_blank" rel="noreferrer">
                  View source
                </a>
              ) : null}
            </li>
          )
        })}
      </ul>
    </section>
  )
}
