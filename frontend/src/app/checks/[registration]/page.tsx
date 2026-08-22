import VehicleChecker from "../../../features/vehicle-check/VehicleChecker";


interface VehicleCheckPageProps {
  params: Promise<{
    registration: string;
  }>;
}


export default async function VehicleCheckPage({
  params,
}: VehicleCheckPageProps) {
  const {
    registration,
  } =
    await params;

  const cleanRegistration =
    registration
      .replace(
        /\s+/g,
        "",
      )
      .toUpperCase();

  return (
    <VehicleChecker
      initialRegistration={
        cleanRegistration
      }
      autoCheck
      resultOnly
      activePage="checks"
      backHref="/checks"
      backLabel="Back to My Checks"
    />
  );
}