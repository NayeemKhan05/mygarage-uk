"use client";

import {
  FormEvent,
  useEffect,
  useMemo,
  useState,
} from "react";

import {
  AiApiError,
  askVehicleQuestion,
  generateVehicleInsights,
  getAiStatus,
} from "../../lib/aiApi";

import type {
  AiQuestionResponse,
  AiStatus,
  AiVehicleInsights,
  AiVehicleSnapshot,
} from "../../types/ai";

import styles from "./VehicleAiInsights.module.css";


interface VehicleAiInsightsProps {
  snapshot:
    AiVehicleSnapshot;
}


function toneLabel(
  tone:
    AiVehicleInsights[
      "overall_tone"
    ],
): string {
  if (
    tone === "positive"
  ) {
    return "Positive";
  }

  if (
    tone === "watch"
  ) {
    return "Worth watching";
  }

  if (
    tone === "attention"
  ) {
    return "Needs attention";
  }

  return "Neutral";
}


export default function VehicleAiInsights({
  snapshot,
}: VehicleAiInsightsProps) {
  const [
    status,
    setStatus,
  ] =
    useState<
      AiStatus | null
    >(null);

  const [
    statusLoading,
    setStatusLoading,
  ] =
    useState(true);

  const [
    insights,
    setInsights,
  ] =
    useState<
      AiVehicleInsights | null
    >(null);

  const [
    loading,
    setLoading,
  ] =
    useState(false);

  const [
    error,
    setError,
  ] =
    useState<
      string | null
    >(null);

  const [
    question,
    setQuestion,
  ] =
    useState("");

  const [
    asking,
    setAsking,
  ] =
    useState(false);

  const [
    answer,
    setAnswer,
  ] =
    useState<
      AiQuestionResponse | null
    >(null);


  const snapshotKey =
    useMemo(
      () => {
        const latest =
          snapshot
            .mot_tests[0]
            ?.completed_at
          ?? "";

        return (
          snapshot.registration
          + ":"
          + snapshot
            .mot_tests
            .length
          + ":"
          + latest
        );
      },
      [
        snapshot,
      ],
    );


  useEffect(() => {
    let cancelled =
      false;

    async function loadStatus() {
      try {
        const result =
          await getAiStatus();

        if (!cancelled) {
          setStatus(
            result,
          );
        }

      } catch {
        if (!cancelled) {
          setStatus({
            available:
              false,

            model:
              (
                "qwen3:"
                + "4b-instruct"
              ),

            message:
              (
                "The local AI "
                + "service is "
                + "unavailable."
              ),
          });
        }

      } finally {
        if (!cancelled) {
          setStatusLoading(
            false,
          );
        }
      }
    }

    void loadStatus();

    return () => {
      cancelled =
        true;
    };
  }, []);


  useEffect(() => {
    setInsights(
      null
    );

    setError(
      null
    );

    setQuestion(
      ""
    );

    setAnswer(
      null
    );

  }, [
    snapshotKey,
  ]);


  async function handleGenerate() {
    setLoading(
      true
    );

    setError(
      null
    );

    setAnswer(
      null
    );

    try {
      const result =
        await generateVehicleInsights(
          snapshot,
        );

      setInsights(
        result
      );

    } catch (
      caughtError
    ) {
      if (
        caughtError
        instanceof AiApiError
      ) {
        setError(
          caughtError.message,
        );

      } else {
        setError(
          (
            "We could not "
            + "generate local "
            + "AI insights."
          ),
        );
      }

    } finally {
      setLoading(
        false
      );
    }
  }


  async function handleQuestion(
    event:
      FormEvent<
        HTMLFormElement
      >,
  ) {
    event.preventDefault();

    const cleanQuestion =
      question.trim();

    if (!cleanQuestion) {
      return;
    }

    setAsking(
      true
    );

    setError(
      null
    );

    setAnswer(
      null
    );

    try {
      const result =
        await askVehicleQuestion(
          snapshot,
          cleanQuestion,
        );

      setAnswer(
        result
      );

    } catch (
      caughtError
    ) {
      if (
        caughtError
        instanceof AiApiError
      ) {
        setError(
          caughtError.message,
        );

      } else {
        setError(
          (
            "We could not "
            + "answer that "
            + "question."
          ),
        );
      }

    } finally {
      setAsking(
        false
      );
    }
  }


  return (
    <section
      className={
        styles.panel
      }
    >
      <div
        className={
          styles.header
        }
      >
        <div>
          <div
            className={
              styles.titleRow
            }
          >
            <span
              className={
                styles.mark
              }
              aria-hidden="true"
            >
              ✦
            </span>

            <h2>
              AI Vehicle Insights
            </h2>
          </div>

          <p
            className={
              styles.description
            }
          >
            Local AI analysis grounded
            primarily in this vehicle&apos;s
            DVSA MOT history. Owner-entered
            records are only supplementary
            when available.
          </p>

          <div
            className={
              styles.badges
            }
          >
            <span
              className={
                styles.badge
              }
            >
              MOT-first analysis
            </span>

            <span
              className={
                styles.modelBadge
              }
            >
              {
                status?.model
                ?? (
                  "qwen3:"
                  + "4b-instruct"
                )
              }
            </span>

            <span
              className={
                styles.modelBadge
              }
            >
              Runs locally
            </span>
          </div>
        </div>

        <button
          className={
            styles.generateButton
          }
          type="button"
          disabled={
            loading
            || statusLoading
            || (
              status
              !== null
              && !status.available
            )
          }
          onClick={
            handleGenerate
          }
        >
          {loading
            ? "Analysing..."
            : insights
              ? "Refresh insights"
              : "Generate insights"}
        </button>
      </div>

      {!statusLoading
        && status && (
          <div
            className={`${styles.statusMessage} ${
              status.available
                ? ""
                : styles.unavailable
            }`}
          >
            {status.message}
          </div>
        )}

      {loading && (
        <div
          className={
            styles.loading
          }
        >
          <div
            className="loader"
          />

          Analysing MOT history
          locally...
        </div>
      )}

      {error && (
        <div
          className={
            styles.error
          }
          role="alert"
        >
          {error}
        </div>
      )}

      {insights
        && !loading && (
          <div
            className={
              styles.content
            }
          >
            <div
              className={
                styles.summaryRow
              }
            >
              <span
                className={`${styles.tone} ${
                  styles[
                    insights
                      .overall_tone
                  ]
                }`}
              >
                {toneLabel(
                  insights
                    .overall_tone,
                )}
              </span>

              <p
                className={
                  styles.summary
                }
              >
                {insights.summary}
              </p>
            </div>

            <div
              className={
                styles.stats
              }
            >
              <div
                className={
                  styles.stat
                }
              >
                <span>
                  MOT tests
                </span>

                <strong>
                  {
                    insights
                      .mot_stats
                      .tests
                  }
                </strong>
              </div>

              <div
                className={
                  styles.stat
                }
              >
                <span>
                  Failed
                </span>

                <strong>
                  {
                    insights
                      .mot_stats
                      .failed
                  }
                </strong>
              </div>

              <div
                className={
                  styles.stat
                }
              >
                <span>
                  Advisories
                </span>

                <strong>
                  {
                    insights
                      .mot_stats
                      .advisory
                  }
                </strong>
              </div>

              <div
                className={
                  styles.stat
                }
              >
                <span>
                  Major
                </span>

                <strong>
                  {
                    insights
                      .mot_stats
                      .major
                  }
                </strong>
              </div>
            </div>

            {insights
              .insights
              .length > 0 && (
                <div
                  className={
                    styles.insightGrid
                  }
                >
                  {insights
                    .insights
                    .map(
                      (
                        insight,
                        index,
                      ) => (
                        <article
                          className={
                            styles.insight
                          }
                          key={
                            `${insight.title}-${index}`
                          }
                        >
                          <div
                            className={
                              styles.insightTitle
                            }
                          >
                            <span
                              className={`${styles.dot} ${
                                styles[
                                  insight.level
                                ]
                              }`}
                            />

                            <h3>
                              {
                                insight
                                  .title
                              }
                            </h3>
                          </div>

                          <p>
                            {
                              insight
                                .detail
                            }
                          </p>

                          <span
                            className={
                              styles.evidence
                            }
                          >
                            Evidence:{" "}
                            {
                              insight
                                .evidence
                            }
                          </span>
                        </article>
                      ),
                    )}
                </div>
              )}

            {insights
              .recurring_items
              .length > 0 && (
                <div
                  className={
                    styles.section
                  }
                >
                  <h3>
                    Recurring MOT areas
                  </h3>

                  <div
                    className={
                      styles.recurringList
                    }
                  >
                    {insights
                      .recurring_items
                      .map(
                        (
                          item,
                        ) => (
                          <div
                            className={
                              styles.recurring
                            }
                            key={
                              item.label
                            }
                          >
                            <span>
                              {item.label}
                            </span>

                            <strong>
                              {
                                item.count
                              }{" "}
                              MOTs
                            </strong>
                          </div>
                        ),
                      )}
                  </div>
                </div>
              )}

            <div
              className={
                styles.section
              }
            >
              <h3>
                Mileage analysis
              </h3>

              <p
                className={
                  styles.analysis
                }
              >
                {
                  insights
                    .mileage_analysis
                }
              </p>
            </div>

            {insights
              .supplementary_note && (
                <div
                  className={
                    styles.supplementary
                  }
                >
                  {
                    insights
                      .supplementary_note
                  }
                </div>
              )}

            <div
              className={
                styles.ask
              }
            >
              <h3>
                Ask about this vehicle
              </h3>

              <p
                className={
                  styles.askCopy
                }
              >
                Ask about recurring MOT
                issues, failures, advisories
                or mileage patterns.
              </p>

              <form
                className={
                  styles.form
                }
                onSubmit={
                  handleQuestion
                }
              >
                <input
                  className={
                    styles.input
                  }
                  type="text"
                  maxLength={
                    500
                  }
                  value={
                    question
                  }
                  placeholder="What problems keep appearing?"
                  onChange={(
                    event,
                  ) =>
                    setQuestion(
                      event
                        .target
                        .value,
                    )
                  }
                />

                <button
                  className={
                    styles.askButton
                  }
                  type="submit"
                  disabled={
                    asking
                    || !question
                      .trim()
                  }
                >
                  {asking
                    ? "Asking..."
                    : "Ask AI"}
                </button>
              </form>

              {answer && (
                <div
                  className={
                    styles.answer
                  }
                >
                  <span>
                    Local AI answer
                  </span>

                  <p>
                    {answer.answer}
                  </p>
                </div>
              )}
            </div>

            <p
              className={
                styles.disclaimer
              }
            >
              {
                insights
                  .disclaimer
              }
            </p>
          </div>
        )}
    </section>
  );
}