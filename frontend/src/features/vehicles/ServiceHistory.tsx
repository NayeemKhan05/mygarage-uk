"use client";

import {
  ChangeEvent,
  FormEvent,
  useEffect,
  useState,
} from "react";

import {
  ApiError,
  createServiceRecord,
  deleteServiceReceipt,
  deleteServiceRecord,
  getServiceReceiptUrl,
  getServiceRecords,
  updateServiceRecord,
  uploadServiceReceipt,
} from "../../lib/api";

import type {
  ServiceCategory,
  ServiceRecord,
  ServiceRecordPayload,
} from "../../types/service";

import {
  formatDate,
  formatMileage,
} from "../vehicle-check/utils";

import styles from "./VehicleManagement.module.css";


interface ServiceHistoryProps {
  vehicleId: number;
}


interface ServiceFormState {
  serviceDate: string;
  title: string;
  category: ServiceCategory;
  mileage: string;
  garage: string;
  cost: string;
  notes: string;
}


function todayString(): string {
  return new Date()
    .toISOString()
    .slice(0, 10);
}


function emptyForm():
  ServiceFormState {
  return {
    serviceDate:
      todayString(),

    title: "",

    category:
      "service",

    mileage: "",
    garage: "",
    cost: "",
    notes: "",
  };
}


function formatMoney(
  value: number | null,
): string {
  if (value === null) {
    return "Not recorded";
  }

  return new Intl.NumberFormat(
    "en-GB",
    {
      style: "currency",
      currency: "GBP",
    },
  ).format(value);
}


function formatFileSize(
  bytes: number,
): string {
  if (bytes < 1024) {
    return `${bytes} B`;
  }

  if (
    bytes < 1024 * 1024
  ) {
    return `${(
      bytes / 1024
    ).toFixed(1)} KB`;
  }

  return `${(
    bytes /
    (1024 * 1024)
  ).toFixed(1)} MB`;
}


function receiptLabel(
  contentType: string,
): string {
  if (
    contentType ===
    "application/pdf"
  ) {
    return "PDF";
  }

  return "IMG";
}


export default function ServiceHistory({
  vehicleId,
}: ServiceHistoryProps) {
  const [
    records,
    setRecords,
  ] =
    useState<ServiceRecord[]>(
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
    form,
    setForm,
  ] =
    useState<ServiceFormState>(
      emptyForm(),
    );

  const [
    editingId,
    setEditingId,
  ] =
    useState<number | null>(
      null,
    );

  const [
    receiptFile,
    setReceiptFile,
  ] =
    useState<File | null>(
      null,
    );

  const [
    saving,
    setSaving,
  ] =
    useState(false);

  const [
    uploadingRecordId,
    setUploadingRecordId,
  ] =
    useState<number | null>(
      null,
    );

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


  async function loadRecords() {
    try {
      const result =
        await getServiceRecords(
          vehicleId,
        );

      setRecords(result);

    } catch (caughtError) {
      if (
        caughtError instanceof
        ApiError
      ) {
        setError(
          (
            "We couldn’t load the service "
            + "history right now. "
            + "Please try again."
          ),
        );
      } else {
        setError(
          (
            "We couldn’t load the service "
            + "history right now. "
            + "Please try again."
          ),
        );
      }

    } finally {
      setLoading(false);
    }
  }


  useEffect(() => {
    loadRecords();
  }, [vehicleId]);


  function resetForm() {
    setForm(
      emptyForm(),
    );

    setReceiptFile(null);
    setEditingId(null);
    setFormOpen(false);
  }


  function startCreate() {
    setError(null);
    setNotice(null);

    setForm(
      emptyForm(),
    );

    setReceiptFile(null);
    setEditingId(null);
    setFormOpen(true);
  }


  function startEdit(
    record: ServiceRecord,
  ) {
    setError(null);
    setNotice(null);

    setEditingId(
      record.id,
    );

    setReceiptFile(null);

    setForm({
      serviceDate:
        record.service_date,

      title:
        record.title,

      category:
        record.category,

      mileage:
        record.mileage?.toString()
        ?? "",

      garage:
        record.garage
        ?? "",

      cost:
        record.cost?.toString()
        ?? "",

      notes:
        record.notes
        ?? "",
    });

    setFormOpen(true);
  }


  function buildPayload():
    ServiceRecordPayload {
    return {
      service_date:
        form.serviceDate,

      title:
        form.title.trim(),

      category:
        form.category,

      mileage:
        form.mileage
          ? Number(
              form.mileage,
            )
          : null,

      garage:
        form.garage.trim()
          || null,

      cost:
        form.cost
          ? Number(
              form.cost,
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

    if (
      !form.title.trim()
    ) {
      setError(
        "Enter what work was carried out.",
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
        await updateServiceRecord(
          vehicleId,
          editingId,
          buildPayload(),
        );

        setNotice(
          "Service record updated.",
        );

      } else {
        const created =
          await createServiceRecord(
            vehicleId,
            buildPayload(),
          );

        if (receiptFile) {
          await uploadServiceReceipt(
            vehicleId,
            created.id,
            receiptFile,
          );
        }

        setNotice(
          receiptFile
            ? "Service record and receipt saved."
            : "Service record saved.",
        );
      }

      resetForm();

      await loadRecords();

    } catch (caughtError) {
      if (
        caughtError instanceof
        ApiError
      ) {
        setError(
          (
            "We couldn’t save this service "
            + "record. Please try again."
          ),
        );
      } else {
        setError(
          (
            "We couldn’t save this service "
            + "record. Please try again."
          ),
        );
      }

    } finally {
      setSaving(false);
    }
  }


  async function handleDelete(
    record: ServiceRecord,
  ) {
    const confirmed =
      window.confirm(
        (
          `Delete "${record.title}" `
          + "from the service history?"
        ),
      );

    if (!confirmed) {
      return;
    }

    setError(null);
    setNotice(null);

    try {
      await deleteServiceRecord(
        vehicleId,
        record.id,
      );

      setNotice(
        "Service record deleted.",
      );

      await loadRecords();

    } catch (caughtError) {
      if (
        caughtError instanceof
        ApiError
      ) {
        setError(
          (
            "We couldn’t delete this service "
            + "record. Please try again."
          ),
        );
      } else {
        setError(
          (
            "We couldn’t delete this service "
            + "record. Please try again."
          ),
        );
      }
    }
  }


  async function handleReceiptUpload(
    recordId: number,
    event:
      ChangeEvent<HTMLInputElement>,
  ) {
    const input =
      event.currentTarget;

    const file =
      input.files?.[0];

    input.value = "";

    if (!file) {
      return;
    }

    setUploadingRecordId(
      recordId,
    );

    setError(null);
    setNotice(null);

    try {
      await uploadServiceReceipt(
        vehicleId,
        recordId,
        file,
      );

      setNotice(
        "Receipt attached.",
      );

      await loadRecords();

    } catch (caughtError) {
      if (
        caughtError instanceof
        ApiError
      ) {
        setError(
          (
            "We couldn’t upload this receipt. "
            + "Please try again."
          ),
        );
      } else {
        setError(
          (
            "We couldn’t upload this receipt. "
            + "Please try again."
          ),
        );
      }

    } finally {
      setUploadingRecordId(
        null,
      );
    }
  }


  async function handleDeleteReceipt(
    recordId: number,
    receiptId: number,
  ) {
    const confirmed =
      window.confirm(
        "Delete this receipt?",
      );

    if (!confirmed) {
      return;
    }

    try {
      await deleteServiceReceipt(
        vehicleId,
        recordId,
        receiptId,
      );

      setNotice(
        "Receipt deleted.",
      );

      await loadRecords();

    } catch (caughtError) {
      if (
        caughtError instanceof
        ApiError
      ) {
        setError(
          (
            "We couldn’t delete this receipt. "
            + "Please try again."
          ),
        );
      } else {
        setError(
          (
            "We couldn’t delete this receipt. "
            + "Please try again."
          ),
        );
      }
    }
  }


  return (
    <section className={styles.section}>
      <div className={styles.sectionHeader}>
        <div>
          <span className={styles.eyebrow}>
            Vehicle records
          </span>

          <h2>
            Service history
          </h2>

          <p>
            Keep a record of servicing,
            repairs and parts fitted to
            this vehicle.
          </p>
        </div>

        <button
          className={styles.addButton}
          type="button"
          onClick={startCreate}
        >
          + Add service or repair
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

      {formOpen && (
        <form
          className={styles.form}
          onSubmit={handleSubmit}
        >
          <h3 className={styles.formTitle}>
            {editingId
              ? "Edit service record"
              : "Add service or repair"}
          </h3>

          <div className={styles.formGrid}>
            <label className={styles.field}>
              <span>
                Date
              </span>

              <input
                type="date"
                value={
                  form.serviceDate
                }
                onChange={(event) =>
                  setForm({
                    ...form,

                    serviceDate:
                      event.target.value,
                  })
                }
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
                      event.target.value as ServiceCategory
                    ),
                  })
                }
              >
                <option value="service">
                  Service
                </option>

                <option value="repair">
                  Repair
                </option>

                <option value="maintenance">
                  Maintenance
                </option>

                <option value="parts">
                  Parts purchase
                </option>

                <option value="inspection">
                  Inspection
                </option>

                <option value="other">
                  Other
                </option>
              </select>
            </label>

            <label
              className={`${styles.field} ${styles.fullWidth}`}
            >
              <span>
                Work carried out
              </span>

              <input
                type="text"
                value={form.title}
                onChange={(event) =>
                  setForm({
                    ...form,

                    title:
                      event.target.value,
                  })
                }
                placeholder="e.g. Front brake pads replaced"
                maxLength={160}
                required
              />
            </label>

            <label className={styles.field}>
              <span>
                Mileage
              </span>

              <input
                type="number"
                min="0"
                value={
                  form.mileage
                }
                onChange={(event) =>
                  setForm({
                    ...form,

                    mileage:
                      event.target.value,
                  })
                }
                placeholder="e.g. 82400"
              />
            </label>

            <label className={styles.field}>
              <span>
                Cost (£)
              </span>

              <input
                type="number"
                min="0"
                step="0.01"
                value={
                  form.cost
                }
                onChange={(event) =>
                  setForm({
                    ...form,

                    cost:
                      event.target.value,
                  })
                }
                placeholder="e.g. 145.50"
              />
            </label>

            <label
              className={`${styles.field} ${styles.fullWidth}`}
            >
              <span>
                Garage / supplier
              </span>

              <input
                type="text"
                value={
                  form.garage
                }
                onChange={(event) =>
                  setForm({
                    ...form,

                    garage:
                      event.target.value,
                  })
                }
                placeholder="Optional"
                maxLength={160}
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
                placeholder="Parts used, work completed or anything else worth noting..."
              />
            </label>

            {!editingId && (
              <label
                className={`${styles.field} ${styles.fullWidth}`}
              >
                <span>
                  Receipt / invoice
                </span>

                <input
                  className={styles.fileInput}
                  type="file"
                  accept=".pdf,.jpg,.jpeg,.png,.webp,application/pdf,image/jpeg,image/png,image/webp"
                  onChange={(event) =>
                    setReceiptFile(
                      event.target.files?.[0]
                      ?? null,
                    )
                  }
                />

                <p className={styles.fileHint}>
                  PDF or image, up to 10 MB.
                </p>
              </label>
            )}
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
                  : "Add record"}
            </button>
          </div>
        </form>
      )}

      {loading ? (
        <div className={styles.loading}>
          Loading service history...
        </div>

      ) : records.length === 0 ? (
        <div className={styles.empty}>
          No service history added yet.
          Add a service or repair to start
          building this vehicle&apos;s record.
        </div>

      ) : (
        <div className={styles.list}>
          {records.map((record) => (
            <article
              className={styles.record}
              key={record.id}
            >
              <div className={styles.recordHeader}>
                <div>
                  <div className={styles.recordTitleRow}>
                    <h3 className={styles.recordTitle}>
                      {record.title}
                    </h3>

                    <span className={styles.categoryBadge}>
                      {record.category}
                    </span>
                  </div>

                  <div className={styles.recordDate}>
                    {formatDate(
                      record.service_date,
                    )}
                  </div>
                </div>

                <div className={styles.recordActions}>
                  <button
                    className={styles.secondaryButton}
                    type="button"
                    onClick={() =>
                      startEdit(
                        record,
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
                        record,
                      )
                    }
                  >
                    Delete
                  </button>
                </div>
              </div>

              <div className={styles.metaGrid}>
                <div className={styles.metaItem}>
                  <span>
                    Mileage
                  </span>

                  <strong>
                    {formatMileage(
                      record.mileage,
                      "MI",
                    )}
                  </strong>
                </div>

                <div className={styles.metaItem}>
                  <span>
                    Cost
                  </span>

                  <strong>
                    {formatMoney(
                      record.cost,
                    )}
                  </strong>
                </div>

                <div className={styles.metaItem}>
                  <span>
                    Garage / supplier
                  </span>

                  <strong>
                    {record.garage
                      ?? "Not recorded"}
                  </strong>
                </div>
              </div>

              {record.notes && (
                <p className={styles.notes}>
                  {record.notes}
                </p>
              )}

              <div className={styles.receiptArea}>
                <div className={styles.receiptHeading}>
                  <strong>
                    Receipts & invoices
                  </strong>

                  <label className={styles.receiptUpload}>
                    {uploadingRecordId === record.id
                      ? "Uploading..."
                      : "+ Attach receipt"}

                    <input
                      type="file"
                      disabled={
                        uploadingRecordId
                        !== null
                      }
                      accept=".pdf,.jpg,.jpeg,.png,.webp,application/pdf,image/jpeg,image/png,image/webp"
                      onChange={(event) =>
                        handleReceiptUpload(
                          record.id,
                          event,
                        )
                      }
                    />
                  </label>
                </div>

                {record.receipts.length === 0 ? (
                  <span className={styles.fileHint}>
                    No receipt attached.
                  </span>

                ) : (
                  <div className={styles.receiptList}>
                    {record.receipts.map(
                      (receipt) => (
                        <div
                          className={styles.receipt}
                          key={receipt.id}
                        >
                          <div className={styles.receiptInfo}>
                            <span className={styles.receiptIcon}>
                              {receiptLabel(
                                receipt.content_type,
                              )}
                            </span>

                            <div>
                              <div className={styles.receiptName}>
                                {receipt.original_filename}
                              </div>

                              <span className={styles.receiptSize}>
                                {formatFileSize(
                                  receipt.size_bytes,
                                )}
                              </span>
                            </div>
                          </div>

                          <div className={styles.receiptActions}>
                            <button
                              className={styles.smallButton}
                              type="button"
                              onClick={() =>
                                window.open(
                                  getServiceReceiptUrl(
                                    vehicleId,
                                    record.id,
                                    receipt.id,
                                  ),
                                  "_blank",
                                  "noopener,noreferrer",
                                )
                              }
                            >
                              Open
                            </button>

                            <button
                              className={styles.dangerButton}
                              type="button"
                              onClick={() =>
                                handleDeleteReceipt(
                                  record.id,
                                  receipt.id,
                                )
                              }
                            >
                              Delete
                            </button>
                          </div>
                        </div>
                      ),
                    )}
                  </div>
                )}
              </div>
            </article>
          ))}
        </div>
      )}
    </section>
  );
}