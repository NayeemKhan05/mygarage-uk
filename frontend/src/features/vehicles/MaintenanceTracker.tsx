"use client";

import {
  FormEvent,
  useEffect,
  useState,
} from "react";

import {
  ApiError,
  createMaintenanceItem,
  deleteMaintenanceItem,
  getMaintenanceItems,
  updateMaintenanceItem,
} from "../../lib/api";

import type {
  MaintenanceCategory,
  MaintenanceItem,
  MaintenanceItemPayload,
  MaintenanceStatus,
} from "../../types/maintenance";

import {
  formatDate,
  formatMileage,
} from "../vehicle-check/utils";

import styles from "./VehicleManagement.module.css";


interface MaintenanceTrackerProps {
  vehicleId: number;
}


interface MaintenanceFormState {
  name: string;
  category: MaintenanceCategory;

  lastCompletedDate: string;
  lastCompletedMileage: string;

  nextDueDate: string;
  nextDueMileage: string;

  notes: string;
}


function emptyForm():
  MaintenanceFormState {
  return {
    name: "",
    category: "general",

    lastCompletedDate: "",
    lastCompletedMileage: "",

    nextDueDate: "",
    nextDueMileage: "",

    notes: "",
  };
}


function statusClass(
  status: MaintenanceStatus,
): string {
  if (status === "good") {
    return styles.good;
  }

  if (
    status === "due_soon"
  ) {
    return styles.dueSoon;
  }

  if (
    status === "overdue"
  ) {
    return styles.overdue;
  }

  return styles.unknown;
}


function statusLabel(
  status: MaintenanceStatus,
): string {
  if (status === "good") {
    return "Good";
  }

  if (
    status === "due_soon"
  ) {
    return "Due soon";
  }

  if (
    status === "overdue"
  ) {
    return "Overdue";
  }

  return "Unknown";
}


export default function MaintenanceTracker({
  vehicleId,
}: MaintenanceTrackerProps) {
  const [
    items,
    setItems,
  ] =
    useState<MaintenanceItem[]>(
      [],
    );

  const [
    loading,
    setLoading,
  ] =
    useState(true);

  const [
    formOpen,
    setFormOpen,
  ] =
    useState(false);

  const [
    editingId,
    setEditingId,
  ] =
    useState<number | null>(
      null,
    );

  const [
    form,
    setForm,
  ] =
    useState<MaintenanceFormState>(
      emptyForm(),
    );

  const [
    saving,
    setSaving,
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


  async function loadItems() {
    try {
      const result =
        await getMaintenanceItems(
          vehicleId,
        );

      setItems(result);

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
          "We could not load maintenance items.",
        );
      }

    } finally {
      setLoading(false);
    }
  }


  useEffect(() => {
    loadItems();
  }, [vehicleId]);


  function resetForm() {
    setForm(
      emptyForm(),
    );

    setEditingId(null);
    setFormOpen(false);
  }


  function startCreate() {
    setError(null);
    setNotice(null);

    setForm(
      emptyForm(),
    );

    setEditingId(null);
    setFormOpen(true);
  }


  function startEdit(
    item: MaintenanceItem,
  ) {
    setError(null);
    setNotice(null);

    setEditingId(
      item.id,
    );

    setForm({
      name:
        item.name,

      category:
        item.category,

      lastCompletedDate:
        item.last_completed_date
        ?? "",

      lastCompletedMileage:
        item.last_completed_mileage
          ?.toString()
        ?? "",

      nextDueDate:
        item.next_due_date
        ?? "",

      nextDueMileage:
        item.next_due_mileage
          ?.toString()
        ?? "",

      notes:
        item.notes
        ?? "",
    });

    setFormOpen(true);
  }


  function payload():
    MaintenanceItemPayload {
    return {
      name:
        form.name.trim(),

      category:
        form.category,

      last_completed_date:
        form.lastCompletedDate
        || null,

      last_completed_mileage:
        form.lastCompletedMileage
          ? Number(
              form.lastCompletedMileage,
            )
          : null,

      next_due_date:
        form.nextDueDate
        || null,

      next_due_mileage:
        form.nextDueMileage
          ? Number(
              form.nextDueMileage,
            )
          : null,

      notes:
        form.notes.trim()
        || null,
    };
  }


  async function handleSubmit(
    event:
      FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault();

    if (!form.name.trim()) {
      setError(
        "Enter a maintenance item.",
      );

      return;
    }

    setSaving(true);
    setError(null);
    setNotice(null);

    try {
      if (
        editingId !== null
      ) {
        await updateMaintenanceItem(
          vehicleId,
          editingId,
          payload(),
        );

        setNotice(
          "Maintenance item updated.",
        );

      } else {
        await createMaintenanceItem(
          vehicleId,
          payload(),
        );

        setNotice(
          "Maintenance item added.",
        );
      }

      resetForm();

      await loadItems();

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
          "We could not save the maintenance item.",
        );
      }

    } finally {
      setSaving(false);
    }
  }


  async function handleDelete(
    item: MaintenanceItem,
  ) {
    const confirmed =
      window.confirm(
        (
          `Remove "${item.name}" `
          + "from maintenance tracking?"
        ),
      );

    if (!confirmed) {
      return;
    }

    try {
      await deleteMaintenanceItem(
        vehicleId,
        item.id,
      );

      setNotice(
        "Maintenance item removed.",
      );

      await loadItems();

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
          "We could not remove the maintenance item.",
        );
      }
    }
  }


  const goodCount =
    items.filter(
      (item) =>
        item.status
        === "good",
    ).length;

  const dueSoonCount =
    items.filter(
      (item) =>
        item.status
        === "due_soon",
    ).length;

  const overdueCount =
    items.filter(
      (item) =>
        item.status
        === "overdue",
    ).length;

  const unknownCount =
    items.filter(
      (item) =>
        item.status
        === "unknown",
    ).length;


  return (
    <section className={styles.section}>
      <div className={styles.sectionHeader}>
        <div>
          <span className={styles.eyebrow}>
            Maintenance
          </span>

          <h2>
            Maintenance tracker
          </h2>

          <p>
            Track what has been changed and
            when the next maintenance item is
            due by date or mileage.
          </p>
        </div>

        <button
          className={styles.addButton}
          type="button"
          onClick={startCreate}
        >
          + Track maintenance
        </button>
      </div>

      {error && (
        <div
          className={styles.error}
          role="alert"
        >
          {error}
        </div>
      )}

      {notice && (
        <div className={styles.notice}>
          {notice}
        </div>
      )}

      {!loading &&
        items.length > 0 && (
          <div className={styles.maintenanceSummary}>
            <div className={styles.summaryBox}>
              <strong>
                {goodCount}
              </strong>

              <span>
                Good
              </span>
            </div>

            <div className={styles.summaryBox}>
              <strong>
                {dueSoonCount}
              </strong>

              <span>
                Due soon
              </span>
            </div>

            <div className={styles.summaryBox}>
              <strong>
                {overdueCount}
              </strong>

              <span>
                Overdue
              </span>
            </div>

            <div className={styles.summaryBox}>
              <strong>
                {unknownCount}
              </strong>

              <span>
                Unknown
              </span>
            </div>
          </div>
        )}

      {formOpen && (
        <form
          className={styles.form}
          onSubmit={handleSubmit}
        >
          <h3 className={styles.formTitle}>
            {editingId
              ? "Edit maintenance item"
              : "Track maintenance"}
          </h3>

          <div className={styles.formGrid}>
            <label className={styles.field}>
              <span>
                Maintenance item
              </span>

              <input
                type="text"
                value={form.name}
                onChange={(event) =>
                  setForm({
                    ...form,

                    name:
                      event.target.value,
                  })
                }
                placeholder="e.g. Engine oil"
                required
              />
            </label>

            <label className={styles.field}>
              <span>
                Category
              </span>
            <select
                value={form.category}
                onChange={(event) =>
                setForm({
                    ...form,

                    category: (
                    event.target.value as MaintenanceCategory
                    ),
                })
                }
            >
                <option value="oil">
                  Oil
                </option>

                <option value="filters">
                  Filters
                </option>

                <option value="brakes">
                  Brakes
                </option>

                <option value="tyres">
                  Tyres
                </option>

                <option value="fluids">
                  Fluids
                </option>

                <option value="belts">
                  Belts
                </option>

                <option value="battery">
                  Battery
                </option>

                <option value="suspension">
                  Suspension
                </option>

                <option value="general">
                  General
                </option>

                <option value="other">
                  Other
                </option>
              </select>
            </label>

            <label className={styles.field}>
              <span>
                Last completed date
              </span>

              <input
                type="date"
                value={
                  form.lastCompletedDate
                }
                onChange={(event) =>
                  setForm({
                    ...form,

                    lastCompletedDate:
                      event.target.value,
                  })
                }
              />
            </label>

            <label className={styles.field}>
              <span>
                Last completed mileage
              </span>

              <input
                type="number"
                min="0"
                value={
                  form.lastCompletedMileage
                }
                onChange={(event) =>
                  setForm({
                    ...form,

                    lastCompletedMileage:
                      event.target.value,
                  })
                }
                placeholder="e.g. 80000"
              />
            </label>

            <label className={styles.field}>
              <span>
                Next due date
              </span>

              <input
                type="date"
                value={
                  form.nextDueDate
                }
                onChange={(event) =>
                  setForm({
                    ...form,

                    nextDueDate:
                      event.target.value,
                  })
                }
              />
            </label>

            <label className={styles.field}>
              <span>
                Next due mileage
              </span>

              <input
                type="number"
                min="0"
                value={
                  form.nextDueMileage
                }
                onChange={(event) =>
                  setForm({
                    ...form,

                    nextDueMileage:
                      event.target.value,
                  })
                }
                placeholder="e.g. 90000"
              />
            </label>

            <label
              className={`${styles.field} ${styles.fullWidth}`}
            >
              <span>
                Notes
              </span>

              <textarea
                value={
                  form.notes
                }
                onChange={(event) =>
                  setForm({
                    ...form,

                    notes:
                      event.target.value,
                  })
                }
                placeholder="Brand, specification, mechanic advice, anything else..."
              />
            </label>
          </div>

          <div className={styles.formActions}>
            <button
              className={styles.cancelButton}
              type="button"
              onClick={resetForm}
            >
              Cancel
            </button>

            <button
              className={styles.saveButton}
              type="submit"
              disabled={saving}
            >
              {saving
                ? "Saving..."
                : editingId
                  ? "Save changes"
                  : "Add item"}
            </button>
          </div>
        </form>
      )}

      {loading ? (
        <div className={styles.loading}>
          Loading maintenance...
        </div>

      ) : items.length === 0 ? (
        <div className={styles.empty}>
          Nothing is being tracked yet.
          Add engine oil, tyres, brake pads,
          fluids or anything else you want
          MyGarage to keep an eye on.
        </div>

      ) : (
        <div className={styles.list}>
          {items.map((item) => {
            const tone =
              statusClass(
                item.status,
              );

            return (
              <article
                className={`${styles.maintenanceCard} ${tone}`}
                key={item.id}
              >
                <div className={styles.maintenanceHeader}>
                  <div>
                    <div className={styles.recordTitleRow}>
                      <h3 className={styles.maintenanceName}>
                        {item.name}
                      </h3>

                      <span className={styles.categoryBadge}>
                        {item.category}
                      </span>
                    </div>

                    <div
                      className={`${styles.statusReason} ${tone}`}
                    >
                      {item.status_reason}
                    </div>
                  </div>

                  <div className={styles.recordActions}>
                    <span
                      className={`${styles.statusBadge} ${tone}`}
                    >
                      {statusLabel(
                        item.status,
                      )}
                    </span>

                    <button
                      className={styles.secondaryButton}
                      type="button"
                      onClick={() =>
                        startEdit(
                          item,
                        )
                      }
                    >
                      Edit
                    </button>

                    <button
                      className={styles.dangerButton}
                      type="button"
                      onClick={() =>
                        handleDelete(
                          item,
                        )
                      }
                    >
                      Delete
                    </button>
                  </div>
                </div>

                <div className={styles.maintenanceDetails}>
                  <div className={styles.maintenanceDetail}>
                    <span>
                      Last completed
                    </span>

                    <strong>
                      {item.last_completed_date
                        ? formatDate(
                            item.last_completed_date,
                          )
                        : "Not recorded"}
                    </strong>
                  </div>

                  <div className={styles.maintenanceDetail}>
                    <span>
                      Mileage when completed
                    </span>

                    <strong>
                      {formatMileage(
                        item.last_completed_mileage,
                        "MI",
                      )}
                    </strong>
                  </div>

                  <div className={styles.maintenanceDetail}>
                    <span>
                      Next due
                    </span>

                    <strong>
                      {item.next_due_date
                        ? formatDate(
                            item.next_due_date,
                          )
                        : "No date set"}
                    </strong>
                  </div>

                  <div className={styles.maintenanceDetail}>
                    <span>
                      Next due mileage
                    </span>

                    <strong>
                      {formatMileage(
                        item.next_due_mileage,
                        "MI",
                      )}
                    </strong>
                  </div>
                </div>

                {item.notes && (
                  <p className={styles.notes}>
                    {item.notes}
                  </p>
                )}
              </article>
            );
          })}
        </div>
      )}
    </section>
  );
}