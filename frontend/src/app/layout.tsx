import type {
  Metadata,
} from "next";

import {
  AuthProvider,
} from "../contexts/AuthContext";

import "./globals.css";


export const metadata: Metadata = {
  title:
    "MyGarage UK | Vehicle MOT Checker",

  description:
    "Check UK vehicle MOT history, mileage and recorded defects.",
};


export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en-GB">
      <body>
        <AuthProvider>
          {children}
        </AuthProvider>
      </body>
    </html>
  );
}