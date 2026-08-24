export type ReminderKind =
  | "mot"
  | "maintenance";


export type ReminderSeverity =
  | "urgent"
  | "warning";


export interface Reminder {
  reminder_key: string;

  kind: ReminderKind;
  severity: ReminderSeverity;

  title: string;
  message: string;

  vehicle_id: number;

  registration: string;

  make: string | null;
  model: string | null;

  due_date: string | null;

  due_mileage: number | null;
  current_mileage: number | null;

  action_href: string;
}


export interface ReminderSummary {
  total: number;

  urgent: number;
  warning: number;

  mot: number;
  maintenance: number;
}


export interface ReminderSettings {
  user_id: number;

  mot_enabled: boolean;
  maintenance_enabled: boolean;

  due_soon_days: number;
  due_soon_miles: number;

  created_at: string;
  updated_at: string;
}


export interface ReminderSettingsPayload {
  mot_enabled?: boolean;

  maintenance_enabled?: boolean;

  due_soon_days?: number;
  due_soon_miles?: number;
}