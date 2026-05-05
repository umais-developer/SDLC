import type { HeatMapGrid } from '../types';

interface HeatMapProps {
  grid: HeatMapGrid;
  totalToday: number;
  error: boolean;
}

const INTENSITY_COLORS = [
  'var(--heatmap-0)',
  'var(--heatmap-1)',
  'var(--heatmap-2)',
  'var(--heatmap-3)',
  'var(--heatmap-4)',
];

function getIntensity(count: number): number {
  if (count === 0) return 0;
  if (count === 1) return 1;
  if (count <= 3) return 2;
  if (count <= 6) return 3;
  return 4;
}

const DAY_LABELS = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];

export function HeatMap({ grid, totalToday, error }: HeatMapProps) {
  const hasAnySession = grid.some((row) => row.some((cell) => cell.count > 0));

  return (
    <section className="heatmap-section" aria-label="Productivity heat map">
      <div className="heatmap-header">
        <h2 className="section-title">Your Productivity</h2>
        <span className="sessions-today-badge" aria-label={`${totalToday} sessions today`}>
          {totalToday} today
        </span>
      </div>

      {error && (
        <p className="error-message" role="alert">
          Unable to load history. Data will still be saved for this session.
        </p>
      )}

      <div className="heatmap-wrapper">
        {/* Day-of-week labels on the left */}
        <div className="heatmap-day-labels" aria-hidden="true">
          {DAY_LABELS.map((d) => (
            <span key={d} className="heatmap-day-label">
              {d}
            </span>
          ))}
        </div>

        {/* Grid */}
        <div
          className="heatmap-grid"
          role="grid"
          aria-label="12-week session history"
        >
          {grid[0]?.map((_, colIdx) => (
            <div key={colIdx} className="heatmap-col" role="row">
              {grid.map((row, rowIdx) => {
                const cell = row[colIdx];
                if (!cell) return null;
                const intensity = getIntensity(cell.count);
                return (
                  <div
                    key={rowIdx}
                    role="gridcell"
                    className={`heatmap-cell ${cell.isToday ? 'heatmap-cell--today' : ''}`}
                    style={{ backgroundColor: INTENSITY_COLORS[intensity] }}
                    aria-label={cell.label}
                    title={cell.label}
                    tabIndex={0}
                  />
                );
              })}
            </div>
          ))}
        </div>
      </div>

      {/* Legend */}
      <div className="heatmap-legend" aria-hidden="true">
        <span className="legend-label">Less</span>
        {INTENSITY_COLORS.map((color, i) => (
          <div
            key={i}
            className="heatmap-cell heatmap-cell--legend"
            style={{ backgroundColor: color }}
          />
        ))}
        <span className="legend-label">More</span>
      </div>

      {!hasAnySession && !error && (
        <p className="heatmap-empty" aria-live="polite">
          No sessions yet — start your first Pomodoro!
        </p>
      )}
    </section>
  );
}
