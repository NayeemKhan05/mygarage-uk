"use client";

import {
  useCallback,
  useEffect,
  useMemo,
  useState,
} from "react";

import Link from "next/link";

import {
  useRouter,
} from "next/navigation";

import SiteHeader from "../../components/SiteHeader";

import {
  useAuth,
} from "../../contexts/AuthContext";

import {
  ApiError,
  addVehicleToGarage,
  clearVehicleCheckHistory,
  deleteVehicleCheckHistoryItem,
  getVehicleCheckHistory,
} from "../../lib/api";

import type {
  VehicleCheckHistoryItem,
} from "../../types/checkHistory";

import {
  formatRegistration,
} from "../vehicle-check/utils";

import styles from "./Checks.module.css";


function formatCheckedAt(
  value: string,
): string {
  const date =
    new Date(value);

  if (
    Number.isNaN(
      date.getTime(),
    )
  ) {
    return "Date unavailable";
  }

  const formatted =
    new Intl.DateTimeFormat(
      "en-GB",
      {
        day: "2-digit",
        month: "short",
        year: "2-digit",

        hour: "2-digit",
        minute: "2-digit",

        hour12: false,
      },
    ).format(date);

  return formatted.replace(
    ",",
    " ·",
  );
}


function vehicleName(
  item:
    VehicleCheckHistoryItem,
): string {
  const value = [
    item.make,
    item.model,
  ]
    .filter(Boolean)
    .join(" ");

  return (
    value
    || "Vehicle details unavailable"
  );
}


function vehicleMeta(
  item:
    VehicleCheckHistoryItem,
): string {
  return [
    item.year,
    item.fuel_type,
    item.colour,
  ]
    .filter(Boolean)
    .join(" · ");
}


export default function ChecksDashboard() {
  const router =
    useRouter();

  const {
    user,
    loading:
      authLoading,
  } =
    useAuth();

  const [
    checks,
    setChecks,
  ] =
    useState<
      VehicleCheckHistoryItem[]
    >([]);

  const [
    searchQuery,
    setSearchQuery,
  ] =
    useState("");

  const [
    loading,
    setLoading,
  ] =
    useState(true);

  const [
    addingId,
    setAddingId,
  ] =
    useState<
      number | null
    >(null);

  const [
    deletingId,
    setDeletingId,
  ] =
    useState<
      number | null
    >(null);

  const [
    clearing,
    setClearing,
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
    notice,
    setNotice,
  ] =
    useState<
      string | null
    >(null);


  const loadChecks =
    useCallback(
      async () => {
        try {
          const result =
            await getVehicleCheckHistory();

          setChecks(
            result,
          );

        } catch (
          caughtError
        ) {
          if (
            caughtError
            instanceof ApiError
          ) {
            setError(
              "We couldn’t load your checks. Please try again.",
            );

          } else {
            setError(
              "We couldn’t load your checks. Please try again.",
            );
          }

        } finally {
          setLoading(
            false,
          );
        }
      },
      [],
    );


  useEffect(() => {
    if (authLoading) {
      return;
    }

    if (!user) {
      router.replace(
        "/login",
      );

      return;
    }

    loadChecks();

  }, [
    authLoading,
    user,
    router,
    loadChecks,
  ]);


  const visibleChecks =
    useMemo(
      () => {
        const query =
          searchQuery
            .trim()
            .toLowerCase();

        if (!query) {
          return checks;
        }

        return checks.filter(
          (item) => {
            const searchable =
              [
                item.registration,
                item.make,
                item.model,
                item.year,
                item.fuel_type,
                item.colour,
              ]
                .filter(
                  Boolean,
                )
                .join(" ")
                .toLowerCase();

            return searchable.includes(
              query,
            );
          },
        );
      },
      [
        checks,
        searchQuery,
      ],
    );


  function handleCheckAgain(
    item:
      VehicleCheckHistoryItem,
  ) {
    router.push(
      (
        "/checks/"
        + encodeURIComponent(
          item.registration,
        )
      ),
    );
  }


  async function handleAddVehicle(
    item:
      VehicleCheckHistoryItem,
  ) {
    setAddingId(
      item.id,
    );

    setError(null);
    setNotice(null);

    try {
      await addVehicleToGarage(
        item.registration,
      );

      await loadChecks();

      setNotice(
        (
          `${formatRegistration(
            item.registration,
          )} added to My Vehicles.`
        ),
      );

    } catch (
      caughtError
    ) {
      if (
        caughtError
        instanceof ApiError
      ) {
        setError(
          "We couldn’t add this vehicle. Please try again.",
        );

      } else {
        setError(
          "We couldn’t add this vehicle. Please try again.",
        );
      }

    } finally {
      setAddingId(
        null,
      );
    }
  }


  async function handleDelete(
    item:
      VehicleCheckHistoryItem,
  ) {
    const confirmed =
      window.confirm(
        (
          `Remove ${formatRegistration(
            item.registration,
          )} from your recent checks?`
        ),
      );

    if (!confirmed) {
      return;
    }

    setDeletingId(
      item.id,
    );

    setError(null);
    setNotice(null);

    try {
      await deleteVehicleCheckHistoryItem(
        item.id,
      );

      setChecks(
        (
          current,
        ) =>
          current.filter(
            (check) =>
              check.id
              !== item.id,
          ),
      );

    } catch (
      caughtError
    ) {
      if (
        caughtError
        instanceof ApiError
      ) {
        setError(
          "We couldn’t remove this check. Please try again.",
        );

      } else {
        setError(
          "We couldn’t remove this check. Please try again.",
        );
      }

    } finally {
      setDeletingId(
        null,
      );
    }
  }


  async function handleClearAll() {
    const confirmed =
      window.confirm(
        (
          "Clear all recent checks?"
        ),
      );

    if (!confirmed) {
      return;
    }

    setClearing(true);
    setError(null);
    setNotice(null);

    try {
      await clearVehicleCheckHistory();

      setChecks([]);
      setSearchQuery("");

      setNotice(
        "Recent checks cleared.",
      );

    } catch (
      caughtError
    ) {
      if (
        caughtError
        instanceof ApiError
      ) {
        setError(
          "We couldn’t clear your checks. Please try again.",
        );

      } else {
        setError(
          "We couldn’t clear your checks. Please try again.",
        );
      }

    } finally {
      setClearing(
        false,
      );
    }
  }


  if (
    authLoading
    || !user
  ) {
    return (
      <div className="site-shell">
        <SiteHeader
          activePage="checks"
        />

        <main
          className={
            styles.page
          }
        >
          <div
            className={
              styles.inner
            }
          >
            <div
              className={
                styles.loading
              }
            >
              <div className="loader" />

              Loading your checks...
            </div>
          </div>
        </main>
      </div>
    );
  }


  return (
    <div className="site-shell">
      <SiteHeader
        activePage="checks"
      />

      <main
        className={
          styles.page
        }
      >
        <div
          className={
            styles.inner
          }
        >
          <div
            className={
              styles.heading
            }
          >
            <div>
              <span
                className={
                  styles.eyebrow
                }
              >
                Vehicle history
              </span>

              <h1>
                My Checks
              </h1>

              <p>
                Quickly return to vehicles
                you&apos;ve checked before and
                view their latest history.
              </p>
            </div>
          </div>

          {notice && (
            <div
              className={
                styles.notice
              }
            >
              {notice}
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

          {loading ? (
            <div
              className={
                styles.loading
              }
            >
              <div className="loader" />

              Loading your checks...
            </div>

          ) : checks.length === 0 ? (
            <div
              className={
                styles.empty
              }
            >
              <div
                className={
                  styles.emptyIcon
                }
              >
                ?
              </div>

              <h2>
                No recent checks yet
              </h2>

              <p>
                Vehicles you check will appear
                here so you can easily
                return to them later.
              </p>

              <Link
                className={
                  styles.checkVehicleLink
                }
                href="/"
              >
                Check a vehicle
              </Link>
            </div>

          ) : (
            <section
              className={
                styles.historyPanel
              }
            >
              <div
                className={
                  styles.toolbar
                }
              >
                <div
                  className={
                    styles.toolbarTitle
                  }
                >
                  <strong>
                    Recent checks
                  </strong>

                  <span>
                    {checks.length}{" "}
                    {checks.length === 1
                      ? "vehicle"
                      : "vehicles"}
                  </span>
                </div>

                <div
                  className={
                    styles.toolbarActions
                  }
                >
                  <div
                    className={
                      styles.searchWrap
                    }
                  >
                    <span
                      className={
                        styles.searchIcon
                      }
                      aria-hidden="true"
                    >
                      ⌕
                    </span>

                    <input
                      className={
                        styles.searchInput
                      }
                      type="search"
                      placeholder="Search registration, make or model"
                      value={
                        searchQuery
                      }
                      onChange={(
                        event,
                      ) =>
                        setSearchQuery(
                          event.target.value,
                        )
                      }
                      aria-label="Search vehicle checks"
                    />
                  </div>

                  <button
                    className={
                      styles.clearButton
                    }
                    type="button"
                    disabled={
                      clearing
                    }
                    onClick={
                      handleClearAll
                    }
                  >
                    {clearing
                      ? "Clearing..."
                      : "Clear history"}
                  </button>
                </div>
              </div>

              <div
                className={
                  styles.tableHeader
                }
                aria-hidden="true"
              >
                <span>
                  Registration
                </span>

                <span>
                  Vehicle
                </span>

                <span>
                  Last checked
                </span>

                <span>
                  Status
                </span>

                <span>
                  Actions
                </span>
              </div>

              {visibleChecks.length === 0 ? (
                <div
                  className={
                    styles.noResults
                  }
                >
                  No checks match
                  &ldquo;{searchQuery}&rdquo;.
                </div>

              ) : (
                <div
                  className={
                    styles.rows
                  }
                >
                  {visibleChecks.map(
                    (item) => (
                      <article
                        className={
                          styles.checkRow
                        }
                        key={
                          item.id
                        }
                      >
                        <div
                          className={
                            styles.registrationCell
                          }
                        >
                          <span
                            className={
                              styles.mobileLabel
                            }
                          >
                            Registration
                          </span>

                          <span
                            className={
                              styles.numberPlate
                            }
                          >
                            {formatRegistration(
                              item.registration,
                            )}
                          </span>
                        </div>

                        <div
                          className={
                            styles.vehicleCell
                          }
                        >
                          <span
                            className={
                              styles.mobileLabel
                            }
                          >
                            Vehicle
                          </span>

                          <strong>
                            {vehicleName(
                              item,
                            )}
                          </strong>

                          <span
                            className={
                              styles.vehicleMeta
                            }
                          >
                            {vehicleMeta(
                              item,
                            )
                              || "Details unavailable"}
                          </span>
                        </div>

                        <div
                          className={
                            styles.dateCell
                          }
                        >
                          <span
                            className={
                              styles.mobileLabel
                            }
                          >
                            Last checked
                          </span>

                          <span>
                            {formatCheckedAt(
                              item.last_checked_at,
                            )}
                          </span>
                        </div>

                        <div
                          className={
                            styles.statusCell
                          }
                        >
                          <span
                            className={
                              styles.mobileLabel
                            }
                          >
                            Status
                          </span>

                          <span
                            className={
                              item.in_garage
                                ? styles.savedBadge
                                : styles.unsavedBadge
                            }
                          >
                            {item.in_garage
                              ? "In My Vehicles"
                              : "Not in My Vehicles"}
                          </span>
                        </div>

                        <div
                          className={
                            styles.actions
                          }
                        >
                          <span
                            className={
                              styles.mobileLabel
                            }
                          >
                            Actions
                          </span>

                          <div
                            className={
                              styles.actionButtons
                            }
                          >
                            <button
                              className={
                                styles.textButton
                              }
                              type="button"
                              onClick={() =>
                                handleCheckAgain(
                                  item,
                                )
                              }
                            >
                              Check again
                            </button>

                            {item.in_garage
                              && item.garage_vehicle_id
                              ? (
                                <button
                                  className={
                                    styles.primaryButton
                                  }
                                  type="button"
                                  onClick={() =>
                                    router.push(
                                      (
                                        "/vehicles/"
                                        + item.garage_vehicle_id
                                      ),
                                    )
                                  }
                                >
                                  View
                                </button>
                              )
                              : (
                                <button
                                  className={
                                    styles.primaryButton
                                  }
                                  type="button"
                                  disabled={
                                    addingId
                                    === item.id
                                  }
                                  onClick={() =>
                                    handleAddVehicle(
                                      item,
                                    )
                                  }
                                >
                                  {addingId
                                    === item.id
                                    ? "Adding..."
                                    : "Add"}
                                </button>
                              )
                            }

                            <button
                              className={
                                styles.removeButton
                              }
                              type="button"
                              disabled={
                                deletingId
                                === item.id
                              }
                              onClick={() =>
                                handleDelete(
                                  item,
                                )
                              }
                              aria-label={
                                (
                                  "Remove "
                                  + formatRegistration(
                                    item.registration,
                                  )
                                  + " from recent checks"
                                )
                              }
                              title="Remove from recent checks"
                            >
                              {deletingId
                                === item.id
                                ? "..."
                                : "×"}
                            </button>
                          </div>
                        </div>
                      </article>
                    ),
                  )}
                </div>
              )}
            </section>
          )}
        </div>
      </main>

      <footer className="site-footer">
        <span>
          MyGarage UK
        </span>

        <span>
          Vehicle history and ownership,
          made simpler.
        </span>
      </footer>
    </div>
  );
}