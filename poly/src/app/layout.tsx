import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Poly: The Intelligent Cloud File Browser",
  description: "Store, browse, research, and organize your files with A.I. — available on web and desktop",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>
        <div className="noise-overlay" />
        {children}
      </body>
    </html>
  );
}