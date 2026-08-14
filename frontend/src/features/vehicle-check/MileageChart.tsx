"use client";

import { useState } from "react";

import type { MotTest } from "../../types/vehicle";

import {
  formatDate,
  formatMileage,
  sortMotTests,
} from "./utils";


interface MileageChartProps {
  motTests: MotTest[];
}


interface ChartPoint {
  test: MotTest;
  mileage: number;
}


export default function MileageChart({
  motTests,
}: MileageChartProps) {
  const [hoveredIndex, setHoveredIndex] =
    useState<number | null>(null);

  // Work from the oldest MOT to the newest so the graph reads left to right.
  const sortedTests = sortMotTests(
    motTests,
  ).reverse();

  const latestUnit = [...sortedTests]
    .reverse()
    .find(
      (test) =>
        test.odometer_value !== null &&
        test.odometer_unit,
    )
    ?.odometer_unit;

  const mileageTests = sortedTests.filter(
    (test) =>
      test.odometer_value !== null &&
      (
        !latestUnit ||
        test.odometer_unit === latestUnit
      ),
  );

  /*
   * Failed MOTs are often followed by a pass with exactly the same
   * mileage. Keep just the later test in that situation so we don't
   * draw several points on top of each other.
   */
  const points = mileageTests.reduce<
    ChartPoint[]
  >(
    (result, test) => {
      const mileage =
        test.odometer_value as number;

      const previousPoint =
        result[result.length - 1];

      if (
        previousPoint &&
        previousPoint.mileage === mileage
      ) {
        result[result.length - 1] = {
          test,
          mileage,
        };

        return result;
      }

      result.push({
        test,
        mileage,
      });

      return result;
    },
    [],
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

  const width = 820;
  const height = 330;

  const padding = {
    top: 30,
    right: 32,
    bottom: 58,
    left: 88,
  };

  const chartWidth =
    width - padding.left - padding.right;

  const chartHeight =
    height - padding.top - padding.bottom;

  const values = points.map(
    (point) => point.mileage,
  );

  const actualMinimum = Math.min(
    ...values,
  );

  const actualMaximum = Math.max(
    ...values,
  );

  /*
   * Give the graph a little space above and below the actual readings.
   * Otherwise the highest and lowest points sit directly on the axes.
   */
  const rawRange = Math.max(
    actualMaximum - actualMinimum,
    1,
  );

  const buffer = rawRange * 0.08;

  const graphMinimum = Math.max(
    0,
    actualMinimum - buffer,
  );

  const graphMaximum =
    actualMaximum + buffer;

  const graphRange =
    graphMaximum - graphMinimum;

  const getX = (
    index: number,
  ) =>
    padding.left +
    (
      index /
      Math.max(
        points.length - 1,
        1,
      )
    ) *
      chartWidth;

  const getY = (
    value: number,
  ) =>
    padding.top +
    (
      (graphMaximum - value) /
      graphRange
    ) *
      chartHeight;

  const linePoints = points
    .map(
      (point, index) =>
        `${getX(index)},${getY(
          point.mileage,
        )}`,
    )
    .join(" ");

  /*
   * Five horizontal steps keep the mileage axis readable without
   * covering the graph in too many labels.
   */
  const yTickCount = 5;

  const yTicks = Array.from(
    {
      length: yTickCount,
    },
    (_, index) => {
      const ratio =
        index /
        (yTickCount - 1);

      return (
        graphMaximum -
        ratio * graphRange
      );
    },
  );

  /*
   * Only show a handful of year labels when a car has a very long
   * history, otherwise the bottom axis gets crowded.
   */
  const maximumXLabels = 6;

  const xLabelIndexes = Array.from(
    new Set(
      Array.from(
        {
          length: Math.min(
            maximumXLabels,
            points.length,
          ),
        },
        (_, index) =>
          Math.round(
            (
              index /
              Math.max(
                Math.min(
                  maximumXLabels,
                  points.length,
                ) - 1,
                1,
              )
            ) *
              (points.length - 1),
          ),
      ),
    ),
  );

  const hoveredPoint =
    hoveredIndex !== null
      ? points[hoveredIndex]
      : null;

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
          {points.length} mileage changes
        </span>
      </div>

      <div className="mileage-chart-wrapper">
        <svg
          className="mileage-chart"
          viewBox={`0 0 ${width} ${height}`}
          role="img"
          aria-label="Vehicle mileage over time"
        >
          {yTicks.map(
            (tick, index) => {
              const y = getY(tick);

              return (
                <g
                  key={`y-${index}`}
                >
                  <line
                    className="chart-horizontal-grid"
                    x1={padding.left}
                    y1={y}
                    x2={
                      width -
                      padding.right
                    }
                    y2={y}
                  />

                  <text
                    className="chart-axis-label"
                    x={
                      padding.left -
                      14
                    }
                    y={y + 4}
                    textAnchor="end"
                  >
                    {Math.round(
                      tick,
                    ).toLocaleString(
                      "en-GB",
                    )}
                  </text>
                </g>
              );
            },
          )}

          {xLabelIndexes.map(
            (pointIndex) => {
              const point =
                points[pointIndex];

              const x =
                getX(pointIndex);

              const year =
                new Date(
                  point.test.completed_at,
                ).getFullYear();

              return (
                <g
                  key={`x-${pointIndex}`}
                >
                  <line
                    className="chart-vertical-grid"
                    x1={x}
                    y1={padding.top}
                    x2={x}
                    y2={
                      height -
                      padding.bottom
                    }
                  />

                  <text
                    className="chart-axis-label"
                    x={x}
                    y={
                      height -
                      padding.bottom +
                      29
                    }
                    textAnchor="middle"
                  >
                    {year}
                  </text>
                </g>
              );
            },
          )}

          <line
            className="chart-axis"
            x1={padding.left}
            y1={padding.top}
            x2={padding.left}
            y2={
              height -
              padding.bottom
            }
          />

          <line
            className="chart-axis"
            x1={padding.left}
            y1={
              height -
              padding.bottom
            }
            x2={
              width -
              padding.right
            }
            y2={
              height -
              padding.bottom
            }
          />

          <text
            className="chart-axis-title"
            x={18}
            y={
              padding.top +
              chartHeight / 2
            }
            textAnchor="middle"
            transform={`rotate(-90 18 ${
              padding.top +
              chartHeight / 2
            })`}
          >
            Mileage
          </text>

          <polyline
            className="mileage-line"
            fill="none"
            points={linePoints}
          />

          {points.map(
            (point, index) => {
              const x =
                getX(index);

              const y =
                getY(
                  point.mileage,
                );

              const hovered =
                hoveredIndex ===
                index;

              return (
                <g
                  key={
                    point.test
                      .mot_test_number
                  }
                  className="mileage-point-group"
                  onMouseEnter={() =>
                    setHoveredIndex(
                      index,
                    )
                  }
                  onMouseLeave={() =>
                    setHoveredIndex(
                      null,
                    )
                  }
                  onFocus={() =>
                    setHoveredIndex(
                      index,
                    )
                  }
                  onBlur={() =>
                    setHoveredIndex(
                      null,
                    )
                  }
                  tabIndex={0}
                >
                  <circle
                    className={
                      hovered
                        ? "mileage-point hovered"
                        : "mileage-point"
                    }
                    cx={x}
                    cy={y}
                    r={
                      hovered
                        ? 6
                        : 4
                    }
                  />

                  {/* Give each point a larger invisible hit area. */}
                  <circle
                    className="mileage-hit-area"
                    cx={x}
                    cy={y}
                    r="12"
                  />
                </g>
              );
            },
          )}

          {hoveredPoint &&
            hoveredIndex !== null && (
              <MileageTooltip
                point={
                  hoveredPoint
                }
                x={getX(
                  hoveredIndex,
                )}
                y={getY(
                  hoveredPoint.mileage,
                )}
                chartWidth={width}
                chartHeight={height}
                unit={
                  latestUnit ??
                  null
                }
              />
            )}
        </svg>
      </div>

      <p className="chart-help">
        Hover over a point to see the exact
        recorded mileage and MOT details.
      </p>
    </section>
  );
}


interface MileageTooltipProps {
  point: ChartPoint;
  x: number;
  y: number;
  chartWidth: number;
  chartHeight: number;
  unit: string | null;
}


function MileageTooltip({
  point,
  x,
  y,
  chartWidth,
  unit,
}: MileageTooltipProps) {
  const tooltipWidth = 190;
  const tooltipHeight = 82;

  /*
   * Move the tooltip to the other side of the point when it would
   * otherwise run outside the graph.
   */
  const placeOnLeft =
    x + tooltipWidth + 18 >
    chartWidth;

  const tooltipX =
    placeOnLeft
      ? x -
        tooltipWidth -
        14
      : x + 14;

  const tooltipY = Math.max(
    8,
    y -
      tooltipHeight -
      12,
  );

  const result =
    point.test.test_result
      ?.toUpperCase() ??
    "UNKNOWN";

  return (
    <g
      className="chart-tooltip"
      pointerEvents="none"
    >
      <rect
        x={tooltipX}
        y={tooltipY}
        width={tooltipWidth}
        height={tooltipHeight}
        rx="9"
      />

      <text
        className="chart-tooltip-mileage"
        x={tooltipX + 13}
        y={tooltipY + 23}
      >
        {formatMileage(
          point.mileage,
          unit,
        )}
      </text>

      <text
        className="chart-tooltip-detail"
        x={tooltipX + 13}
        y={tooltipY + 44}
      >
        {formatDate(
          point.test.completed_at,
        )}
      </text>

      <text
        className={
          result === "PASSED"
            ? "chart-tooltip-result pass"
            : "chart-tooltip-result fail"
        }
        x={tooltipX + 13}
        y={tooltipY + 64}
      >
        MOT {result}
      </text>
    </g>
  );
}