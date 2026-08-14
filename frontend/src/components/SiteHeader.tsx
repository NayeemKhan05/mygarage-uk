import Link from "next/link";


type ActivePage =
  | "home"
  | "checks"
  | "vehicles";


interface SiteHeaderProps {
  activePage: ActivePage;
}


const navigation = [
  {
    label: "Home",
    href: "/",
    page: "home",
  },
  {
    label: "My Checks",
    href: "/checks",
    page: "checks",
  },
  {
    label: "My Vehicles",
    href: "/vehicles",
    page: "vehicles",
  },
] as const;


export default function SiteHeader({
  activePage,
}: SiteHeaderProps) {
  return (
    <header className="site-header">
      <div className="header-inner">
        <Link
          className="brand"
          href="/"
        >
          <span className="brand-mark">
            MG
          </span>

          <span>
            MyGarage
            <strong> UK</strong>
          </span>
        </Link>

        <nav
          className="site-nav"
          aria-label="Main navigation"
        >
          {navigation.map((item) => (
            <Link
              key={item.page}
              href={item.href}
              className={
                activePage === item.page
                  ? "nav-link active"
                  : "nav-link"
              }
            >
              {item.label}
            </Link>
          ))}
        </nav>
      </div>
    </header>
  );
}