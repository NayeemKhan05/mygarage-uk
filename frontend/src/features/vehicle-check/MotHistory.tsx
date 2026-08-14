"use client";

import { useState } from "react";

import type { MotTest } from "../../types/vehicle";

import {
  formatDate,
  formatMileage,
  getDefectTone,
  getMileageChange,
  sortMotTests,
} from "./utils";


interface MotHistoryProps {
  motTests: MotTest[];
}


const INITIAL_TEST_COUNT = 8;


export default function MotHistory({
  motTests,
}: MotHistoryProps) {
  const [showAll, setShowAll] =
    useState(false);

  const sortedTests =
    sortMotTests(motTests);

  const visibleTests = showAll
    ? sortedTests
    : sortedTests.slice(
        0,
        INITIAL_TEST_COUNT,
      );

  if (sortedTests.length === 0) {
    return (
      <section className="panel">
        <div className="section-heading">
          <div>
            <span className="eyebrow">
              History
            </span>

            <h2>MOT history</h2>
          </div>
        </div>

        <div className="empty-state">
          No MOT tests were returned for
          this vehicle.
        </div>
      </section>
    );
  }

  return (
    <section className="panel">
      <div className="section-heading">
        <div>
          <span className="eyebrow">
            History
          </span>

          <h2>MOT history</h2>
        </div>

        <span className="section-meta">
          {sortedTests.length} tests
        </span>
      </div>

      <div className="mot-list">
        {visibleTests.map(
          (test, index) => {
            const passed =
              test.test_result?.toUpperCase() ===
              "PASSED";

            // The list is newest first, so the next item is the MOT
            // that happened immediately before this one.
            const previousTest =
              sortedTests[index + 1];

            const mileageChange =
              getMileageChange(
                test,
                previousTest,
              );

            return (
              <details
                className="mot-card"
                key={test.mot_test_number}
                open={index === 0}
              >
                <summary className="mot-summary">
                  <div className="mot-date">
                    <strong>
                      {formatDate(
                        test.completed_at,
                      )}
                    </strong>

                    <span>
                      {formatMileage(
                        test.odometer_value,
                        test.odometer_unit,
                      )}
                    </span>

                    <span
                      className={`mileage-change ${mileageChange.tone}`}
                    >
                      {mileageChange.label}
                    </span>
                  </div>

                  <div className="mot-summary-right">
                    <span
                      className={
                        passed
                          ? "result-badge passed"
                          : "result-badge failed"
                      }
                    >
                      {passed
                        ? "Passed"
                        : test.test_result ??
                          "Unknown"}
                    </span>

                    <span className="defect-count">
                      {test.defects.length === 0
                        ? "No defects"
                        : `${test.defects.length} ${
                            test.defects.length ===
                            1
                              ? "item"
                              : "items"
                          }`}
                    </span>

                    <span
                      className="mot-chevron"
                      aria-hidden="true"
                    >
                      +
                    </span>
                  </div>
                </summary>

                <div className="mot-content">
                  <div className="mot-details-grid">
                    <div>
                      <span>
                        Expiry
                      </span>

                      <strong>
                        {formatDate(
                          test.expiry_date,
                        )}
                      </strong>
                    </div>

                    <div>
                      <span>
                        Test number
                      </span>

                      <strong>
                        {test.mot_test_number}
                      </strong>
                    </div>

                    <div>
                      <span>
                        Registration
                      </span>

                      <strong>
                        {test.registration_at_time_of_test ??
                          "Not recorded"}
                      </strong>
                    </div>
                  </div>

                  {test.defects.length === 0 ? (
                    <div className="clean-mot">
                      No defects or advisories
                      were recorded on this test.
                    </div>
                  ) : (
                    <div className="defects">
                      {test.defects.map(
                        (
                          defect,
                          defectIndex,
                        ) => (
                          <div
                            className={`defect ${getDefectTone(
                              defect,
                            )}`}
                            key={`${test.mot_test_number}-${defectIndex}`}
                          >
                            <span className="defect-type">
                              {defect.type}
                            </span>

                            <p>
                              {defect.text}
                            </p>
                          </div>
                        ),
                      )}
                    </div>
                  )}
                </div>
              </details>
            );
          },
        )}
      </div>

      {sortedTests.length >
        INITIAL_TEST_COUNT && (
        <button
          className="show-history-button"
          type="button"
          onClick={() =>
            setShowAll(
              (current) => !current,
            )
          }
        >
          {showAll
            ? "Show less"
            : `Show all ${sortedTests.length} MOT tests`}
        </button>
      )}
    </section>
  );
}