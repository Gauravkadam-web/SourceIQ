import type { Metadata } from "next";
import { Inter, JetBrains_Mono } from "next/font/google";
import "../styles/globals.css";
import { WorkspaceProvider } from "../context/WorkspaceContext";
import Navbar from "../components/Navbar";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-sans",
  display: "swap",
});

const jetbrainsMono = JetBrains_Mono({
  subsets: ["latin"],
  variable: "--font-mono",
  display: "swap",
});

export const metadata: Metadata = {
  title: "SourceIQ — AI Answers. Verifiable Sources.",
  description:
    "Evidence-first document intelligence platform grounding answers in retrieved PDF evidence, validating citation references, and communicating uncertainty.",
  icons: {
    icon: "/favicon.ico",
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className={`${inter.variable} ${jetbrainsMono.variable}`}>
      <head>
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
      </head>
      <body>
        <WorkspaceProvider>
          <div style={{ minHeight: "100vh", display: "flex", flexDirection: "column" }}>
            <Navbar />
            <main
              style={{
                flex: 1,
                maxWidth: "1400px",
                width: "100%",
                margin: "0 auto",
                padding: "32px 24px",
              }}
            >
              {children}
            </main>
            <footer
              style={{
                borderTop: "1px solid var(--border-subtle)",
                padding: "20px 24px",
                textAlign: "center",
                color: "var(--text-muted)",
                fontSize: "0.8rem",
              }}
            >
              <div style={{ maxWidth: "1400px", margin: "0 auto", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                <span>SourceIQ — AI Answers. Verifiable Sources.</span>
                <span>Grounds answers in retrieved evidence & validates citations.</span>
              </div>
            </footer>
          </div>
        </WorkspaceProvider>
      </body>
    </html>
  );
}
