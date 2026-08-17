export type ServiceCategory =
  | "service"
  | "repair"
  | "maintenance"
  | "parts"
  | "inspection"
  | "other";


export interface ServiceReceipt {
  id: number;

  original_filename: string;
  content_type: string;
  size_bytes: number;

  created_at: string;
}


export interface ServiceRecord {
  id: number;
  vehicle_id: number;

  service_date: string;

  title: string;
  category: ServiceCategory;

  mileage: number | null;
  garage: string | null;
  cost: number | null;
  notes: string | null;

  receipts: ServiceReceipt[];

  created_at: string;
  updated_at: string;
}


export interface ServiceRecordPayload {
  service_date: string;

  title: string;
  category: ServiceCategory;

  mileage: number | null;
  garage: string | null;
  cost: number | null;
  notes: string | null;
}