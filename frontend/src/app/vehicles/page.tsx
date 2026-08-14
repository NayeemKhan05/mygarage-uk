import SiteHeader from "../../components/SiteHeader";


export default function VehiclesPage() {
  return (
    <div className="site-shell">
      <SiteHeader
        activePage="vehicles"
      />

      <main className="placeholder-page">
        <div className="placeholder-content">
          <span className="eyebrow">
            My Vehicles
          </span>

          <h1>
            Your saved vehicles will
            live here.
          </h1>

          <p>
            We&apos;ll turn this into
            the full My Vehicles
            dashboard in the next
            stages of the project.
          </p>
        </div>
      </main>
    </div>
  );
}