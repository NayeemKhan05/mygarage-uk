"use client";

import {
  useEffect,
  useState,
} from "react";

import Link from "next/link";

import SiteHeader from "../../components/SiteHeader";

import {
  ApiError,
  getGarageVehicles,
  getVehicleMotHistory,
} from "../../lib/api";

import type {
  GarageVehicle,
  MotTest,
} from "../../types/vehicle";

import VehicleCard from "./VehicleCard";

import styles from "./Vehicles.module.css";


interface VehicleSummary {
  vehicle: GarageVehicle;
  motHistory: MotTest[];
}


export default function VehiclesDashboard() {
  const [
    vehicles,
    setVehicles,
  ] =
    useState<VehicleSummary[]>([]);

  const [
    loading,
    setLoading,
  ] =
    useState(true);

  const [
    error,
    setError,
  ] =
    useState<string | null>(
      null,
    );


  useEffect(() => {
    let cancelled = false;

    async function loadVehicles() {
      setLoading(true);
      setError(null);

      try {
        const savedVehicles =
          await getGarageVehicles();

        /*
         * The existing vehicles endpoint only returns the basic car
         * details, so fetch each stored MOT history for the summary cards.
         */
        const summaries =
          await Promise.all(
            savedVehicles.map(
              async (
                vehicle,
              ): Promise<VehicleSummary> => {
                try {
                  const motHistory =
                    await getVehicleMotHistory(
                      vehicle.id,
                    );

                  return {
                    vehicle,
                    motHistory,
                  };
                } catch {
                  // One bad history request should not hide every car.
                  return {
                    vehicle,
                    motHistory: [],
                  };
                }
              },
            ),
          );

        if (!cancelled) {
          setVehicles(
            summaries,
          );
        }
      } catch (caughtError) {
        if (cancelled) {
          return;
        }

        if (
          caughtError instanceof
          ApiError
        ) {
          setError(
            caughtError.message,
          );
        } else {
          setError(
            "We could not load your vehicles. Check that the backend is running and try again.",
          );
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    loadVehicles();

    return () => {
      cancelled = true;
    };
  }, []);


  return (
    <div className="site-shell">
      <SiteHeader
        activePage="vehicles"
      />

      <main className={styles.page}>
        <div className={styles.pageInner}>
          <div className={styles.pageHeading}>
            <div>
              <span className={styles.eyebrow}>
                My Vehicles
              </span>

              <h1>
                Your cars, all in
                one place.
              </h1>

              <p>
                Keep an eye on MOT
                history, mileage and
                vehicle information for
                every car you&apos;ve
                saved.
              </p>
            </div>

            <Link
              className={styles.addVehicleButton}
              href="/"
            >
              + Add another vehicle
            </Link>
          </div>

          {loading && (
            <div className={styles.loadingState}>
              <div className="loader" />

              <div>
                <strong>
                  Loading your vehicles
                </strong>

                <span>
                  Getting the latest
                  saved details.
                </span>
              </div>
            </div>
          )}

          {!loading && error && (
            <div
              className={styles.errorState}
              role="alert"
            >
              <strong>
                Couldn&apos;t load My Vehicles
              </strong>

              <p>
                {error}
              </p>
            </div>
          )}

          {!loading &&
            !error &&
            vehicles.length === 0 && (
              <div className={styles.emptyState}>
                <div className={styles.emptyIcon}>
                  MG
                </div>

                <span className={styles.eyebrow}>
                  Nothing here yet
                </span>

                <h2>
                  Add your first vehicle.
                </h2>

                <p>
                  Check a registration from
                  the homepage, then choose
                  Add to My Vehicles to keep
                  it here.
                </p>

                <Link
                  className={styles.primaryLink}
                  href="/"
                >
                  Check a vehicle
                </Link>
              </div>
            )}

          {!loading &&
            !error &&
            vehicles.length > 0 && (
              <>
                <div className={styles.vehicleCount}>
                  <strong>
                    {vehicles.length}
                  </strong>

                  <span>
                    {vehicles.length === 1
                      ? "vehicle saved"
                      : "vehicles saved"}
                  </span>
                </div>

                <div className={styles.vehicleGrid}>
                  {vehicles.map(
                    ({
                      vehicle,
                      motHistory,
                    }) => (
                      <VehicleCard
                        key={vehicle.id}
                        vehicle={vehicle}
                        motHistory={motHistory}
                      />
                    ),
                  )}
                </div>
              </>
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