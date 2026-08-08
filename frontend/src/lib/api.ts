const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export async function getBackendStatus(): Promise<"online" | "offline"> {
  try {
    const response = await fetch(`${API_URL}/api/v1/health`, { cache: "no-store" });
    return response.ok ? "online" : "offline";
  } catch {
    return "offline";
  }
}
