export type AiTone =
  | "positive"
  | "neutral"
  | "watch"
  | "attention";


export type AiInsightLevel =
  | "positive"
  | "info"
  | "watch"
  | "attention";


export interface AiDefectSnapshot {
  text: string;

  type:
    string | null;

  dangerous:
    boolean;
}


export interface AiMotTestSnapshot {
  completed_at:
    string | null;

  test_result:
    string | null;

  expiry_date:
    string | null;

  odometer_value:
    number | null;

  odometer_unit:
    string | null;

  mot_test_number:
    string | null;

  defects:
    AiDefectSnapshot[];
}


export interface AiVehicleSnapshot {
  registration:
    string;

  make:
    string | null;

  model:
    string | null;

  fuel_type:
    string | null;

  engine_size:
    number | null;

  colour:
    string | null;

  year:
    number | null;

  mot_tests:
    AiMotTestSnapshot[];

  supplementary_service_records?:
    unknown[];

  supplementary_maintenance_items?:
    unknown[];
}


export interface AiMotStats {
  tests: number;

  passed: number;
  failed: number;

  recorded_items: number;

  dangerous: number;
  major: number;
  minor: number;
  advisory: number;
  prs: number;

  mileage_points: number;

  mileage_decreases: number;
}


export interface AiInsightItem {
  title: string;

  detail: string;

  level:
    AiInsightLevel;

  evidence: string;
}


export interface AiRecurringItem {
  label: string;

  count: number;

  latest_date:
    string | null;
}


export interface AiVehicleInsights {
  overall_tone:
    AiTone;

  summary: string;

  mot_stats:
    AiMotStats;

  insights:
    AiInsightItem[];

  recurring_items:
    AiRecurringItem[];

  mileage_analysis:
    string;

  supplementary_note:
    string | null;

  disclaimer:
    string;
}


export interface AiQuestionResponse {
  answer: string;

  disclaimer: string;
}


export interface AiStatus {
  available: boolean;

  model: string;

  message: string;
}