import SiteHeader from "../../components/SiteHeader";


export default function ChecksPage() {
  return (
    <div className="site-shell">
      <SiteHeader
        activePage="checks"
      />

      <main className="placeholder-page">
        <div className="placeholder-content">
          <span className="eyebrow">
            My Checks
          </span>

          <h1>
            Your vehicle checks will
            live here.
          </h1>

          <p>
            We&apos;ll build saved and
            recent vehicle checks in a
            later milestone.
          </p>
        </div>
      </main>
    </div>
  );
}