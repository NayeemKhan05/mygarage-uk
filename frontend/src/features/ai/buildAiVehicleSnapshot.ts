import type {
  AiMotTestSnapshot,
  AiVehicleSnapshot,
} from "../../types/ai";

import type {
  MotTest,
  VehicleCheckResponse,
} from "../../types/vehicle";


function motTestToSnapshot(
  test: MotTest,
): AiMotTestSnapshot {
  return {
    completed_at:
      test.completed_at ?? null,

    test_result:
      test.test_result ?? null,

    expiry_date:
      test.expiry_date ?? null,

    odometer_value:
      test.odometer_value ?? null,

    odometer_unit:
      test.odometer_unit ?? null,

    mot_test_number:
      test.mot_test_number ?? null,

    defects:
      test.defects.map(
        (defect) => ({
          text:
            defect.text,

          type:
            defect.type ?? null,

          dangerous:
            defect.dangerous ?? false,
        }),
      ),
  };
}


export function buildLiveAiSnapshot(
  vehicle: VehicleCheckResponse,
): AiVehicleSnapshot {
  return {
    registration:
      vehicle.registration,

    make:
      vehicle.make ?? null,

    model:
      vehicle.model ?? null,

    fuel_type:
      vehicle.fuel_type ?? null,

    engine_size:
      vehicle.engine_size ?? null,

    colour:
      vehicle.colour ?? null,

    year:
      vehicle.year ?? null,

    mot_tests:
      vehicle.mot_tests.map(
        motTestToSnapshot,
      ),
  };
}


function isRecord(
  value: unknown,
): value is Record<string, unknown> {
  return (
    typeof value === "object"
    && value !== null
    && !Array.isArray(value)
  );
}


function objectValue(
  source: unknown,
  key: string,
): unknown {
  if (!isRecord(source)) {
    return undefined;
  }

  return source[key];
}


function stringValue(
  source: unknown,
  key: string,
): string | null {
  const value =
    objectValue(
      source,
      key,
    );

  if (
    typeof value
    === "string"
  ) {
    return value;
  }

  return null;
}


function numberValue(
  source: unknown,
  key: string,
): number | null {
  const value =
    objectValue(
      source,
      key,
    );

  if (
    typeof value
    === "number"
    && Number.isFinite(value)
  ) {
    return value;
  }

  return null;
}


export function buildSavedAiSnapshot(
  vehicle: unknown,
  motTests: MotTest[],
  serviceRecords: unknown[] = [],
  maintenanceItems: unknown[] = [],
): AiVehicleSnapshot {
  return {
    registration:
      stringValue(
        vehicle,
        "registration",
      ) ?? "",

    make:
      stringValue(
        vehicle,
        "make",
      ),

    model:
      stringValue(
        vehicle,
        "model",
      ),

    fuel_type:
      stringValue(
        vehicle,
        "fuel_type",
      ),

    engine_size:
      numberValue(
        vehicle,
        "engine_size",
      ),

    colour:
      stringValue(
        vehicle,
        "colour",
      ),

    year:
      numberValue(
        vehicle,
        "year",
      ),

    mot_tests:
      motTests.map(
        motTestToSnapshot,
      ),

    supplementary_service_records:
      serviceRecords,

    supplementary_maintenance_items:
      maintenanceItems,
  };
}