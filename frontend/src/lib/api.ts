import type {
  User,
} from "../types/auth";

import type {
  VehicleCheckHistoryItem,
  VehicleCheckHistoryPayload,
} from "../types/checkHistory";

import type {
  MaintenanceItem,
  MaintenanceItemPayload,
} from "../types/maintenance";

import type {
  ServiceReceipt,
  ServiceRecord,
  ServiceRecordPayload,
} from "../types/service";

import type {
  GarageVehicle,
  MotHistoryRefreshResponse,
  MotTest,
  VehicleCheckResponse,
  VehicleImportResponse,
} from "../types/vehicle";


const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL ??
  "http://localhost:8000/api/v1";


interface ApiErrorResponse {
  detail?: string;
}


export class ApiError extends Error {
  status: number;

  constructor(
    status: number,
    message: string,
  ) {
    super(message);

    this.name = "ApiError";
    this.status = status;
  }
}


async function apiRequest<T>(
  path: string,
  options: RequestInit = {},
): Promise<T> {
  const headers =
    new Headers(
      options.headers,
    );

  /*
   * FormData needs to set its own multipart
   * boundary, so JSON headers are only added
   * to normal API requests.
   */
  if (
    !(options.body instanceof FormData)
    && !headers.has(
      "Content-Type"
    )
  ) {
    headers.set(
      "Content-Type",
      "application/json",
    );
  }

  const response = await fetch(
    `${API_BASE_URL}${path}`,
    {
      ...options,

      credentials: "include",

      headers,
    },
  );

  if (!response.ok) {
    let message =
      "Something went wrong";

    try {
      const body =
        (
          await response.json()
        ) as ApiErrorResponse;

      if (body.detail) {
        message =
          body.detail;
      }

    } catch {
      // Some server errors do not return JSON.
    }

    throw new ApiError(
      response.status,
      message,
    );
  }

  if (
    response.status === 204
  ) {
    return undefined as T;
  }

  return (
    response.json() as Promise<T>
  );
}


/* Authentication */


export function registerUser(
  email: string,
  password: string,
): Promise<User> {
  return apiRequest<User>(
    "/auth/register",
    {
      method: "POST",

      body: JSON.stringify({
        email,
        password,
      }),
    },
  );
}


export function loginUser(
  email: string,
  password: string,
): Promise<User> {
  return apiRequest<User>(
    "/auth/login",
    {
      method: "POST",

      body: JSON.stringify({
        email,
        password,
      }),
    },
  );
}


export function logoutUser():
  Promise<void> {
  return apiRequest<void>(
    "/auth/logout",
    {
      method: "POST",
    },
  );
}


export function getCurrentUser():
  Promise<User> {
  return apiRequest<User>(
    "/auth/me",
  );
}


/* Vehicle checks */


export async function checkVehicle(
  registration: string,
): Promise<VehicleCheckResponse> {
  const result =
    await apiRequest<VehicleCheckResponse>(
      "/vehicle-checks",
      {
        method: "POST",

        body: JSON.stringify({
          registration,
        }),
      },
    );

  /*
   * Check history is deliberately separate from
   * the DVSA lookup. Anonymous users get no
   * persisted history and a history failure should
   * not break a successful vehicle check.
   */
  try {
    await saveVehicleCheckHistory({
      registration:
        result.registration,

      make:
        result.make ?? null,

      model:
        result.model ?? null,

      fuel_type:
        result.fuel_type ?? null,

      colour:
        result.colour ?? null,

      year:
        result.year ?? null,
    });

  } catch {
    // The live vehicle result should still be usable.
  }

  return result;
}


/* My Checks */


export function saveVehicleCheckHistory(
  payload: VehicleCheckHistoryPayload,
): Promise<
  VehicleCheckHistoryItem | null
> {
  return apiRequest<
    VehicleCheckHistoryItem | null
  >(
    "/vehicle-checks/history",
    {
      method: "POST",

      body: JSON.stringify(
        payload,
      ),
    },
  );
}


export function getVehicleCheckHistory():
  Promise<VehicleCheckHistoryItem[]> {
  return apiRequest<
    VehicleCheckHistoryItem[]
  >(
    "/vehicle-checks/history",
  );
}


export function deleteVehicleCheckHistoryItem(
  checkId: number,
): Promise<void> {
  return apiRequest<void>(
    (
      "/vehicle-checks/history/"
      + checkId
    ),
    {
      method: "DELETE",
    },
  );
}


export function clearVehicleCheckHistory():
  Promise<void> {
  return apiRequest<void>(
    "/vehicle-checks/history",
    {
      method: "DELETE",
    },
  );
}


/* My Vehicles */


export function addVehicleToGarage(
  registration: string,
): Promise<VehicleImportResponse> {
  return apiRequest<VehicleImportResponse>(
    "/vehicles/import",
    {
      method: "POST",

      body: JSON.stringify({
        registration,
      }),
    },
  );
}


export function getGarageVehicles():
  Promise<GarageVehicle[]> {
  return apiRequest<GarageVehicle[]>(
    "/vehicles",
  );
}


export function getGarageVehicle(
  vehicleId: number,
): Promise<GarageVehicle> {
  return apiRequest<GarageVehicle>(
    `/vehicles/${vehicleId}`,
  );
}


export function getVehicleMotHistory(
  vehicleId: number,
): Promise<MotTest[]> {
  return apiRequest<MotTest[]>(
    `/vehicles/${vehicleId}/mot-history`,
  );
}


export function refreshVehicleMotHistory(
  vehicleId: number,
): Promise<MotHistoryRefreshResponse> {
  return apiRequest<MotHistoryRefreshResponse>(
    `/vehicles/${vehicleId}/mot-history/refresh`,
    {
      method: "POST",
    },
  );
}


export function deleteGarageVehicle(
  vehicleId: number,
): Promise<void> {
  return apiRequest<void>(
    `/vehicles/${vehicleId}`,
    {
      method: "DELETE",
    },
  );
}


/* Service history */


export function getServiceRecords(
  vehicleId: number,
): Promise<ServiceRecord[]> {
  return apiRequest<ServiceRecord[]>(
    `/vehicles/${vehicleId}/service-records`,
  );
}


export function createServiceRecord(
  vehicleId: number,
  payload: ServiceRecordPayload,
): Promise<ServiceRecord> {
  return apiRequest<ServiceRecord>(
    `/vehicles/${vehicleId}/service-records`,
    {
      method: "POST",

      body: JSON.stringify(
        payload,
      ),
    },
  );
}


export function updateServiceRecord(
  vehicleId: number,
  recordId: number,
  payload: Partial<ServiceRecordPayload>,
): Promise<ServiceRecord> {
  return apiRequest<ServiceRecord>(
    (
      `/vehicles/${vehicleId}/service-records/`
      + recordId
    ),
    {
      method: "PUT",

      body: JSON.stringify(
        payload,
      ),
    },
  );
}


export function deleteServiceRecord(
  vehicleId: number,
  recordId: number,
): Promise<void> {
  return apiRequest<void>(
    (
      `/vehicles/${vehicleId}/service-records/`
      + recordId
    ),
    {
      method: "DELETE",
    },
  );
}


export function uploadServiceReceipt(
  vehicleId: number,
  recordId: number,
  file: File,
): Promise<ServiceReceipt> {
  const formData =
    new FormData();

  formData.append(
    "file",
    file,
  );

  return apiRequest<ServiceReceipt>(
    (
      `/vehicles/${vehicleId}/service-records/`
      + `${recordId}/receipts`
    ),
    {
      method: "POST",
      body: formData,
    },
  );
}


export function deleteServiceReceipt(
  vehicleId: number,
  recordId: number,
  receiptId: number,
): Promise<void> {
  return apiRequest<void>(
    (
      `/vehicles/${vehicleId}/service-records/`
      + `${recordId}/receipts/${receiptId}`
    ),
    {
      method: "DELETE",
    },
  );
}


export function getServiceReceiptUrl(
  vehicleId: number,
  recordId: number,
  receiptId: number,
): string {
  return (
    `${API_BASE_URL}/vehicles/${vehicleId}`
    + `/service-records/${recordId}`
    + `/receipts/${receiptId}/file`
  );
}


/* Maintenance */


export function getMaintenanceItems(
  vehicleId: number,
): Promise<MaintenanceItem[]> {
  return apiRequest<MaintenanceItem[]>(
    `/vehicles/${vehicleId}/maintenance`,
  );
}


export function createMaintenanceItem(
  vehicleId: number,
  payload: MaintenanceItemPayload,
): Promise<MaintenanceItem> {
  return apiRequest<MaintenanceItem>(
    `/vehicles/${vehicleId}/maintenance`,
    {
      method: "POST",

      body: JSON.stringify(
        payload,
      ),
    },
  );
}


export function updateMaintenanceItem(
  vehicleId: number,
  itemId: number,
  payload: Partial<MaintenanceItemPayload>,
): Promise<MaintenanceItem> {
  return apiRequest<MaintenanceItem>(
    (
      `/vehicles/${vehicleId}/maintenance/`
      + itemId
    ),
    {
      method: "PUT",

      body: JSON.stringify(
        payload,
      ),
    },
  );
}


export function deleteMaintenanceItem(
  vehicleId: number,
  itemId: number,
): Promise<void> {
  return apiRequest<void>(
    (
      `/vehicles/${vehicleId}/maintenance/`
      + itemId
    ),
    {
      method: "DELETE",
    },
  );
}