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
    new Intl.NumberFormat(
      "en-GB",
    ).format(value);

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
      new Date(
        b.completed_at,
      ).getTime() -
      new Date(
        a.completed_at,
      ).getTime(),
  );
}


export function getLatestMileage(
  tests: MotTest[],
): {
  value: number | null;
  unit: string | null;
} {
  const test =
    sortMotTests(tests).find(
      (item) =>
        item.odometer_value !== null,
    );

  return {
    value:
      test?.odometer_value ?? null,
    unit:
      test?.odometer_unit ?? null,
  };
}


export function getMileageChange(
  currentTest: MotTest,
  previousTest: MotTest | undefined,
): {
  label: string;
  tone:
    | "positive"
    | "negative"
    | "neutral"
    | "unavailable";
} {
  if (!previousTest) {
    return {
      label:
        "No earlier MOT mileage",
      tone: "unavailable",
    };
  }

  if (
    currentTest.odometer_value ===
      null ||
    previousTest.odometer_value ===
      null
  ) {
    return {
      label:
        "Mileage change unavailable",
      tone: "unavailable",
    };
  }

  const currentUnit =
    currentTest.odometer_unit
      ?.toUpperCase();

  const previousUnit =
    previousTest.odometer_unit
      ?.toUpperCase();

  // Readings in different units should not be compared.
  if (
    currentUnit &&
    previousUnit &&
    currentUnit !== previousUnit
  ) {
    return {
      label:
        "Mileage change unavailable",
      tone: "unavailable",
    };
  }

  const difference =
    currentTest.odometer_value -
    previousTest.odometer_value;

  const unit =
    currentUnit === "MI"
      ? "mi"
      : currentUnit?.toLowerCase() ??
        "";

  const formattedDifference =
    new Intl.NumberFormat(
      "en-GB",
    ).format(
      Math.abs(difference),
    );

  if (difference > 0) {
    return {
      label:
        `+${formattedDifference} ${unit} since previous MOT`.trim(),
      tone: "positive",
    };
  }

  if (difference < 0) {
    return {
      label:
        `-${formattedDifference} ${unit} vs previous MOT`.trim(),
      tone: "negative",
    };
  }

  return {
    label:
      "No mileage change since previous MOT",
    tone: "neutral",
  };
}


export function getCurrentMot(
  tests: MotTest[],
): {
  label: string;
  expiryDate: string | null;
  daysRemaining: number | null;
  timeRemainingLabel: string;
  tone:
    | "good"
    | "warning"
    | "bad"
    | "neutral";
} {
  const passedTests =
    sortMotTests(tests).filter(
      (test) =>
        test.test_result
          ?.toUpperCase() ===
          "PASSED" &&
        test.expiry_date,
    );

  const latestPassed =
    passedTests[0];

  if (
    !latestPassed?.expiry_date
  ) {
    return {
      label: "No MOT data",
      expiryDate: null,
      daysRemaining: null,
      timeRemainingLabel:
        "No expiry available",
      tone: "neutral",
    };
  }

  const today = new Date();

  today.setHours(
    0,
    0,
    0,
    0,
  );

  const expiry = new Date(
    `${latestPassed.expiry_date}T00:00:00`,
  );

  const millisecondsPerDay =
    1000 * 60 * 60 * 24;

  const daysRemaining =
    Math.round(
      (
        expiry.getTime() -
        today.getTime()
      ) /
        millisecondsPerDay,
    );

  if (daysRemaining < 0) {
    const daysExpired =
      Math.abs(daysRemaining);

    return {
      label: "MOT expired",
      expiryDate:
        latestPassed.expiry_date,
      daysRemaining,
      timeRemainingLabel:
        daysExpired === 1
          ? "Expired yesterday"
          : `Expired ${daysExpired} days ago`,
      tone: "bad",
    };
  }

  if (daysRemaining === 0) {
    return {
      label:
        "MOT expires today",
      expiryDate:
        latestPassed.expiry_date,
      daysRemaining,
      timeRemainingLabel:
        "Expires today",
      tone: "warning",
    };
  }

  if (daysRemaining <= 30) {
    return {
      label:
        "MOT expires soon",
      expiryDate:
        latestPassed.expiry_date,
      daysRemaining,
      timeRemainingLabel:
        daysRemaining === 1
          ? "1 day left"
          : `${daysRemaining} days left`,
      tone: "warning",
    };
  }

  return {
    label: "MOT valid",
    expiryDate:
      latestPassed.expiry_date,
    daysRemaining,
    timeRemainingLabel:
      `${daysRemaining} days left`,
    tone: "good",
  };
}


export function getDefectTone(
  defect: MotDefect,
): string {
  const type =
    defect.type.toUpperCase();

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

  if (type === "PRS") {
    return "prs";
  }

  return "other";
}