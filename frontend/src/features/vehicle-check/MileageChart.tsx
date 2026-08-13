import type { MotTest } from "../../types/vehicle";
import {
  formatMileage,
  sortMotTests,
} from "./utils";


interface MileageChartProps {
  motTests: MotTest[];
}


export default function MileageChart({
  motTests,
}: MileageChartProps) {
  const sorted = sortMotTests(motTests).reverse();

  const latestUnit = [...sorted]
    .reverse()
    .find(
      (test) =>
        test.odometer_value !== null &&
        test.odometer_unit,
    )
    ?.odometer_unit;

  const points = sorted.filter(
    (test) =>
      test.odometer_value !== null &&
      (
        !latestUnit ||
        test.odometer_unit === latestUnit
      ),
  );

  if (points.length < 2) {
    return (
      <section className="panel">
        <div className="section-heading">
          <div>
            <span className="eyebrow">
              Mileage
            </span>

            <h2>Mileage history</h2>
          </div>
        </div>

        <div className="empty-state">
          There is not enough recorded mileage
          data to draw a trend yet.
        </div>
      </section>
    );
  }

  const width = 760;
  const height = 260;

  const padding = {
    top: 24,
    right: 24,
    bottom: 45,
    left: 72,
  };

  const values = points.map(
    (test) => test.odometer_value as number,
  );

  const minimum = Math.min(...values);
  const maximum = Math.max(...values);

  const range = Math.max(
    maximum - minimum,
    1,
  );

  const chartWidth =
    width - padding.left - padding.right;

  const chartHeight =
    height - padding.top - padding.bottom;

  const getX = (index: number) =>
    padding.left +
    (
      index /
      Math.max(points.length - 1, 1)
    ) *
      chartWidth;

  const getY = (value: number) =>
    padding.top +
    (
      (maximum - value) /
      range
    ) *
      chartHeight;

  const linePoints = points
    .map(
      (test, index) =>
        `${getX(index)},${getY(
          test.odometer_value as number,
        )}`,
    )
    .join(" ");

  const firstDate =
    new Date(points[0].completed_at);

  const lastDate =
    new Date(
      points[points.length - 1].completed_at,
    );

  return (
    <section className="panel">
      <div className="section-heading">
        <div>
          <span className="eyebrow">
            Mileage
          </span>

          <h2>Mileage history</h2>
        </div>

        <span className="section-meta">
          {points.length} readings
        </span>
      </div>

      <div className="mileage-chart-wrapper">
        <svg
          className="mileage-chart"
          viewBox={`0 0 ${width} ${height}`}
          role="img"
          aria-label="Vehicle mileage over time"
        >
          <line
            className="chart-grid-line"
            x1={padding.left}
            y1={padding.top}
            x2={padding.left}
            y2={height - padding.bottom}
          />

          <line
            className="chart-grid-line"
            x1={padding.left}
            y1={height - padding.bottom}
            x2={width - padding.right}
            y2={height - padding.bottom}
          />

          <line
            className="chart-guide-line"
            x1={padding.left}
            y1={padding.top}
            x2={width - padding.right}
            y2={padding.top}
          />

          <polyline
            className="mileage-line"
            fill="none"
            points={linePoints}
          />

          {points.map((test, index) => (
            <circle
              key={`${test.mot_test_number}-${index}`}
              className="mileage-point"
              cx={getX(index)}
              cy={getY(
                test.odometer_value as number,
              )}
              r="4"
            />
          ))}

          <text
            className="chart-label"
            x={padding.left - 12}
            y={padding.top + 4}
            textAnchor="end"
          >
            {formatMileage(
              maximum,
              latestUnit ?? null,
            )}
          </text>

          <text
            className="chart-label"
            x={padding.left - 12}
            y={height - padding.bottom + 4}
            textAnchor="end"
          >
            {formatMileage(
              minimum,
              latestUnit ?? null,
            )}
          </text>

          <text
            className="chart-label"
            x={padding.left}
            y={height - 15}
            textAnchor="start"
          >
            {firstDate.getFullYear()}
          </text>

          <text
            className="chart-label"
            x={width - padding.right}
            y={height - 15}
            textAnchor="end"
          >
            {lastDate.getFullYear()}
          </text>
        </svg>
      </div>
    </section>
  );
}