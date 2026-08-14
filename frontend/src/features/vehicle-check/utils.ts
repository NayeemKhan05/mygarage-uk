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


export function getMileageChange(
  currentTest: MotTest,
  previousTest: MotTest | undefined,
): {
  label: string;
  tone: "positive" | "negative" | "neutral" | "unavailable";
} {
  if (!previousTest) {
    return {
      label: "No earlier MOT mileage",
      tone: "unavailable",
    };
  }

  if (
    currentTest.odometer_value === null ||
    previousTest.odometer_value === null
  ) {
    return {
      label: "Mileage change unavailable",
      tone: "unavailable",
    };
  }

  const currentUnit =
    currentTest.odometer_unit?.toUpperCase();

  const previousUnit =
    previousTest.odometer_unit?.toUpperCase();

  // We should not compare readings if DVSA recorded them in different units.
  if (
    currentUnit &&
    previousUnit &&
    currentUnit !== previousUnit
  ) {
    return {
      label: "Mileage change unavailable",
      tone: "unavailable",
    };
  }

  const difference =
    currentTest.odometer_value -
    previousTest.odometer_value;

  const unit =
    currentUnit === "MI"
      ? "mi"
      : currentUnit?.toLowerCase() ?? "";

  const formattedDifference =
    new Intl.NumberFormat("en-GB").format(
      Math.abs(difference),
    );

  if (difference > 0) {
    return {
      label: `+${formattedDifference} ${unit} since previous MOT`.trim(),
      tone: "positive",
    };
  }

  if (difference < 0) {
    return {
      label: `-${formattedDifference} ${unit} vs previous MOT`.trim(),
      tone: "negative",
    };
  }

  return {
    label: `No mileage change since previous MOT`,
    tone: "neutral",
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