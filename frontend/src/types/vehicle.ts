export interface MotDefect {
  text: string;
  type: string;
  dangerous: boolean;
}


export interface MotTest {
  mot_test_number: string;
  completed_at: string;

  data_source: string | null;
  expiry_date: string | null;
  registration_at_time_of_test: string | null;

  test_result: string | null;

  odometer_value: number | null;
  odometer_unit: string | null;
  odometer_result_type: string | null;

  defects: MotDefect[];
}


export interface VehicleCheckResponse {
  registration: string;
  make: string;
  model: string;

  fuel_type: string | null;
  engine_size: number | null;
  colour: string | null;
  year: number | null;

  mot_tests_found: number;
  mot_tests: MotTest[];

  in_garage: boolean;
  garage_vehicle_id: number | null;
}


export interface GarageVehicle {
  id: number;

  registration: string;
  make: string;
  model: string;

  fuel_type: string | null;
  engine_size: number | null;
  colour: string | null;
  year: number | null;

  created_at: string;
  updated_at: string;
}


export interface VehicleImportResponse {
  vehicle: GarageVehicle;

  mot_tests_found: number;
  mot_tests_saved: number;
}


export interface MotHistoryRefreshResponse {
  vehicle_id: number;
  registration: string;

  mot_tests_found: number;
  mot_tests_saved: number;
}