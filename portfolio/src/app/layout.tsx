import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "[Your Name] | Portfolio",
  description: "Software Engineer, Experimental Projects & Prototyping",
};

import Navbar from "@/components/Navbar";
import { getTree } from "@/lib/api";

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  const navTree = getTree();

  return (
    <html lang="en">
      <head>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap" rel="stylesheet" />
      </head>
      <body className="antialiased min-h-screen relative selection:bg-blue-500/30 flex flex-col font-[family-name:var(--font-inter)]">
        <div className="fixed inset-0 z-[-1] bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-blue-900/20 via-slate-900/0 to-slate-950/0 pointer-events-none" />

        <Navbar tree={navTree} />

        <main className="flex-1 w-full max-w-7xl mx-auto p-4 md:p-8">
          {children}
        </main>
      </body>
    </html>
  );
}
