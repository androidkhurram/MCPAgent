import type { FlightCard } from '../api/client'

interface FlightCardsProps {
  flights: FlightCard[]
}

export function FlightCards({ flights }: FlightCardsProps) {
  if (!flights.length) return null

  return (
    <section className="hotel-results" aria-label="Flight recommendations">
      <h2>Suggested flights ({flights.length})</h2>
      <ul className="hotel-list">
        {flights.map((flight, index) => {
          const route =
            flight.from_airport && flight.to_airport
              ? `${flight.from_airport} → ${flight.to_airport}`
              : null
          const stopsLabel =
            flight.stops == null
              ? null
              : flight.stops === 0
                ? 'Nonstop'
                : `${flight.stops} stop${flight.stops === 1 ? '' : 's'}`

          return (
            <li
              key={`${flight.airline}-${flight.flight_numbers}-${index}`}
              className="hotel-card"
            >
              <div className="hotel-card-header">
                <h3>
                  {flight.airline}
                  {flight.flight_numbers ? (
                    <span className="flight-numbers"> · {flight.flight_numbers}</span>
                  ) : null}
                </h3>
                {flight.price ? (
                  <span className="price-hint">{flight.price}</span>
                ) : (
                  <span className="price-hint muted">Price n/a</span>
                )}
              </div>
              <div className="hotel-meta">
                {route ? <span className="rating">{route}</span> : null}
                {stopsLabel ? <span className="reviews">{stopsLabel}</span> : null}
                {flight.duration ? <span className="reviews">{flight.duration}</span> : null}
              </div>
              {(flight.departure_time || flight.arrival_time) && (
                <p className="address">
                  {[flight.departure_time, flight.arrival_time].filter(Boolean).join(' → ')}
                </p>
              )}
              {flight.why ? <p className="why">{flight.why}</p> : null}
              {flight.link ? (
                <a href={flight.link} target="_blank" rel="noreferrer">
                  Open Google Flights
                </a>
              ) : null}
            </li>
          )
        })}
      </ul>
    </section>
  )
}
