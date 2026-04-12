import type { Metadata } from "next";
import { AppProviders } from "@/components/providers/app-providers";
import { env } from "@/lib/env";
import "./globals.css";

export const metadata: Metadata = {
  title: env.appName,
  description: "Next.js dashboard for validating AI stock suggestions.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>
        <AppProviders>{children}</AppProviders>
      </body>
    </html>
  );
}
