"use client";

import Link from "next/link";

import {
  useAuth,
} from "../../contexts/AuthContext";

import styles from "./HomeMarketing.module.css";


function HistoryIcon() {
  return (
    <svg
      viewBox="0 0 24 24"
      aria-hidden="true"
    >
      <path d="M12 7v5l3 2" />
      <path d="M4.9 5.5A9 9 0 1 1 3 12" />
      <path d="M3 5v5h5" />
    </svg>
  );
}


function AiIcon() {
  return (
    <svg
      viewBox="0 0 24 24"
      aria-hidden="true"
    >
      <path d="M12 3l1.25 4.25L17.5 8.5l-4.25 1.25L12 14l-1.25-4.25L6.5 8.5l4.25-1.25L12 3Z" />
      <path d="M18.5 14l.75 2.25L21.5 17l-2.25.75L18.5 20l-.75-2.25L15.5 17l2.25-.75L18.5 14Z" />
    </svg>
  );
}


function VehicleIcon() {
  return (
    <svg
      viewBox="0 0 24 24"
      aria-hidden="true"
    >
      <path d="M5 16h14" />
      <path d="M6 16l1-5h10l1 5" />
      <path d="M8 11l1.5-3h5L16 11" />
      <path d="M6 16v2" />
      <path d="M18 16v2" />

      <circle
        cx="8"
        cy="16"
        r="1"
      />

      <circle
        cx="16"
        cy="16"
        r="1"
      />
    </svg>
  );
}


function ServiceIcon() {
  return (
    <svg
      viewBox="0 0 24 24"
      aria-hidden="true"
    >
      <path d="M14 6a4 4 0 0 0-5 5L4 16l4 4 5-5a4 4 0 0 0 5-5l-3 3-3-3 2-4Z" />
    </svg>
  );
}


function ReminderIcon() {
  return (
    <svg
      viewBox="0 0 24 24"
      aria-hidden="true"
    >
      <path d="M6 9a6 6 0 0 1 12 0v4l2 3H4l2-3V9Z" />
      <path d="M10 19h4" />
    </svg>
  );
}


function MileageIcon() {
  return (
    <svg
      viewBox="0 0 24 24"
      aria-hidden="true"
    >
      <path d="M4 18V6" />
      <path d="M4 18h16" />
      <path d="M7 15l3-4 3 2 5-6" />
    </svg>
  );
}


function ChecksIcon() {
  return (
    <svg
      viewBox="0 0 24 24"
      aria-hidden="true"
    >
      <path d="M7 4h10v16H7z" />
      <path d="M9 8h6" />
      <path d="M9 12h6" />
      <path d="M9 16h3" />
    </svg>
  );
}


function ReceiptIcon() {
  return (
    <svg
      viewBox="0 0 24 24"
      aria-hidden="true"
    >
      <path d="M7 3h10v18l-2-1.5L13 21l-2-1.5L9 21l-2-1.5V3Z" />
      <path d="M9 8h6" />
      <path d="M9 12h6" />
      <path d="M9 16h4" />
    </svg>
  );
}


export default function HomeMarketing() {
  const {
    user,
  } = useAuth();


  return (
    <>
      <section
        className={
          styles.quickValue
        }
        aria-labelledby="home-value-heading"
      >
        <div
          className={
            styles.sectionInner
          }
        >
          <div
            className={
              styles.sectionIntro
            }
          >
            <span
              className={
                styles.eyebrow
              }
            >
              More than an MOT checker
            </span>

            <h2
              id="home-value-heading"
            >
              Understand a vehicle.
              <br />
              Then keep on top of it.
            </h2>

            <p>
              Enter a registration to see a
              clearer picture of the vehicle&apos;s
              MOT history, mileage and recurring
              issues.
            </p>
          </div>

          <div
            className={
              styles.primaryFeatures
            }
          >
            <article
              className={
                styles.primaryCard
              }
            >
              <div
                className={
                  styles.primaryCardHeader
                }
              >
                <div
                  className={
                    styles.iconBox
                  }
                >
                  <HistoryIcon />
                </div>

                <span
                  className={
                    styles.featureCategory
                  }
                >
                  Vehicle history
                </span>
              </div>

              <div
                className={
                  styles.primaryCardContent
                }
              >
                <h3>
                  Complete MOT history
                </h3>

                <p>
                  See passes, failures,
                  advisories and recorded
                  defects in one clear timeline.
                </p>
              </div>
            </article>

            <article
              className={
                styles.primaryCard
              }
            >
              <div
                className={
                  styles.primaryCardHeader
                }
              >
                <div
                  className={
                    styles.iconBox
                  }
                >
                  <MileageIcon />
                </div>

                <span
                  className={
                    styles.featureCategory
                  }
                >
                  Mileage tracking
                </span>
              </div>

              <div
                className={
                  styles.primaryCardContent
                }
              >
                <h3>
                  Mileage trends
                </h3>

                <p>
                  Track recorded mileage
                  over time and see how it
                  changes between MOTs.
                </p>
              </div>
            </article>

            <article
              className={
                styles.primaryCard
              }
            >
              <div
                className={
                  styles.primaryCardHeader
                }
              >
                <div
                  className={
                    styles.iconBox
                  }
                >
                  <AiIcon />
                </div>

                <span
                  className={
                    styles.featureCategory
                  }
                >
                  Vehicle insights
                </span>
              </div>

              <div
                className={
                  styles.primaryCardContent
                }
              >
                <h3>
                  Make sense of the history
                </h3>

                <p>
                  Review recent MOT records,
                  spot recurring concerns and
                  get a clear MOT-history rating.
                </p>
              </div>
            </article>
          </div>
        </div>
      </section>

      <section
        className={
          styles.platform
        }
        aria-labelledby="platform-heading"
      >
        <div
          className={
            styles.sectionInner
          }
        >
          <div
            className={
              styles.platformHeading
            }
          >
            <div>
              <span
                className={
                  styles.eyebrow
                }
              >
                Your own digital garage
              </span>

              <h2
                id="platform-heading"
              >
                Everything you need to manage
                your vehicles in one place.
              </h2>
            </div>

            <p>
              Keep your vehicles, servicing,
              maintenance and reminders together
              in one simple digital garage.
            </p>
          </div>

          <div
            className={
              styles.featureGrid
            }
          >
            <article
              className={`${styles.featureCard} ${styles.featureCardWide}`}
            >
              <div
                className={
                  styles.featureIcon
                }
              >
                <VehicleIcon />
              </div>

              <div
                className={
                  styles.featureText
                }
              >
                <span
                  className={
                    styles.featureLabel
                  }
                >
                  My Vehicles
                </span>

                <h3>
                  Your vehicles, all in one place
                </h3>

                <p>
                  Keep each vehicle&apos;s MOT
                  history, servicing and
                  maintenance together in one
                  place.
                </p>
              </div>

              <Link
                className={
                  styles.cardLink
                }
                href={
                  user
                    ? "/vehicles"
                    : "/login"
                }
              >
                {user
                  ? "Open My Vehicles"
                  : "Sign in to start"}

                <span
                  aria-hidden="true"
                >
                  →
                </span>
              </Link>
            </article>

            <article
              className={
                styles.featureCard
              }
            >
              <div
                className={
                  styles.featureCardTop
                }
              >
                <div
                  className={
                    styles.featureIcon
                  }
                >
                  <ServiceIcon />
                </div>

                <span
                  className={
                    styles.featureLabel
                  }
                >
                  Service history
                </span>
              </div>

              <h3>
                Keep a record of the work
              </h3>

              <p>
                Record services, repairs,
                replacement parts, mileage,
                costs and garage details.
              </p>
            </article>

            <article
              className={
                styles.featureCard
              }
            >
              <div
                className={
                  styles.featureCardTop
                }
              >
                <div
                  className={
                    styles.featureIcon
                  }
                >
                  <ReminderIcon />
                </div>

                <span
                  className={
                    styles.featureLabel
                  }
                >
                  Maintenance &amp; reminders
                </span>
              </div>

              <h3>
                Know what needs doing next
              </h3>

              <p>
                Track maintenance by date
                or mileage and get reminders
                when work is due soon or
                overdue.
              </p>
            </article>

            <article
              className={
                styles.featureCard
              }
            >
              <div
                className={
                  styles.featureCardTop
                }
              >
                <div
                  className={
                    styles.featureIcon
                  }
                >
                  <ChecksIcon />
                </div>

                <span
                  className={
                    styles.featureLabel
                  }
                >
                  My Checks
                </span>
              </div>

              <h3>
                Come back to vehicles you checked
              </h3>

              <p>
                Quickly return to vehicles
                you&apos;ve checked before and
                review their latest history.
              </p>
            </article>

            <article
              className={
                styles.featureCard
              }
            >
              <div
                className={
                  styles.featureCardTop
                }
              >
                <div
                  className={
                    styles.featureIcon
                  }
                >
                  <ReceiptIcon />
                </div>

                <span
                  className={
                    styles.featureLabel
                  }
                >
                  Receipts &amp; records
                </span>
              </div>

              <h3>
                Keep the paperwork with the car
              </h3>

              <p>
                Attach receipts to service
                records so important paperwork
                stays with the vehicle&apos;s
                history.
              </p>
            </article>
          </div>
        </div>
      </section>

      <section
        className={
          styles.aiShowcase
        }
        aria-labelledby="ai-heading"
      >
        <div
          className={
            styles.aiInner
          }
        >
          <div
            className={
              styles.aiCopy
            }
          >
            <span
              className={
                styles.darkEyebrow
              }
            >
              AI Vehicle Insights
            </span>

            <h2
              id="ai-heading"
            >
              Go beyond a list of MOT records.
            </h2>

            <p>
              MyGarage reviews the last
              five years of MOT history to
              highlight recurring issues,
              failures and mileage patterns
              that can be easy to miss.
            </p>

            <ul
              className={
                styles.aiList
              }
            >
              <li>
                <span>
                  ✓
                </span>

                A clear recent MOT-history
                rating out of 100
              </li>

              <li>
                <span>
                  ✓
                </span>

                Recurring defect and advisory
                patterns
              </li>

              <li>
                <span>
                  ✓
                </span>

                Clear mileage and MOT
                summaries
              </li>

              <li>
                <span>
                  ✓
                </span>

                Ask questions about a
                vehicle&apos;s recent history
              </li>
            </ul>

            <a
              className={
                styles.aiCta
              }
              href="#vehicle-check"
            >
              Check a vehicle

              <span
                aria-hidden="true"
              >
                ↑
              </span>
            </a>
          </div>

          <div
            className={
              styles.aiPreview
            }
            aria-hidden="true"
          >
            <div
              className={
                styles.previewTop
              }
            >
              <div
                className={
                  styles.previewSpark
                }
              >
                ✦
              </div>

              <div>
                <span>
                  Vehicle history analysis
                </span>

                <strong>
                  AI Vehicle Insights
                </strong>
              </div>
            </div>

            <div
              className={
                styles.scoreRow
              }
            >
              <div>
                <span>
                  Recent MOT history rating
                </span>

                <strong>
                  86

                  <small>
                    /100
                  </small>
                </strong>
              </div>

              <span
                className={
                  styles.goodBadge
                }
              >
                Good
              </span>
            </div>

            <div
              className={
                styles.scoreTrack
              }
            >
              <span />
            </div>

            <div
              className={
                styles.previewCards
              }
            >
              <div>
                <span
                  className={
                    styles.previewDot
                  }
                />

                <strong>
                  Recurring brake wear
                </strong>

                <p>
                  Brake-related advisories
                  appear across multiple
                  recent MOTs.
                </p>
              </div>

              <div>
                <span
                  className={`${styles.previewDot} ${styles.previewDotBlue}`}
                />

                <strong>
                  Consistent mileage
                </strong>

                <p>
                  Recorded mileage progresses
                  consistently through recent
                  tests.
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section
        className={
          styles.howItWorks
        }
        aria-labelledby="how-heading"
      >
        <div
          className={
            styles.sectionInner
          }
        >
          <div
            className={
              styles.centerHeading
            }
          >
            <span
              className={
                styles.eyebrow
              }
            >
              Simple from the start
            </span>

            <h2
              id="how-heading"
            >
              From a registration to a
              clearer vehicle history.
            </h2>
          </div>

          <div
            className={
              styles.steps
            }
          >
            <div
              className={
                styles.step
              }
            >
              <span
                className={
                  styles.stepNumber
                }
              >
                1
              </span>

              <div>
                <h3>
                  Enter a registration
                </h3>

                <p>
                  Enter any UK registration
                  to view its MOT history.
                </p>
              </div>
            </div>

            <div
              className={
                styles.stepConnector
              }
              aria-hidden="true"
            />

            <div
              className={
                styles.step
              }
            >
              <span
                className={
                  styles.stepNumber
                }
              >
                2
              </span>

              <div>
                <h3>
                  Review its history
                </h3>

                <p>
                  Review MOT results,
                  mileage, defects and
                  AI-powered insights.
                </p>
              </div>
            </div>

            <div
              className={
                styles.stepConnector
              }
              aria-hidden="true"
            />

            <div
              className={
                styles.step
              }
            >
              <span
                className={
                  styles.stepNumber
                }
              >
                3
              </span>

              <div>
                <h3>
                  Add your vehicle
                </h3>

                <p>
                  Keep servicing,
                  maintenance and reminders
                  together in your garage.
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section
        className={
          styles.finalCta
        }
      >
        <div
          className={
            styles.finalCtaInner
          }
        >
          <div>
            <span
              className={
                styles.darkEyebrow
              }
            >
              MyGarage UK
            </span>

            <h2>
              Your vehicle history,
              without the guesswork.
            </h2>

            <p>
              Check a vehicle in seconds, or
              create an account to manage your
              own garage.
            </p>
          </div>

          <div
            className={
              styles.finalActions
            }
          >
            <a
              className={
                styles.primaryCta
              }
              href="#vehicle-check"
            >
              Check a vehicle
            </a>

            {!user && (
              <Link
                className={
                  styles.secondaryCta
                }
                href="/register"
              >
                Create an account
              </Link>
            )}

            {user && (
              <Link
                className={
                  styles.secondaryCta
                }
                href="/vehicles"
              >
                Open My Vehicles
              </Link>
            )}
          </div>
        </div>
      </section>
    </>
  );
}