export type MaintenanceCategory =
  | "oil"
  | "filters"
  | "brakes"
  | "tyres"
  | "fluids"
  | "belts"
  | "battery"
  | "suspension"
  | "general"
  | "other";


export type MaintenanceStatus =
  | "good"
  | "due_soon"
  | "overdue"
  | "unknown";


export interface MaintenanceItem {
  id: number;
  vehicle_id: number;

  name: string;
  category: MaintenanceCategory;

  last_completed_date: string | null;
  last_completed_mileage: number | null;

  next_due_date: string | null;
  next_due_mileage: number | null;

  notes: string | null;

  status: MaintenanceStatus;
  status_reason: string;

  current_mileage: number | null;

  created_at: string;
  updated_at: string;
}


export interface MaintenanceItemPayload {
  name: string;
  category: MaintenanceCategory;

  last_completed_date: string | null;
  last_completed_mileage: number | null;

  next_due_date: string | null;
  next_due_mileage: number | null;

  notes: string | null;
}