"use client";

import {
  FormEvent,
  useEffect,
  useMemo,
  useRef,
  useState,
} from "react";

import {
  AiApiError,
  askVehicleQuestion,
  generateVehicleInsights,
} from "../../lib/aiApi";

import type {
  AiQuestionResponse,
  AiVehicleInsights,
  AiVehicleSnapshot,
} from "../../types/ai";

import styles from "./VehicleAiInsights.module.css";


interface VehicleAiInsightsProps {
  snapshot: AiVehicleSnapshot;
}


export default function VehicleAiInsights({
  snapshot,
}: VehicleAiInsightsProps) {
  const [
    insights,
    setInsights,
  ] =
    useState<AiVehicleInsights | null>(
      null,
    );

  const [
    loading,
    setLoading,
  ] =
    useState(false);

  const [
    error,
    setError,
  ] =
    useState<string | null>(
      null,
    );

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
    useState<AiQuestionResponse | null>(
      null,
    );

  const [
    notificationDismissed,
    setNotificationDismissed,
  ] =
    useState(true);

  const [
    analysisJustCompleted,
    setAnalysisJustCompleted,
  ] =
    useState(false);

  const insightsRef =
    useRef<HTMLElement | null>(
      null,
    );


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
    setInsights(
      null,
    );

    setError(
      null,
    );

    setQuestion(
      "",
    );

    setAnswer(
      null,
    );

    setNotificationDismissed(
      true,
    );

    setAnalysisJustCompleted(
      false,
    );

  }, [
    snapshotKey,
  ]);


  useEffect(() => {
    if (
      loading
      || !analysisJustCompleted
      || notificationDismissed
    ) {
      return;
    }

    const timeout =
      window.setTimeout(
        () => {
          setNotificationDismissed(
            true,
          );

          setAnalysisJustCompleted(
            false,
          );
        },
        15000,
      );

    return () => {
      window.clearTimeout(
        timeout,
      );
    };

  }, [
    loading,
    analysisJustCompleted,
    notificationDismissed,
  ]);


  async function handleGenerate() {
    setLoading(
      true,
    );

    setError(
      null,
    );

    setAnswer(
      null,
    );

    setAnalysisJustCompleted(
      false,
    );

    setNotificationDismissed(
      false,
    );

    try {
      const result =
        await generateVehicleInsights(
          snapshot,
        );

      setInsights(
        result,
      );

      /*
       * Show the completed notification even if
       * the user hid the loading notification.
       */
      setNotificationDismissed(
        false,
      );

      setAnalysisJustCompleted(
        true,
      );

    } catch (
      caughtError
    ) {
      setNotificationDismissed(
        true,
      );

      setAnalysisJustCompleted(
        false,
      );

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
            "We couldn't analyse "
            + "this vehicle right now. "
            + "Please try again."
          ),
        );
      }

    } finally {
      setLoading(
        false,
      );
    }
  }


  async function handleQuestion(
    event:
      FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault();

    const cleanQuestion =
      question.trim();

    if (!cleanQuestion) {
      return;
    }

    setAsking(
      true,
    );

    setError(
      null,
    );

    setAnswer(
      null,
    );

    try {
      const result =
        await askVehicleQuestion(
          snapshot,
          cleanQuestion,
        );

      setAnswer(
        result,
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
            "We couldn't answer "
            + "that question right now. "
            + "Please try again."
          ),
        );
      }

    } finally {
      setAsking(
        false,
      );
    }
  }


  function handleViewInsights() {
    setNotificationDismissed(
      true,
    );

    setAnalysisJustCompleted(
      false,
    );

    insightsRef
      .current
      ?.scrollIntoView({
        behavior: "smooth",
        block: "start",
      });
  }


  function handleDismissNotification() {
    setNotificationDismissed(
      true,
    );
  }


  return (
    <>
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
          <div
            className={
              styles.headerContent
            }
          >
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

              <div>
                <span
                  className={
                    styles.eyebrow
                  }
                >
                  Vehicle history analysis
                </span>

                <h2>
                  AI Vehicle Insights
                </h2>
              </div>
            </div>

            <p
              className={
                styles.description
              }
            >
              Understand this vehicle&apos;s
              recent history at a glance.
              MyGarage reviews MOT records
              from the last 5 years to
              highlight recurring issues,
              failures and mileage patterns.
            </p>
          </div>

          <button
            className={
              styles.generateButton
            }
            type="button"
            disabled={
              loading
            }
            onClick={
              handleGenerate
            }
          >
            {loading
              ? "Analysing..."
              : insights
                ? "Refresh analysis"
                : "Analyse recent MOTs"}
          </button>
        </div>

        {loading && (
          <div
            className={
              styles.loading
            }
          >
            <div
              className="loader"
            />

            <div>
              <strong>
                Reviewing recent MOT history
              </strong>

              <span>
                You can keep browsing while
                MyGarage analyses the vehicle.
                We&apos;ll let you know when
                the results are ready.
              </span>
            </div>
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

        {insights && (
          <div
            className={
              styles.content
            }
          >
            <section
              ref={
                insightsRef
              }
              className={
                styles.ratingSection
              }
            >
              <div
                className={
                  styles.ratingTop
                }
              >
                <div>
                  <span
                    className={
                      styles.sectionEyebrow
                    }
                  >
                    Recent MOT history rating
                  </span>

                  <div
                    className={
                      styles.ratingHeading
                    }
                  >
                    <strong
                      className={`${styles.ratingScore} ${
                        styles[
                          insights
                            .rating
                            .tone
                        ]
                      }`}
                    >
                      {
                        insights
                          .rating
                          .score
                      }

                      <small>
                        /100
                      </small>
                    </strong>

                    <span
                      className={`${styles.ratingLabel} ${
                        styles[
                          insights
                            .rating
                            .tone
                        ]
                      }`}
                    >
                      {
                        insights
                          .rating
                          .label
                      }
                    </span>
                  </div>
                </div>

                <p
                  className={
                    styles.ratingExplanation
                  }
                >
                  {
                    insights
                      .rating
                      .explanation
                  }
                </p>
              </div>

              <div
                className={
                  styles.ratingTrack
                }
                aria-hidden="true"
              >
                <div
                  className={`${styles.ratingFill} ${
                    styles[
                      insights
                        .rating
                        .tone
                    ]
                  }`}
                  style={{
                    width:
                      `${
                        insights
                          .rating
                          .score
                      }%`,
                  }}
                />
              </div>

              <div
                className={
                  styles.ratingScale
                }
              >
                <span>
                  Concerning
                </span>

                <span>
                  Needs attention
                </span>

                <span>
                  Fair
                </span>

                <span>
                  Good
                </span>

                <span>
                  Excellent
                </span>
              </div>

              <p
                className={
                  styles.ratingNote
                }
              >
                Based on MOT records from
                the last 5 years. This is a
                history-based rating, not a
                mechanical inspection.
              </p>
            </section>

            <section
              className={
                styles.summarySection
              }
            >
              <span
                className={
                  styles.sectionEyebrow
                }
              >
                Recent MOT summary
              </span>

              <p
                className={
                  styles.summary
                }
              >
                {insights.summary}
              </p>
            </section>

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

                <small>
                  In the analysis period
                </small>
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

                <small>
                  Recorded failed tests
                </small>
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

                <small>
                  Recorded advisory items
                </small>
              </div>

              <div
                className={
                  styles.stat
                }
              >
                <span>
                  Major defects
                </span>

                <strong>
                  {
                    insights
                      .mot_stats
                      .major
                  }
                </strong>

                <small>
                  Recorded major items
                </small>
              </div>
            </div>

            {insights
              .insights
              .length > 0 && (
                <section
                  className={
                    styles.section
                  }
                >
                  <div
                    className={
                      styles.sectionHeading
                    }
                  >
                    <div>
                      <span
                        className={
                          styles.sectionEyebrow
                        }
                      >
                        Patterns found
                      </span>

                      <h3>
                        Key insights
                      </h3>
                    </div>
                  </div>

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

                              <h4>
                                {
                                  insight
                                    .title
                                }
                              </h4>
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
                              <strong>
                                Based on:
                              </strong>{" "}
                              {
                                insight
                                  .evidence
                              }
                            </span>
                          </article>
                        ),
                      )}
                  </div>
                </section>
              )}

            {insights
              .recurring_items
              .length > 0 && (
                <section
                  className={
                    styles.section
                  }
                >
                  <div
                    className={
                      styles.sectionHeading
                    }
                  >
                    <div>
                      <span
                        className={
                          styles.sectionEyebrow
                        }
                      >
                        Repeated findings
                      </span>

                      <h3>
                        Recurring MOT areas
                      </h3>
                    </div>
                  </div>

                  <p
                    className={
                      styles.sectionCopy
                    }
                  >
                    These areas were mentioned
                    on more than one recent MOT.
                    Repeated findings do not
                    necessarily mean the same
                    fault remained unresolved.
                  </p>

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
                </section>
              )}

            <section
              className={
                styles.section
              }
            >
              <div
                className={
                  styles.sectionHeading
                }
              >
                <div>
                  <span
                    className={
                      styles.sectionEyebrow
                    }
                  >
                    Recorded usage
                  </span>

                  <h3>
                    Mileage analysis
                  </h3>
                </div>
              </div>

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
            </section>

            {insights
              .supplementary_note && (
                <div
                  className={
                    styles.supplementary
                  }
                >
                  <strong>
                    Additional context
                  </strong>

                  <span>
                    {
                      insights
                        .supplementary_note
                    }
                  </span>
                </div>
              )}

            <section
              className={
                styles.ask
              }
            >
              <div
                className={
                  styles.sectionHeading
                }
              >
                <div>
                  <span
                    className={
                      styles.sectionEyebrow
                    }
                  >
                    Explore the history
                  </span>

                  <h3>
                    Ask about this vehicle
                  </h3>
                </div>
              </div>

              <p
                className={
                  styles.askCopy
                }
              >
                Ask about failures,
                advisories, recurring issues
                or mileage recorded across
                the vehicle&apos;s recent MOT
                history.
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
                    ? "Checking..."
                    : "Ask"}
                </button>
              </form>

              {answer && (
                <div
                  className={
                    styles.answer
                  }
                >
                  <span>
                    Answer
                  </span>

                  <p>
                    {answer.answer}
                  </p>
                </div>
              )}
            </section>

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

      {!notificationDismissed
        && loading && (
          <div
            className={`${styles.aiToast} ${styles.processingToast}`}
            role="status"
            aria-live="polite"
          >
            <span
              className={
                styles.toastSpinner
              }
              aria-hidden="true"
            />

            <div
              className={
                styles.toastContent
              }
            >
              <strong>
                Analysing recent MOTs
              </strong>

              <span>
                You can keep browsing.
                We&apos;ll let you know
                when it&apos;s ready.
              </span>
            </div>

            <button
              className={
                styles.toastClose
              }
              type="button"
              aria-label={
                "Dismiss analysis notification"
              }
              title={
                "Dismiss"
              }
              onClick={
                handleDismissNotification
              }
            >
              ×
            </button>
          </div>
        )}

      {!notificationDismissed
        && !loading
        && analysisJustCompleted
        && insights && (
          <div
            className={`${styles.aiToast} ${styles.completedToast}`}
            role="status"
            aria-live="polite"
          >
            <button
              className={
                styles.toastOpen
              }
              type="button"
              onClick={
                handleViewInsights
              }
            >
              <span
                className={
                  styles.readyIcon
                }
                aria-hidden="true"
              >
                ✓
              </span>

              <span
                className={
                  styles.toastContent
                }
              >
                <strong>
                  Vehicle analysis ready
                </strong>

                <span>
                  View the latest rating
                  and insights.
                </span>
              </span>

              <span
                className={
                  styles.readyAction
                }
              >
                View
              </span>
            </button>

            <button
              className={
                styles.toastClose
              }
              type="button"
              aria-label={
                "Dismiss notification"
              }
              title={
                "Dismiss"
              }
              onClick={
                handleDismissNotification
              }
            >
              ×
            </button>
          </div>
        )}
    </>
  );
}