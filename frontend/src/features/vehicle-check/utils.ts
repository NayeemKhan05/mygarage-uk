import type {
  MotDefect,
  MotTest,
} from "../../types/vehicle";


export function formatRegistration(
  registration: string,
): string {
  const cleaned = registration
    .replace(/\s+/g, "")
    .toUpperCase();

  if (cleaned.length <= 3) {
    return cleaned;
  }

  return `${cleaned.slice(0, -3)} ${cleaned.slice(-3)}`;
}


export function formatDate(
  value: string | null,
): string {
  if (!value) {
    return "Not available";
  }

  const normalised = value.includes("T")
    ? value
    : value.includes(" ")
      ? value.replace(" ", "T")
      : `${value}T00:00:00`;

  const date = new Date(normalised);

  if (Number.isNaN(date.getTime())) {
    return value;
  }

  return new Intl.DateTimeFormat(
    "en-GB",
    {
      day: "numeric",
      month: "short",
      year: "numeric",
    },
  ).format(date);
}


export function formatMileage(
  value: number | null,
  unit: string | null,
): string {
  if (value === null) {
    return "Not recorded";
  }

  const formatted =
    new Intl.NumberFormat("en-GB").format(value);

  if (!unit) {
    return formatted;
  }

  const normalisedUnit =
    unit.toUpperCase() === "MI"
      ? "mi"
      : unit.toLowerCase();

  return `${formatted} ${normalisedUnit}`;
}


export function sortMotTests(
  tests: MotTest[],
): MotTest[] {
  return [...tests].sort(
    (a, b) =>
      new Date(b.completed_at).getTime() -
      new Date(a.completed_at).getTime(),
  );
}


export function getLatestMileage(
  tests: MotTest[],
): {
  value: number | null;
  unit: string | null;
} {
  const test = sortMotTests(tests).find(
    (item) => item.odometer_value !== null,
  );

  return {
    value: test?.odometer_value ?? null,
    unit: test?.odometer_unit ?? null,
  };
}


export function getCurrentMot(
  tests: MotTest[],
): {
  label: string;
  expiryDate: string | null;
  tone: "good" | "bad" | "neutral";
} {
  const passedTests = sortMotTests(tests).filter(
    (test) =>
      test.test_result?.toUpperCase() ===
        "PASSED" &&
      test.expiry_date,
  );

  const latestPassed = passedTests[0];

  if (!latestPassed?.expiry_date) {
    return {
      label: "No MOT data",
      expiryDate: null,
      tone: "neutral",
    };
  }

  const expiry = new Date(
    `${latestPassed.expiry_date}T23:59:59`,
  );

  const valid = expiry.getTime() >= Date.now();

  return {
    label: valid
      ? "MOT valid"
      : "MOT expired",
    expiryDate: latestPassed.expiry_date,
    tone: valid ? "good" : "bad",
  };
}


export function getDefectTone(
  defect: MotDefect,
): string {
  const type = defect.type.toUpperCase();

  if (
    type === "DANGEROUS" ||
    defect.dangerous
  ) {
    return "dangerous";
  }

  if (type === "MAJOR") {
    return "major";
  }

  if (type === "MINOR") {
    return "minor";
  }

  if (type === "ADVISORY") {
    return "advisory";
  }

  return "other";
}