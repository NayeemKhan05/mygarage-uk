import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "MyGarage UK",
  description: "Your UK vehicle history and maintenance hub",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
