import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Temper Risk Management",
  description: "ISO 31000 / ISO 27001:2022 Risk Management Platform",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-gray-50 text-gray-900 antialiased">
        {children}
      </body>
    </html>
  );
}
