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
  | "vehicles"
  | "reminders";


interface SiteHeaderProps {
  activePage?: ActivePage;
}


export default function SiteHeader({
  activePage,
}: SiteHeaderProps) {
  const router =
    useRouter();

  const {
    user,
    logout,
  } =
    useAuth();


  function navClass(
    page: ActivePage,
  ): string {
    return (
      activePage === page
        ? "nav-link active"
        : "nav-link"
    );
  }


  async function handleLogout() {
    await logout();

    router.push(
      "/",
    );

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
            MyGarage UK
          </span>
        </Link>

        <div
          className={
            styles.rightSide
          }
        >
          <nav
            className="site-nav"
            aria-label="Main navigation"
          >
            <Link
              className={
                navClass(
                  "home",
                )
              }
              href="/"
            >
              Home
            </Link>

            <Link
              className={
                navClass(
                  "checks",
                )
              }
              href="/checks"
            >
              My Checks
            </Link>

            <Link
              className={
                navClass(
                  "vehicles",
                )
              }
              href="/vehicles"
            >
              My Vehicles
            </Link>

            <Link
              className={
                navClass(
                  "reminders",
                )
              }
              href="/reminders"
            >
              Reminders
            </Link>
          </nav>

          <div
            className={
              styles.authArea
            }
          >
            {user ? (
              <>
                <span
                  className={
                    styles.userEmail
                  }
                  title={
                    user.email
                  }
                >
                  {user.email}
                </span>

                <button
                  className={
                    styles.logoutButton
                  }
                  type="button"
                  onClick={
                    handleLogout
                  }
                >
                  Log out
                </button>
              </>

            ) : (
              <Link
                className={
                  styles.signInLink
                }
                href="/login"
              >
                Sign in
              </Link>
            )}
          </div>
        </div>
      </div>
    </header>
  );
}