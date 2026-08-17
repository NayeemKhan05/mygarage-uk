"use client";

import {
  FormEvent,
  useEffect,
  useState,
} from "react";

import Link from "next/link";

import {
  useRouter,
} from "next/navigation";

import SiteHeader from "../../components/SiteHeader";

import {
  useAuth,
} from "../../contexts/AuthContext";

import {
  ApiError,
} from "../../lib/api";

import styles from "./Auth.module.css";


interface AuthFormProps {
  mode:
    | "login"
    | "register";
}


export default function AuthForm({
  mode,
}: AuthFormProps) {
  const router =
    useRouter();

  const {
    user,
    loading: authLoading,
    login,
    register,
  } = useAuth();

  const [
    email,
    setEmail,
  ] = useState("");

  const [
    password,
    setPassword,
  ] = useState("");

  const [
    confirmPassword,
    setConfirmPassword,
  ] = useState("");

  const [
    submitting,
    setSubmitting,
  ] = useState(false);

  const [
    error,
    setError,
  ] =
    useState<string | null>(
      null,
    );


  const isRegister =
    mode === "register";


  useEffect(() => {
    if (
      !authLoading &&
      user
    ) {
      router.replace(
        "/vehicles"
      );
    }
  }, [
    authLoading,
    user,
    router,
  ]);


  async function handleSubmit(
    event:
      FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault();

    setError(null);

    if (
      isRegister &&
      password !==
        confirmPassword
    ) {
      setError(
        "The passwords do not match.",
      );

      return;
    }

    setSubmitting(true);

    try {
      if (isRegister) {
        await register(
          email,
          password,
        );
      } else {
        await login(
          email,
          password,
        );
      }

      router.push(
        "/vehicles"
      );
    } catch (caughtError) {
      if (
        caughtError instanceof
        ApiError
      ) {
        setError(
          caughtError.message,
        );
      } else {
        setError(
          "Something went wrong. Please try again.",
        );
      }
    } finally {
      setSubmitting(false);
    }
  }


  return (
    <div className="site-shell">
      <SiteHeader
        activePage="home"
      />

      <main className={styles.page}>
        <div className={styles.card}>
          <div className={styles.heading}>
            <span className={styles.eyebrow}>
              {isRegister
                ? "Create account"
                : "Welcome back"}
            </span>

            <h1>
              {isRegister
                ? "Create your MyGarage account."
                : "Sign in to MyGarage."}
            </h1>

            <p>
              {isRegister
                ? "Use your email address to create your account and keep your vehicles together."
                : "Sign in with your email address to access My Vehicles."}
            </p>
          </div>

          <form
            className={styles.form}
            onSubmit={handleSubmit}
          >
            <label>
              <span>
                Email address
              </span>

              <input
                type="email"
                value={email}
                onChange={(
                  event,
                ) =>
                  setEmail(
                    event.target.value
                  )
                }
                autoComplete="email"
                required
                placeholder="you@example.com"
              />
            </label>

            <label>
              <span>
                Password
              </span>

              <input
                type="password"
                value={password}
                onChange={(
                  event,
                ) =>
                  setPassword(
                    event.target.value
                  )
                }
                autoComplete={
                  isRegister
                    ? "new-password"
                    : "current-password"
                }
                minLength={
                  isRegister
                    ? 8
                    : undefined
                }
                required
              />
            </label>

            {isRegister && (
              <label>
                <span>
                  Confirm password
                </span>

                <input
                  type="password"
                  value={
                    confirmPassword
                  }
                  onChange={(
                    event,
                  ) =>
                    setConfirmPassword(
                      event.target.value
                    )
                  }
                  autoComplete="new-password"
                  minLength={8}
                  required
                />
              </label>
            )}

            {isRegister && (
              <p className={styles.passwordHint}>
                Use at least 8 characters.
              </p>
            )}

            {error && (
              <div
                className={styles.error}
                role="alert"
              >
                {error}
              </div>
            )}

            <button
              type="submit"
              className={styles.submitButton}
              disabled={
                submitting ||
                authLoading
              }
            >
              {submitting
                ? isRegister
                  ? "Creating account..."
                  : "Signing in..."
                : isRegister
                  ? "Create account"
                  : "Sign in"}
            </button>
          </form>

          <div className={styles.switchMode}>
            {isRegister ? (
              <p>
                Already have an account?{" "}
                <Link href="/login">
                  Sign in
                </Link>
              </p>
            ) : (
              <p>
                New to MyGarage?{" "}
                <Link href="/register">
                  Create an account
                </Link>
              </p>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}