"use client";

import {
  useCallback,
  useEffect,
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
  ApiError,
  dismissReminder,
  getReminderSettings,
  getReminders,
  restoreDismissedReminders,
  updateReminderSettings,
} from "../../lib/api";

import type {
  Reminder,
  ReminderSettings,
} from "../../types/reminder";

import {
  formatRegistration,
} from "../vehicle-check/utils";

import styles from "./Reminders.module.css";


function vehicleName(
  reminder: Reminder,
): string {
  const name = [
    reminder.make,
    reminder.model,
  ]
    .filter(Boolean)
    .join(" ");

  return (
    name
    || "Vehicle"
  );
}


export default function RemindersDashboard() {
  const router =
    useRouter();

  const {
    user,
    loading:
      authLoading,
  } =
    useAuth();

  const [
    reminders,
    setReminders,
  ] =
    useState<
      Reminder[]
    >([]);

  const [
    settings,
    setSettings,
  ] =
    useState<
      ReminderSettings | null
    >(null);

  const [
    loading,
    setLoading,
  ] =
    useState(true);

  const [
    saving,
    setSaving,
  ] =
    useState(false);

  const [
    dismissingKey,
    setDismissingKey,
  ] =
    useState<
      string | null
    >(null);

  const [
    restoring,
    setRestoring,
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


  const loadData =
    useCallback(
      async () => {
        setError(null);

        try {
          const [
            remindersResult,
            settingsResult,
          ] =
            await Promise.all([
              getReminders(),
              getReminderSettings(),
            ]);

          setReminders(
            remindersResult,
          );

          setSettings(
            settingsResult,
          );

        } catch (caughtError) {
          if (
            caughtError
            instanceof ApiError
          ) {
            setError(
              (
                "We couldn’t load your "
                + "reminders right now. "
                + "Please try again."
              ),
            );

          } else {
            setError(
              (
                "We couldn’t load your "
                + "reminders right now. "
                + "Please try again."
              ),
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

    void loadData();

  }, [
    authLoading,
    user,
    router,
    loadData,
  ]);


  async function handleSaveSettings() {
    if (!settings) {
      return;
    }

    setSaving(true);
    setError(null);
    setNotice(null);

    try {
      const updated =
        await updateReminderSettings({
          mot_enabled:
            settings.mot_enabled,

          maintenance_enabled:
            settings.maintenance_enabled,

          due_soon_days:
            settings.due_soon_days,

          due_soon_miles:
            settings.due_soon_miles,
        });

      setSettings(
        updated,
      );

      await loadData();

      setNotice(
        "Reminder settings updated.",
      );

    } catch (caughtError) {
      if (
        caughtError
        instanceof ApiError
      ) {
        setError(
          (
            "We couldn’t save your "
            + "reminder settings. "
            + "Please try again."
          ),
        );

      } else {
        setError(
          (
            "We couldn’t save your "
            + "reminder settings. "
            + "Please try again."
          ),
        );
      }

    } finally {
      setSaving(
        false,
      );
    }
  }


  async function handleDismiss(
    reminder: Reminder,
  ) {
    setDismissingKey(
      reminder.reminder_key,
    );

    setError(null);
    setNotice(null);

    try {
      await dismissReminder(
        reminder.reminder_key,
      );

      setReminders(
        (current) =>
          current.filter(
            (item) =>
              item.reminder_key
              !== reminder.reminder_key,
          ),
      );

    } catch (caughtError) {
      if (
        caughtError
        instanceof ApiError
      ) {
        setError(
          (
            "We couldn’t dismiss this "
            + "reminder. Please try again."
          ),
        );

      } else {
        setError(
          (
            "We couldn’t dismiss this "
            + "reminder. Please try again."
          ),
        );
      }

    } finally {
      setDismissingKey(
        null,
      );
    }
  }


  async function handleRestore() {
    setRestoring(true);
    setError(null);
    setNotice(null);

    try {
      await restoreDismissedReminders();

      await loadData();

      setNotice(
        "Dismissed reminders restored.",
      );

    } catch (caughtError) {
      if (
        caughtError
        instanceof ApiError
      ) {
        setError(
          (
            "We couldn’t restore your "
            + "dismissed reminders. "
            + "Please try again."
          ),
        );

      } else {
        setError(
          (
            "We couldn’t restore your "
            + "dismissed reminders. "
            + "Please try again."
          ),
        );
      }

    } finally {
      setRestoring(
        false,
      );
    }
  }


  const urgent =
    reminders.filter(
      (reminder) =>
        reminder.severity
        === "urgent",
    ).length;

  const warning =
    reminders.filter(
      (reminder) =>
        reminder.severity
        === "warning",
    ).length;


  if (
    authLoading
    || !user
  ) {
    return (
      <div className="site-shell">
        <SiteHeader
          activePage="reminders"
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
              Loading reminders...
            </div>
          </div>
        </main>
      </div>
    );
  }


  return (
    <div className="site-shell">
      <SiteHeader
        activePage="reminders"
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
            <span
              className={
                styles.eyebrow
              }
            >
              Vehicle alerts
            </span>

            <h1>
              Reminders
            </h1>

            <p>
              Stay ahead of upcoming MOT
              and maintenance deadlines.
            </p>
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
              Loading your reminders...
            </div>

          ) : (
            <>
              <div
                className={
                  styles.summaryGrid
                }
              >
                <div
                  className={
                    styles.summaryCard
                  }
                >
                  <span>
                    Active reminders
                  </span>

                  <strong>
                    {reminders.length}
                  </strong>
                </div>

                <div
                  className={
                    styles.summaryCard
                  }
                >
                  <span>
                    Urgent
                  </span>

                  <strong
                    className={
                      styles.urgentNumber
                    }
                  >
                    {urgent}
                  </strong>
                </div>

                <div
                  className={
                    styles.summaryCard
                  }
                >
                  <span>
                    Due soon
                  </span>

                  <strong
                    className={
                      styles.warningNumber
                    }
                  >
                    {warning}
                  </strong>
                </div>
              </div>

              {settings && (
                <section
                  className={
                    styles.panel
                  }
                >
                  <div
                    className={
                      styles.panelHeader
                    }
                  >
                    <div>
                      <h2>
                        Reminder settings
                      </h2>

                      <p>
                        Choose which reminders
                        you want to receive.
                      </p>
                    </div>
                  </div>

                  <div
                    className={
                      styles.settingsGrid
                    }
                  >
                    <label
                      className={
                        styles.toggleRow
                      }
                    >
                      <div
                        className={
                          styles.toggleText
                        }
                      >
                        <strong>
                          MOT reminders
                        </strong>

                        <span>
                          Get a reminder before
                          an MOT is due and if
                          it expires.
                        </span>
                      </div>

                      <input
                        type="checkbox"
                        checked={
                          settings.mot_enabled
                        }
                        onChange={(
                          event,
                        ) =>
                          setSettings({
                            ...settings,

                            mot_enabled:
                              event.target
                                .checked,
                          })
                        }
                      />
                    </label>

                    <label
                      className={
                        styles.toggleRow
                      }
                    >
                      <div
                        className={
                          styles.toggleText
                        }
                      >
                        <strong>
                          Maintenance reminders
                        </strong>

                        <span>
                          Get a reminder when
                          scheduled maintenance
                          is approaching.
                        </span>
                      </div>

                      <input
                        type="checkbox"
                        checked={
                          settings
                            .maintenance_enabled
                        }
                        onChange={(
                          event,
                        ) =>
                          setSettings({
                            ...settings,

                            maintenance_enabled:
                              event.target
                                .checked,
                          })
                        }
                      />
                    </label>

                    <label
                      className={
                        styles.field
                      }
                    >
                      <span>
                        Days before due
                      </span>

                      <input
                        type="number"
                        min="1"
                        max="90"
                        value={
                          settings
                            .due_soon_days
                        }
                        onChange={(
                          event,
                        ) =>
                          setSettings({
                            ...settings,

                            due_soon_days:
                              Number(
                                event.target
                                  .value,
                              ),
                          })
                        }
                      />
                    </label>

                    <label
                      className={
                        styles.field
                      }
                    >
                      <span>
                        Miles before due
                      </span>

                      <input
                        type="number"
                        min="100"
                        max="5000"
                        step="100"
                        value={
                          settings
                            .due_soon_miles
                        }
                        onChange={(
                          event,
                        ) =>
                          setSettings({
                            ...settings,

                            due_soon_miles:
                              Number(
                                event.target
                                  .value,
                              ),
                          })
                        }
                      />
                    </label>
                  </div>

                  <div
                    className={
                      styles.settingsActions
                    }
                  >
                    <button
                      className={
                        styles.secondaryButton
                      }
                      type="button"
                      disabled={
                        restoring
                      }
                      onClick={
                        handleRestore
                      }
                    >
                      {restoring
                        ? "Restoring..."
                        : "Restore dismissed"}
                    </button>

                    <button
                      className={
                        styles.primaryButton
                      }
                      type="button"
                      disabled={
                        saving
                      }
                      onClick={
                        handleSaveSettings
                      }
                    >
                      {saving
                        ? "Saving..."
                        : "Save settings"}
                    </button>
                  </div>
                </section>
              )}

              {reminders.length === 0 ? (
                <div
                  className={
                    styles.empty
                  }
                >
                  <strong>
                    Everything looks up to date
                  </strong>

                  You don&apos;t have any
                  reminders that need attention
                  right now.
                </div>

              ) : (
                <div
                  className={
                    styles.list
                  }
                >
                  {reminders.map(
                    (reminder) => (
                      <article
                        className={`${styles.reminder} ${
                          reminder.severity
                          === "urgent"
                            ? styles.urgent
                            : ""
                        }`}
                        key={
                          reminder.reminder_key
                        }
                      >
                        <div
                          className={
                            styles.numberPlate
                          }
                        >
                          {formatRegistration(
                            reminder.registration,
                          )}
                        </div>

                        <div
                          className={
                            styles.content
                          }
                        >
                          <div
                            className={
                              styles.topLine
                            }
                          >
                            <h3>
                              {reminder.title}
                            </h3>

                            <span
                              className={`${styles.badge} ${
                                reminder.severity
                                === "urgent"
                                  ? styles.urgent
                                  : styles.warning
                              }`}
                            >
                              {reminder.severity
                                === "urgent"
                                ? "Urgent"
                                : "Due soon"}
                            </span>
                          </div>

                          <p
                            className={
                              styles.message
                            }
                          >
                            {reminder.message}
                          </p>

                          <div
                            className={
                              styles.vehicleName
                            }
                          >
                            {vehicleName(
                              reminder,
                            )}
                          </div>
                        </div>

                        <div
                          className={
                            styles.reminderActions
                          }
                        >
                          <button
                            className={
                              styles.primaryButton
                            }
                            type="button"
                            onClick={() =>
                              router.push(
                                reminder.action_href,
                              )
                            }
                          >
                            View vehicle
                          </button>

                          <button
                            className={
                              styles.dismissButton
                            }
                            type="button"
                            disabled={
                              dismissingKey
                              === reminder.reminder_key
                            }
                            onClick={() =>
                              handleDismiss(
                                reminder,
                              )
                            }
                          >
                            {dismissingKey
                            === reminder.reminder_key
                              ? "..."
                              : "Dismiss"}
                          </button>
                        </div>
                      </article>
                    ),
                  )}
                </div>
              )}
            </>
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