import Link from "next/link";

import type {
  GarageVehicle,
  MotTest,
} from "../../types/vehicle";

import {
  formatDate,
  formatMileage,
  formatRegistration,
  getCurrentMot,
  getLatestMileage,
} from "../vehicle-check/utils";

import styles from "./Vehicles.module.css";


interface VehicleCardProps {
  vehicle: GarageVehicle;
  motHistory: MotTest[];
}


export default function VehicleCard({
  vehicle,
  motHistory,
}: VehicleCardProps) {
  const motStatus =
    getCurrentMot(motHistory);

  const mileage =
    getLatestMileage(motHistory);

  const toneClass =
    motStatus.tone === "good"
      ? styles.good
      : motStatus.tone === "warning"
        ? styles.warning
        : motStatus.tone === "bad"
          ? styles.bad
          : styles.neutral;

  return (
    <article className={styles.vehicleCard}>
      <div className={styles.cardTop}>
        <div>
          <div className="number-plate">
            {formatRegistration(
              vehicle.registration,
            )}
          </div>

          <h2 className={styles.vehicleName}>
            {vehicle.make}{" "}
            {vehicle.model}
          </h2>

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
      </div>

      <div className={styles.cardStats}>
        <div className={styles.cardMetric}>
          <span className={styles.metricLabel}>
            MOT status
          </span>

          <strong
            className={`${styles.motStatus} ${toneClass}`}
          >
            <span className={styles.statusDot} />

            {motStatus.label}
          </strong>

          <span className={styles.metricDetail}>
            {motStatus.expiryDate
              ? motStatus.timeRemainingLabel
              : "No MOT expiry available"}
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

        <div className={styles.cardMetric}>
          <span className={styles.metricLabel}>
            Latest mileage
          </span>

          <strong>
            {formatMileage(
              mileage.value,
              mileage.unit,
            )}
          </strong>

          <span className={styles.metricDetail}>
            {motHistory.length === 0
              ? "No MOT records saved"
              : `${motHistory.length} MOT ${
                  motHistory.length === 1
                    ? "record"
                    : "records"
                }`}
          </span>
        </div>
      </div>

      <div className={styles.cardFooter}>
        <Link
          className={styles.viewVehicleButton}
          href={`/vehicles/${vehicle.id}`}
        >
          View vehicle
          <span aria-hidden="true">
            →
          </span>
        </Link>
      </div>
    </article>
  );
}