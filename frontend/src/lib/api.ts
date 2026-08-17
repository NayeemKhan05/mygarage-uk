import type {
  User,
} from "../types/auth";

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
  const response = await fetch(
    `${API_BASE_URL}${path}`,
    {
      ...options,

      // Authentication is stored in an HttpOnly cookie.
      credentials: "include",

      headers: {
        "Content-Type": "application/json",
        ...options.headers,
      },
    },
  );

  if (!response.ok) {
    let message = "Something went wrong";

    try {
      const body =
        (await response.json()) as ApiErrorResponse;

      if (body.detail) {
        message = body.detail;
      }
    } catch {
      // Some server errors do not return JSON.
    }

    throw new ApiError(
      response.status,
      message,
    );
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return response.json() as Promise<T>;
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


export function checkVehicle(
  registration: string,
): Promise<VehicleCheckResponse> {
  return apiRequest<VehicleCheckResponse>(
    "/vehicle-checks",
    {
      method: "POST",
      body: JSON.stringify({
        registration,
      }),
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