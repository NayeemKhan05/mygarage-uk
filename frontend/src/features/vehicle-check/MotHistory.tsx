import type {
  MotDefect,
  MotTest,
} from "../../types/vehicle";

import {
  formatDate,
  formatMileage,
  getMileageChange,
  sortMotTests,
} from "./utils";


interface MotHistoryProps {
  motTests: MotTest[];
}


interface DefectGroup {
  title: string;
  tone: string;
  defects: MotDefect[];
}


function groupDefects(
  defects: MotDefect[],
): DefectGroup[] {
  const dangerous = defects.filter(
    (defect) =>
      defect.dangerous ||
      defect.type.toUpperCase() === "DANGEROUS",
  );

  const major = defects.filter(
    (defect) =>
      defect.type.toUpperCase() === "MAJOR" &&
      !dangerous.includes(defect),
  );

  const minor = defects.filter(
    (defect) =>
      defect.type.toUpperCase() === "MINOR",
  );

  const advisory = defects.filter(
    (defect) =>
      defect.type.toUpperCase() === "ADVISORY",
  );

  const prs = defects.filter(
    (defect) =>
      defect.type.toUpperCase() === "PRS",
  );

  const knownDefects = new Set([
    ...dangerous,
    ...major,
    ...minor,
    ...advisory,
    ...prs,
  ]);

  // This should rarely appear, but keeping a fallback means the UI
  // will still cope if DVSA adds another defect type in future.
  const other = defects.filter(
    (defect) => !knownDefects.has(defect),
  );

  return [
    {
      title: "Dangerous defects",
      tone: "dangerous",
      defects: dangerous,
    },
    {
      title: "Major defects",
      tone: "major",
      defects: major,
    },
    {
      title: "Minor defects",
      tone: "minor",
      defects: minor,
    },
    {
      title: "Advisories",
      tone: "advisory",
      defects: advisory,
    },
    {
      title: "Repaired during MOT",
      tone: "prs",
      defects: prs,
    },
    {
      title: "Other recorded items",
      tone: "other",
      defects: other,
    },
  ].filter(
    (group) => group.defects.length > 0,
  );
}


export default function MotHistory({
  motTests,
}: MotHistoryProps) {
  const sortedTests =
    sortMotTests(motTests);

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
    <section className="panel mot-history-panel">
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

      <div className="mot-table-header">
        <span>Date</span>
        <span>Result</span>
        <span>Details</span>
      </div>

      <div className="mot-history-list">
        {sortedTests.map(
          (test, index) => {
            const result =
              test.test_result?.toUpperCase() ??
              "UNKNOWN";

            const passed =
              result === "PASSED";

            const previousTest =
              sortedTests[index + 1];

            const mileageChange =
              getMileageChange(
                test,
                previousTest,
              );

            const defectGroups =
              groupDefects(test.defects);

            return (
              <article
                className={`mot-history-row ${
                  passed
                    ? "mot-pass"
                    : "mot-fail"
                }`}
                key={test.mot_test_number}
              >
                <div className="mot-history-date">
                  <strong>
                    {formatDate(
                      test.completed_at,
                    )}
                  </strong>

                  <span>
                    {new Intl.DateTimeFormat(
                      "en-GB",
                      {
                        hour: "2-digit",
                        minute: "2-digit",
                        hour12: false,
                      },
                    ).format(
                      new Date(
                        test.completed_at,
                      ),
                    )}
                  </span>
                </div>

                <div className="mot-history-result">
                  <span
                    className={
                      passed
                        ? "mot-result-box pass"
                        : "mot-result-box fail"
                    }
                  >
                    {passed
                      ? "Pass"
                      : result === "FAILED"
                        ? "Fail"
                        : result}
                  </span>
                </div>

                <div className="mot-history-details">
                  <div className="mot-mileage-line">
                    <strong>
                      Mileage:
                    </strong>

                    <span>
                      {formatMileage(
                        test.odometer_value,
                        test.odometer_unit,
                      )}
                    </span>
                  </div>

                  <div
                    className={`mot-mileage-change ${mileageChange.tone}`}
                  >
                    {mileageChange.label}
                  </div>

                  {test.expiry_date && passed && (
                    <div className="mot-expiry-line">
                      <strong>
                        MOT valid until:
                      </strong>

                      <span>
                        {formatDate(
                          test.expiry_date,
                        )}
                      </span>
                    </div>
                  )}

                  {defectGroups.length === 0 ? (
                    <div className="mot-clean-result">
                      No defects or advisories
                      recorded.
                    </div>
                  ) : (
                    <div className="mot-defect-groups">
                      {defectGroups.map(
                        (group) => (
                          <div
                            className={`mot-defect-group ${group.tone}`}
                            key={group.title}
                          >
                            <div className="mot-defect-heading">
                              <span
                                className={`mot-defect-dot ${group.tone}`}
                              />

                              <strong>
                                {group.title}
                              </strong>

                              <span className="mot-defect-total">
                                {
                                  group.defects
                                    .length
                                }
                              </span>
                            </div>

                            <ul>
                              {group.defects.map(
                                (
                                  defect,
                                  defectIndex,
                                ) => (
                                  <li
                                    key={`${test.mot_test_number}-${group.title}-${defectIndex}`}
                                  >
                                    {defect.text}
                                  </li>
                                ),
                              )}
                            </ul>
                          </div>
                        ),
                      )}
                    </div>
                  )}

                  <div className="mot-record-meta">
                    <span>
                      Test number:{" "}
                      {test.mot_test_number}
                    </span>

                    {test.registration_at_time_of_test && (
                      <span>
                        Registration:{" "}
                        {
                          test.registration_at_time_of_test
                        }
                      </span>
                    )}
                  </div>
                </div>
              </article>
            );
          },
        )}
      </div>
    </section>
  );
}