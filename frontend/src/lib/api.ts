import type {
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

  constructor(status: number, message: string) {
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
      // Some server errors do not have a JSON response.
    }

    throw new ApiError(
      response.status,
      message,
    );
  }

  return response.json() as Promise<T>;
}


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