import type {
  AiQuestionResponse,
  AiStatus,
  AiVehicleInsights,
  AiVehicleSnapshot,
} from "../types/ai";


const API_BASE_URL =
  process.env
    .NEXT_PUBLIC_API_URL
  ?? (
    "http://localhost:"
    + "8000/api/v1"
  );


interface ErrorResponse {
  detail?: string;
}


export class AiApiError
  extends Error {
  status:
    number;


  constructor(
    status:
      number,

    message:
      string,
  ) {
    super(
      message
    );

    this.name =
      "AiApiError";

    this.status =
      status;
  }
}


async function aiRequest<T>(
  path:
    string,

  options:
    RequestInit = {},
): Promise<T> {
  const headers =
    new Headers(
      options.headers,
    );

  headers.set(
    "Content-Type",
    "application/json",
  );

  const response =
    await fetch(
      `${API_BASE_URL}${path}`,
      {
        ...options,

        credentials:
          "include",

        headers,
      },
    );

  if (!response.ok) {
    let message =
      (
        "AI insights are "
        + "currently unavailable."
      );

    try {
      const body:
        ErrorResponse =
          await response.json();

      if (
        body.detail
      ) {
        message =
          body.detail;
      }

    } catch {
      // Some errors do not contain JSON.
    }

    throw new AiApiError(
      response.status,
      message,
    );
  }

  const data: T =
    await response.json();

  return data;
}


export function getAiStatus():
  Promise<AiStatus> {
  return aiRequest<
    AiStatus
  >(
    "/ai/status"
  );
}


export function generateVehicleInsights(
  vehicle:
    AiVehicleSnapshot,
): Promise<
  AiVehicleInsights
> {
  return aiRequest<
    AiVehicleInsights
  >(
    (
      "/ai/"
      + "vehicle-insights"
    ),
    {
      method:
        "POST",

      body:
        JSON.stringify({
          vehicle,
        }),
    },
  );
}


export function askVehicleQuestion(
  vehicle:
    AiVehicleSnapshot,

  question:
    string,
): Promise<
  AiQuestionResponse
> {
  return aiRequest<
    AiQuestionResponse
  >(
    (
      "/ai/"
      + "vehicle-question"
    ),
    {
      method:
        "POST",

      body:
        JSON.stringify({
          vehicle,
          question,
        }),
    },
  );
}