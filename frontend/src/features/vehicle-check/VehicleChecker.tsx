"use client";

import {
  FormEvent,
  useState,
} from "react";

import {
  useRouter,
} from "next/navigation";

import SiteHeader from "../../components/SiteHeader";

import {
  useAuth,
} from "../../contexts/AuthContext";

import {
  addVehicleToGarage,
  ApiError,
  checkVehicle,
} from "../../lib/api";

import type {
  VehicleCheckResponse,
} from "../../types/vehicle";

import MileageChart from "./MileageChart";
import MotHistory from "./MotHistory";

import {
  formatDate,
  formatMileage,
  formatRegistration,
  getCurrentMot,
  getLatestMileage,
  sortMotTests,
} from "./utils";


export default function VehicleChecker() {
  const router =
    useRouter();

  const {
    user,
  } = useAuth();

  const [
    registration,
    setRegistration,
  ] = useState("");

  const [
    vehicle,
    setVehicle,
  ] =
    useState<VehicleCheckResponse | null>(
      null,
    );

  const [
    loading,
    setLoading,
  ] =
    useState(false);

  const [
    addingToGarage,
    setAddingToGarage,
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


  async function handleSearch(
    event:
      FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault();

    if (!registration.trim()) {
      setError(
        "Enter a registration number first.",
      );

      return;
    }

    setLoading(true);
    setError(null);
    setNotice(null);
    setVehicle(null);

    try {
      const result =
        await checkVehicle(
          registration,
        );

      setVehicle(result);

      setRegistration(
        formatRegistration(
          result.registration,
        ),
      );
    } catch (caughtError) {
      if (
        caughtError instanceof
        ApiError
      ) {
        if (
          caughtError.status === 404
        ) {
          setError(
            "We could not find a vehicle with that registration.",
          );
        } else {
          setError(
            caughtError.message,
          );
        }
      } else {
        setError(
          "We could not connect to MyGarage. Check that the backend is running and try again.",
        );
      }
    } finally {
      setLoading(false);
    }
  }


  async function handleAddToGarage() {
    if (!vehicle) {
      return;
    }

    if (!user) {
      router.push(
        "/login"
      );

      return;
    }

    if (vehicle.in_garage) {
      return;
    }

    setAddingToGarage(true);
    setError(null);
    setNotice(null);

    try {
      const result =
        await addVehicleToGarage(
          vehicle.registration,
        );

      setVehicle({
        ...vehicle,
        in_garage: true,
        garage_vehicle_id:
          result.vehicle.id,
      });

      setNotice(
        `Added to My Vehicles. ${result.mot_tests_saved} MOT ${
          result.mot_tests_saved === 1
            ? "test was"
            : "tests were"
        } newly saved.`,
      );
    } catch (caughtError) {
      if (
        caughtError instanceof
          ApiError &&
        caughtError.status === 409
      ) {
        setVehicle({
          ...vehicle,
          in_garage: true,
        });

        setNotice(
          "This vehicle is already in My Vehicles.",
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
          "We could not add the vehicle to My Vehicles. Please try again.",
        );
      }
    } finally {
      setAddingToGarage(false);
    }
  }


  const motStatus =
    vehicle
      ? getCurrentMot(
          vehicle.mot_tests,
        )
      : null;

  const mileage =
    vehicle
      ? getLatestMileage(
          vehicle.mot_tests,
        )
      : null;

  const latestMot =
    vehicle
      ? sortMotTests(
          vehicle.mot_tests,
        )[0]
      : null;


  return (
    <div className="site-shell">
      <SiteHeader
        activePage="home"
      />

      <main>
        <section className="hero">
          <div className="hero-inner">
            <span className="hero-eyebrow">
              UK vehicle history
            </span>

            <h1>
              Know what&apos;s happened
              <br />
              to a car before you rely on it.
            </h1>

            <p className="hero-copy">
              Check MOT history, mileage and
              recorded defects from one
              registration number.
            </p>

            <form
              className="registration-search"
              onSubmit={handleSearch}
            >
              <div className="registration-field">
                <span
                  className="plate-strip"
                  aria-hidden="true"
                >
                  UK
                </span>

                <input
                  type="text"
                  value={registration}
                  onChange={(event) =>
                    setRegistration(
                      event.target.value
                        .toUpperCase(),
                    )
                  }
                  placeholder="ENTER REG"
                  maxLength={9}
                  autoComplete="off"
                  spellCheck={false}
                  aria-label="Vehicle registration"
                />
              </div>

              <button
                className="primary-button search-button"
                type="submit"
                disabled={loading}
              >
                {loading
                  ? "Checking..."
                  : "Check vehicle"}
              </button>
            </form>

            <p className="search-note">
              Checking a vehicle does not add
              it to My Vehicles.
            </p>

            {error && (
              <div
                className="message error-message"
                role="alert"
              >
                {error}
              </div>
            )}
          </div>
        </section>

        {!vehicle &&
          !loading && (
            <section className="features">
              <div className="features-inner">
                <div className="feature-card">
                  <span className="feature-number">
                    01
                  </span>

                  <h2>
                    MOT history
                  </h2>

                  <p>
                    See previous tests,
                    failures, advisories and
                    defects in one timeline.
                  </p>
                </div>

                <div className="feature-card">
                  <span className="feature-number">
                    02
                  </span>

                  <h2>
                    Mileage
                  </h2>

                  <p>
                    Follow recorded odometer
                    readings across the life
                    of the vehicle.
                  </p>
                </div>

                <div className="feature-card">
                  <span className="feature-number">
                    03
                  </span>

                  <h2>
                    My Vehicles
                  </h2>

                  <p>
                    Sign in and save your own
                    vehicles so their history
                    is always easy to find.
                  </p>
                </div>
              </div>
            </section>
          )}

        {loading && (
          <section className="results">
            <div className="results-inner">
              <div className="loading-panel">
                <div className="loader" />

                <div>
                  <strong>
                    Checking DVSA records
                  </strong>

                  <span>
                    Pulling together the
                    vehicle&apos;s MOT history.
                  </span>
                </div>
              </div>
            </div>
          </section>
        )}

        {vehicle &&
          motStatus &&
          mileage && (
            <section className="results">
              <div className="results-inner">
                <div className="vehicle-header">
                  <div>
                    <div className="number-plate">
                      {formatRegistration(
                        vehicle.registration,
                      )}
                    </div>

                    <h2 className="vehicle-title">
                      {vehicle.make}{" "}
                      {vehicle.model}
                    </h2>

                    <div className="vehicle-details">
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

                  <div className="garage-action">
                    <button
                      className={
                        vehicle.in_garage
                          ? "garage-button in-garage"
                          : "garage-button"
                      }
                      type="button"
                      disabled={
                        vehicle.in_garage ||
                        addingToGarage
                      }
                      onClick={
                        handleAddToGarage
                      }
                    >
                      {vehicle.in_garage
                        ? "In My Vehicles"
                        : !user
                          ? "Sign in to add"
                          : addingToGarage
                            ? "Adding..."
                            : "Add to My Vehicles"}
                    </button>

                    {vehicle.in_garage && (
                      <span className="garage-caption">
                        Saved to your account
                      </span>
                    )}
                  </div>
                </div>

                {notice && (
                  <div className="message success-message">
                    {notice}
                  </div>
                )}

                {error && (
                  <div
                    className="message error-message"
                    role="alert"
                  >
                    {error}
                  </div>
                )}

                <div className="stats-grid">
                  <div className="stat-card">
                    <span className="stat-label">
                      Current MOT
                    </span>

                    <strong
                      className={`status-text ${motStatus.tone}`}
                    >
                      <span className="status-dot" />

                      {motStatus.label}
                    </strong>

                    {motStatus.expiryDate ? (
                      <div className="mot-expiry-summary">
                        <span
                          className={`mot-countdown ${motStatus.tone}`}
                        >
                          {motStatus.timeRemainingLabel}
                        </span>

                        <span className="stat-detail">
                          Until{" "}
                          {formatDate(
                            motStatus.expiryDate,
                          )}
                        </span>
                      </div>
                    ) : (
                      <span className="stat-detail">
                        No expiry available
                      </span>
                    )}
                  </div>

                  <div className="stat-card">
                    <span className="stat-label">
                      Latest mileage
                    </span>

                    <strong>
                      {formatMileage(
                        mileage.value,
                        mileage.unit,
                      )}
                    </strong>

                    <span className="stat-detail">
                      {latestMot
                        ? `Recorded ${formatDate(
                            latestMot.completed_at,
                          )}`
                        : "No reading available"}
                    </span>
                  </div>

                  <div className="stat-card">
                    <span className="stat-label">
                      MOT records
                    </span>

                    <strong>
                      {vehicle.mot_tests_found}
                    </strong>

                    <span className="stat-detail">
                      Tests found
                    </span>
                  </div>
                </div>

                {latestMot && (
                  <section className="latest-mot panel">
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
                            ?.toUpperCase() ===
                          "PASSED"
                            ? "result-badge passed"
                            : "result-badge failed"
                        }
                      >
                        {latestMot.test_result ??
                          "Unknown"}
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
                    vehicle.mot_tests
                  }
                />

                <MotHistory
                  motTests={
                    vehicle.mot_tests
                  }
                />

                <p className="data-note">
                  MOT information is retrieved
                  from DVSA records. A vehicle
                  check is only saved when you
                  choose to add it to My Vehicles.
                </p>
              </div>
            </section>
          )}
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