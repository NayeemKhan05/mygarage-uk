"use client";

import {
  useCallback,
  useEffect,
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
  checkVehicle,
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
      date.getTime()
    )
  ) {
    return "Unknown";
  }

  return new Intl.DateTimeFormat(
    "en-GB",
    {
      day: "numeric",
      month: "short",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    },
  ).format(date);
}


function vehicleName(
  item: VehicleCheckHistoryItem,
): string {
  const name = [
    item.make,
    item.model,
  ]
    .filter(Boolean)
    .join(" ");

  return (
    name
    || "Vehicle details unavailable"
  );
}


function checkCountLabel(
  count: number,
): string {
  if (count === 1) {
    return "Checked once";
  }

  return `Checked ${count} times`;
}


export default function ChecksDashboard() {
  const router =
    useRouter();

  const {
    user,
    loading: authLoading,
  } = useAuth();

  const [
    checks,
    setChecks,
  ] =
    useState<
      VehicleCheckHistoryItem[]
    >([]);

  const [
    loading,
    setLoading,
  ] =
    useState(true);

  const [
    checkingId,
    setCheckingId,
  ] =
    useState<number | null>(
      null,
    );

  const [
    addingId,
    setAddingId,
  ] =
    useState<number | null>(
      null,
    );

  const [
    deletingId,
    setDeletingId,
  ] =
    useState<number | null>(
      null,
    );

  const [
    clearing,
    setClearing,
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
    notice,
    setNotice,
  ] =
    useState<string | null>(
      null,
    );


  const loadChecks =
    useCallback(
      async () => {
        setError(null);

        try {
          const result =
            await getVehicleCheckHistory();

          setChecks(
            result,
          );

        } catch (caughtError) {
          if (
            caughtError instanceof
            ApiError
          ) {
            setError(
              caughtError.message,
            );
          } else {
            setError(
              "We could not load your recent checks.",
            );
          }

        } finally {
          setLoading(false);
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
        "/login"
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


  async function handleCheckAgain(
    item: VehicleCheckHistoryItem,
  ) {
    setCheckingId(
      item.id,
    );

    setError(null);
    setNotice(null);

    try {
      await checkVehicle(
        item.registration,
      );

      await loadChecks();

      setNotice(
        (
          `${formatRegistration(
            item.registration,
          )} was checked against `
          + "the latest DVSA data."
        ),
      );

    } catch (caughtError) {
      if (
        caughtError instanceof
        ApiError
      ) {
        setError(
          caughtError.message,
        );
      } else {
        setError(
          "We could not check this vehicle.",
        );
      }

    } finally {
      setCheckingId(
        null,
      );
    }
  }


  async function handleAddVehicle(
    item: VehicleCheckHistoryItem,
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
          )} was added to My Vehicles.`
        ),
      );

    } catch (caughtError) {
      if (
        caughtError instanceof
        ApiError
      ) {
        setError(
          caughtError.message,
        );
      } else {
        setError(
          "We could not add this vehicle.",
        );
      }

    } finally {
      setAddingId(
        null,
      );
    }
  }


  async function handleDelete(
    item: VehicleCheckHistoryItem,
  ) {
    const confirmed =
      window.confirm(
        (
          `Remove ${formatRegistration(
            item.registration,
          )} from My Checks?`
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
        (current) =>
          current.filter(
            (check) =>
              check.id !== item.id,
          ),
      );

    } catch (caughtError) {
      if (
        caughtError instanceof
        ApiError
      ) {
        setError(
          caughtError.message,
        );
      } else {
        setError(
          "We could not remove this check.",
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
        "Clear your entire vehicle check history?",
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

      setNotice(
        "Your check history was cleared.",
      );

    } catch (caughtError) {
      if (
        caughtError instanceof
        ApiError
      ) {
        setError(
          caughtError.message,
        );
      } else {
        setError(
          "We could not clear your check history.",
        );
      }

    } finally {
      setClearing(false);
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

        <main className={styles.page}>
          <div className={styles.inner}>
            <div className={styles.loading}>
              <div className="loader" />

              Loading My Checks...
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

      <main className={styles.page}>
        <div className={styles.inner}>
          <div className={styles.heading}>
            <div>
              <span className={styles.eyebrow}>
                Recent lookups
              </span>

              <h1>
                My Checks
              </h1>

              <p>
                Registrations you have recently
                checked. Checking a vehicle here
                does not add it to My Vehicles
                unless you choose to save it.
              </p>
            </div>

            {checks.length > 0 && (
              <button
                className={styles.clearButton}
                type="button"
                disabled={clearing}
                onClick={handleClearAll}
              >
                {clearing
                  ? "Clearing..."
                  : "Clear history"}
              </button>
            )}
          </div>

          {notice && (
            <div className={styles.notice}>
              {notice}
            </div>
          )}

          {error && (
            <div
              className={styles.error}
              role="alert"
            >
              {error}
            </div>
          )}

          {loading ? (
            <div className={styles.loading}>
              <div className="loader" />

              Loading your vehicle checks...
            </div>

          ) : checks.length === 0 ? (
            <div className={styles.empty}>
              <div className={styles.emptyIcon}>
                ?
              </div>

              <h2>
                No vehicle checks yet
              </h2>

              <p>
                Search a registration while
                signed in and it will appear
                here automatically.
              </p>

              <Link
                className={styles.checkVehicleLink}
                href="/"
              >
                Check a vehicle
              </Link>
            </div>

          ) : (
            <div className={styles.grid}>
              {checks.map(
                (item) => (
                  <article
                    className={styles.card}
                    key={item.id}
                  >
                    <div className={styles.cardTop}>
                      <span className={styles.numberPlate}>
                        {formatRegistration(
                          item.registration,
                        )}
                      </span>

                      <span
                        className={
                          item.in_garage
                            ? styles.garageBadge
                            : styles.unsavedBadge
                        }
                      >
                        {item.in_garage
                          ? "In My Vehicles"
                          : "Not saved"}
                      </span>
                    </div>

                    <h2 className={styles.vehicleName}>
                      {vehicleName(
                        item,
                      )}
                    </h2>

                    <div className={styles.vehicleMeta}>
                      {item.year && (
                        <span>
                          {item.year}
                        </span>
                      )}

                      {item.fuel_type && (
                        <span>
                          {item.fuel_type}
                        </span>
                      )}

                      {item.colour && (
                        <span>
                          {item.colour}
                        </span>
                      )}
                    </div>

                    <div className={styles.checkDetails}>
                      <div className={styles.detail}>
                        <span>
                          Last checked
                        </span>

                        <strong>
                          {formatCheckedAt(
                            item.last_checked_at,
                          )}
                        </strong>
                      </div>

                      <div className={styles.detail}>
                        <span>
                          Check history
                        </span>

                        <strong>
                          {checkCountLabel(
                            item.check_count,
                          )}
                        </strong>
                      </div>
                    </div>

                    <div className={styles.actions}>
                      <button
                        className={styles.secondaryButton}
                        type="button"
                        disabled={
                          checkingId
                          !== null
                        }
                        onClick={() =>
                          handleCheckAgain(
                            item,
                          )
                        }
                      >
                        {checkingId === item.id
                          ? "Checking..."
                          : "Check again"}
                      </button>

                      {item.in_garage
                        && item.garage_vehicle_id
                        ? (
                          <button
                            className={styles.primaryButton}
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
                            View vehicle
                          </button>
                        )
                        : (
                          <button
                            className={styles.primaryButton}
                            type="button"
                            disabled={
                              addingId
                              !== null
                            }
                            onClick={() =>
                              handleAddVehicle(
                                item,
                              )
                            }
                          >
                            {addingId === item.id
                              ? "Adding..."
                              : "Add to My Vehicles"}
                          </button>
                        )
                      }

                      <button
                        className={styles.dangerButton}
                        type="button"
                        disabled={
                          deletingId
                          !== null
                        }
                        onClick={() =>
                          handleDelete(
                            item,
                          )
                        }
                      >
                        {deletingId === item.id
                          ? "Removing..."
                          : "Remove"}
                      </button>
                    </div>
                  </article>
                ),
              )}
            </div>
          )}
        </div>
      </main>

      <footer className="site-footer">
        <span>
          MyGarage UK
        </span>

        <span>
          Built for UK motorists.
        </span>
      </footer>
    </div>
  );
}