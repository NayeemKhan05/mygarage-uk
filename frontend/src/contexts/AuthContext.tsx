"use client";

import {
  createContext,
  ReactNode,
  useContext,
  useEffect,
  useState,
} from "react";

import {
  ApiError,
  getCurrentUser,
  loginUser,
  logoutUser,
  registerUser,
} from "../lib/api";

import type {
  User,
} from "../types/auth";


interface AuthContextValue {
  user: User | null;
  loading: boolean;

  login: (
    email: string,
    password: string,
  ) => Promise<User>;

  register: (
    email: string,
    password: string,
  ) => Promise<User>;

  logout: () => Promise<void>;
}


const AuthContext =
  createContext<AuthContextValue | null>(
    null,
  );


interface AuthProviderProps {
  children: ReactNode;
}


export function AuthProvider({
  children,
}: AuthProviderProps) {
  const [
    user,
    setUser,
  ] =
    useState<User | null>(
      null,
    );

  const [
    loading,
    setLoading,
  ] =
    useState(true);


  useEffect(() => {
    let cancelled = false;

    async function loadUser() {
      try {
        const currentUser =
          await getCurrentUser();

        if (!cancelled) {
          setUser(
            currentUser,
          );
        }
      } catch (error) {
        if (
          !cancelled &&
          error instanceof ApiError &&
          error.status === 401
        ) {
          setUser(null);
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    loadUser();

    return () => {
      cancelled = true;
    };
  }, []);


  async function login(
    email: string,
    password: string,
  ): Promise<User> {
    const loggedInUser =
      await loginUser(
        email,
        password,
      );

    setUser(
      loggedInUser,
    );

    return loggedInUser;
  }


  async function register(
    email: string,
    password: string,
  ): Promise<User> {
    const registeredUser =
      await registerUser(
        email,
        password,
      );

    setUser(
      registeredUser,
    );

    return registeredUser;
  }


  async function logout() {
    try {
      await logoutUser();
    } finally {
      setUser(null);
    }
  }


  return (
    <AuthContext.Provider
      value={{
        user,
        loading,
        login,
        register,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}


export function useAuth():
  AuthContextValue {
  const context =
    useContext(AuthContext);

  if (!context) {
    throw new Error(
      "useAuth must be used inside AuthProvider"
    );
  }

  return context;
}