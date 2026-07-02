import Frame from './Frame.jsx'

export default function FloorMap({ floors = [], currentFloorIndex = 0 }) {
  return (
    <Frame label="Dungeon Map" className="floor-map">
      <ol className="floor-map__list">
        {floors.map((floor) => (
          <li key={floor.index} className={`floor-node floor-node--${floor.status}`}>
            <span className="floor-node__marker" />
            <span className="floor-node__label">
              <span className="floor-node__index">{String(floor.index + 1).padStart(2, '0')}</span>
              <span className="floor-node__name">{floor.name}</span>
            </span>
            {floor.index === currentFloorIndex && floor.status === 'current' && (
              <span className="status-pill status-pill--warn status-pill--live">
                <span className="status-dot" />
                here
              </span>
            )}
          </li>
        ))}
      </ol>
    </Frame>
  )
}
