import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Agent Audit System",
  description: "Real-time governance dashboard for AI agent operations",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body>{children}</body>
    </html>
  );
}
