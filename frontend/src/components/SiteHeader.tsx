"use client";

import Link from "next/link";

import {
  useRouter,
} from "next/navigation";

import {
  useAuth,
} from "../contexts/AuthContext";

import styles from "./SiteHeader.module.css";


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
  const router =
    useRouter();

  const {
    user,
    loading,
    logout,
  } = useAuth();


  async function handleLogout() {
    await logout();

    router.push("/");
    router.refresh();
  }


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

        <div className={styles.rightSide}>
          <nav
            className="site-nav"
            aria-label="Main navigation"
          >
            {navigation.map(
              (item) => (
                <Link
                  key={item.page}
                  href={item.href}
                  className={
                    activePage ===
                    item.page
                      ? "nav-link active"
                      : "nav-link"
                  }
                >
                  {item.label}
                </Link>
              ),
            )}
          </nav>

          <div className={styles.authArea}>
            {!loading && !user && (
              <Link
                href="/login"
                className={styles.signInLink}
              >
                Sign in
              </Link>
            )}

            {!loading && user && (
              <>
                <span
                  className={styles.userEmail}
                  title={user.email}
                >
                  {user.email}
                </span>

                <button
                  type="button"
                  className={styles.logoutButton}
                  onClick={handleLogout}
                >
                  Log out
                </button>
              </>
            )}
          </div>
        </div>
      </div>
    </header>
  );
}