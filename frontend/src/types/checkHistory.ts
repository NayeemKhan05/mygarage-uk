export interface VehicleCheckHistoryItem {
  id: number;

  registration: string;

  make: string | null;
  model: string | null;

  fuel_type: string | null;
  colour: string | null;
  year: number | null;

  first_checked_at: string;
  last_checked_at: string;

  check_count: number;

  in_garage: boolean;
  garage_vehicle_id: number | null;
}


export interface VehicleCheckHistoryPayload {
  registration: string;

  make: string | null;
  model: string | null;

  fuel_type: string | null;
  colour: string | null;
  year: number | null;
}