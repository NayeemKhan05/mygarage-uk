import type {
  Metadata,
} from "next";

import "./globals.css";
import "../styles/numberPlate.css";

import {
  AuthProvider,
} from "../contexts/AuthContext";


export const metadata:
  Metadata = {
  title: "MyGarage UK",

  description:
    "Check, save and manage your UK vehicles.",
};


export default function RootLayout({
  children,
}: Readonly<{
  children:
    React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>
        <AuthProvider>
          {children}
        </AuthProvider>
      </body>
    </html>
  );
}