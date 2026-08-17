"use client";

import {
  useEffect,
  useState,
} from "react";

import Link from "next/link";

import {
  useParams,
  useRouter,
} from "next/navigation";

import SiteHeader from "../../components/SiteHeader";

import {
  useAuth,
} from "../../contexts/AuthContext";

import {
  ApiError,
  deleteGarageVehicle,
  getGarageVehicle,
  getVehicleMotHistory,
  refreshVehicleMotHistory,
} from "../../lib/api";

import type {
  GarageVehicle,
  MotTest,
} from "../../types/vehicle";

import MileageChart from "../vehicle-check/MileageChart";
import MotHistory from "../vehicle-check/MotHistory";

import {
  formatDate,
  formatMileage,
  formatRegistration,
  getCurrentMot,
  getLatestMileage,
  sortMotTests,
} from "../vehicle-check/utils";

import MaintenanceTracker from "./MaintenanceTracker";
import ServiceHistory from "./ServiceHistory";

import styles from "./Vehicles.module.css";


export default function VehicleDetails() {
  const params =
    useParams<{
      id: string;
    }>();

  const router =
    useRouter();

  const {
    user,
    loading: authLoading,
  } = useAuth();

  const vehicleId =
    Number(params.id);

  const [
    vehicle,
    setVehicle,
  ] =
    useState<GarageVehicle | null>(
      null,
    );

  const [
    motHistory,
    setMotHistory,
  ] =
    useState<MotTest[]>([]);

  const [
    loading,
    setLoading,
  ] =
    useState(true);

  const [
    refreshing,
    setRefreshing,
  ] =
    useState(false);

  const [
    deleting,
    setDeleting,
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

    let cancelled = false;


    async function loadVehicle() {
      if (
        !Number.isInteger(
          vehicleId,
        )
        || vehicleId <= 0
      ) {
        setError(
          "This vehicle link is invalid.",
        );

        setLoading(false);

        return;
      }

      setLoading(true);
      setError(null);

      try {
        const [
          vehicleResult,
          motHistoryResult,
        ] =
          await Promise.all([
            getGarageVehicle(
              vehicleId,
            ),

            getVehicleMotHistory(
              vehicleId,
            ),
          ]);

        if (!cancelled) {
          setVehicle(
            vehicleResult,
          );

          setMotHistory(
            motHistoryResult,
          );
        }

      } catch (caughtError) {
        if (cancelled) {
          return;
        }

        if (
          caughtError instanceof
            ApiError
          && caughtError.status === 404
        ) {
          setError(
            "This vehicle could not be found in My Vehicles.",
          );

        } else if (
          caughtError instanceof
          ApiError
        ) {
          setError(
            caughtError.message,
          );

        } else {
          setError(
            "We could not load this vehicle. Please try again.",
          );
        }

      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }


    loadVehicle();

    return () => {
      cancelled = true;
    };

  }, [
    authLoading,
    user,
    router,
    vehicleId,
  ]);


  async function handleRefresh() {
    if (!vehicle) {
      return;
    }

    setRefreshing(true);
    setError(null);
    setNotice(null);

    try {
      const result =
        await refreshVehicleMotHistory(
          vehicle.id,
        );

      const updatedHistory =
        await getVehicleMotHistory(
          vehicle.id,
        );

      setMotHistory(
        updatedHistory,
      );

      if (
        result.mot_tests_saved ===
        0
      ) {
        setNotice(
          "MOT history is already up to date.",
        );

      } else {
        setNotice(
          `${result.mot_tests_saved} new MOT ${
            result.mot_tests_saved === 1
              ? "test was"
              : "tests were"
          } added.`,
        );
      }

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
          "We could not refresh the MOT history. Please try again.",
        );
      }

    } finally {
      setRefreshing(false);
    }
  }


  async function handleDelete() {
    if (!vehicle) {
      return;
    }

    const confirmed =
      window.confirm(
        `Remove ${formatRegistration(
          vehicle.registration,
        )} from My Vehicles?`,
      );

    if (!confirmed) {
      return;
    }

    setDeleting(true);
    setError(null);

    try {
      await deleteGarageVehicle(
        vehicle.id,
      );

      router.push(
        "/vehicles",
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
          "We could not remove this vehicle. Please try again.",
        );
      }

      setDeleting(false);
    }
  }


  if (
    authLoading
    || !user
    || loading
  ) {
    return (
      <div className="site-shell">
        <SiteHeader
          activePage="vehicles"
        />

        <main className={styles.page}>
          <div className={styles.pageInner}>
            <div className={styles.loadingState}>
              <div className="loader" />

              <div>
                <strong>
                  Loading vehicle
                </strong>

                <span>
                  Getting your saved MOT
                  history and vehicle details.
                </span>
              </div>
            </div>
          </div>
        </main>
      </div>
    );
  }


  if (
    error
    && !vehicle
  ) {
    return (
      <div className="site-shell">
        <SiteHeader
          activePage="vehicles"
        />

        <main className={styles.page}>
          <div className={styles.pageInner}>
            <Link
              className={styles.backLink}
              href="/vehicles"
            >
              ← Back to My Vehicles
            </Link>

            <div className={styles.errorState}>
              <strong>
                Vehicle unavailable
              </strong>

              <p>
                {error}
              </p>
            </div>
          </div>
        </main>
      </div>
    );
  }


  if (!vehicle) {
    return null;
  }


  const motStatus =
    getCurrentMot(
      motHistory,
    );

  const mileage =
    getLatestMileage(
      motHistory,
    );

  const latestMot =
    sortMotTests(
      motHistory,
    )[0];

  const toneClass =
    motStatus.tone === "good"
      ? styles.good
      : motStatus.tone === "warning"
        ? styles.warning
        : motStatus.tone === "bad"
          ? styles.bad
          : styles.neutral;


  return (
    <div className="site-shell">
      <SiteHeader
        activePage="vehicles"
      />

      <main className={styles.page}>
        <div className={styles.detailsInner}>
          <Link
            className={styles.backLink}
            href="/vehicles"
          >
            ← Back to My Vehicles
          </Link>

          <div className={styles.vehicleHero}>
            <div>
              <div className="number-plate">
                {formatRegistration(
                  vehicle.registration,
                )}
              </div>

              <h1>
                {vehicle.make}{" "}
                {vehicle.model}
              </h1>

              <div className={styles.vehicleDetails}>
                {vehicle.year && (
                  <span>
                    {vehicle.year}
                  </span>
                )}

                {vehicle.fuel_type && (
                  <span>
                    {vehicle.fuel_type}
                  </span>
                )}

                {vehicle.engine_size && (
                  <span>
                    {vehicle.engine_size.toLocaleString(
                      "en-GB",
                    )}{" "}
                    cc
                  </span>
                )}

                {vehicle.colour && (
                  <span>
                    {vehicle.colour}
                  </span>
                )}
              </div>
            </div>

            <div className={styles.vehicleActions}>
              <button
                className={styles.refreshButton}
                type="button"
                disabled={refreshing}
                onClick={handleRefresh}
              >
                {refreshing
                  ? "Refreshing..."
                  : "Refresh MOT data"}
              </button>

              <button
                className={styles.deleteButton}
                type="button"
                disabled={deleting}
                onClick={handleDelete}
              >
                {deleting
                  ? "Removing..."
                  : "Remove vehicle"}
              </button>
            </div>
          </div>

          {notice && (
            <div className={styles.successMessage}>
              {notice}
            </div>
          )}

          {error && (
            <div
              className={styles.inlineError}
              role="alert"
            >
              {error}
            </div>
          )}

          <div className={styles.detailsStats}>
            <div className={styles.summaryCard}>
              <span className={styles.metricLabel}>
                Current MOT
              </span>

              <strong
                className={`${styles.motStatus} ${toneClass}`}
              >
                <span className={styles.statusDot} />

                {motStatus.label}
              </strong>

              <span
                className={`${styles.countdown} ${toneClass}`}
              >
                {motStatus.timeRemainingLabel}
              </span>

              {motStatus.expiryDate && (
                <span className={styles.metricSubtle}>
                  Until{" "}
                  {formatDate(
                    motStatus.expiryDate,
                  )}
                </span>
              )}
            </div>

            <div className={styles.summaryCard}>
              <span className={styles.metricLabel}>
                Latest mileage
              </span>

              <strong className={styles.bigValue}>
                {formatMileage(
                  mileage.value,
                  mileage.unit,
                )}
              </strong>

              <span className={styles.metricSubtle}>
                {latestMot
                  ? `Recorded ${formatDate(
                      latestMot.completed_at,
                    )}`
                  : "No mileage recorded"}
              </span>
            </div>

            <div className={styles.summaryCard}>
              <span className={styles.metricLabel}>
                MOT records
              </span>

              <strong className={styles.bigValue}>
                {motHistory.length}
              </strong>

              <span className={styles.metricSubtle}>
                Tests saved
              </span>
            </div>
          </div>

          <ServiceHistory
            vehicleId={vehicle.id}
          />

          <MaintenanceTracker
            vehicleId={vehicle.id}
          />

          {latestMot && (
            <section className="panel">
              <div className="section-heading">
                <div>
                  <span className="eyebrow">
                    Latest test
                  </span>

                  <h2>
                    Latest MOT
                  </h2>
                </div>

                <span
                  className={
                    latestMot.test_result
                      ?.toUpperCase()
                    === "PASSED"
                      ? "result-badge passed"
                      : "result-badge failed"
                  }
                >
                  {latestMot.test_result
                    ?? "Unknown"}
                </span>
              </div>

              <div className="latest-mot-grid">
                <div>
                  <span>
                    Date
                  </span>

                  <strong>
                    {formatDate(
                      latestMot.completed_at,
                    )}
                  </strong>
                </div>

                <div>
                  <span>
                    Mileage
                  </span>

                  <strong>
                    {formatMileage(
                      latestMot.odometer_value,
                      latestMot.odometer_unit,
                    )}
                  </strong>
                </div>

                <div>
                  <span>
                    Recorded items
                  </span>

                  <strong>
                    {latestMot.defects.length}
                  </strong>
                </div>
              </div>
            </section>
          )}

          <MileageChart
            motTests={
              motHistory
            }
          />

          <MotHistory
            motTests={
              motHistory
            }
          />

          <p className="data-note">
            MOT information is saved from DVSA
            records. Service and maintenance
            information is private to your
            MyGarage account.
          </p>
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