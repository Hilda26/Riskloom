import type { Metadata } from "next";
import { Space_Grotesk, Inter, JetBrains_Mono } from "next/font/google";
import "./globals.css";
import { Providers } from "./providers";

const spaceGrotesk = Space_Grotesk({
  subsets: ["latin"],
  weight: ["300", "400", "500", "600", "700"],
  variable: "--font-sg",
});
const inter = Inter({
  subsets: ["latin"],
  weight: ["400", "500", "600"],
  variable: "--font-body",
});
const jetbrainsMono = JetBrains_Mono({
  subsets: ["latin"],
  weight: ["400", "500"],
  variable: "--font-mono",
});

export const metadata: Metadata = {
  title: "Riskloom - Stablecoin Risk Intelligence",
  description:
    "Riskloom continuously analyzes reserves, issuer health, peg stability, and regulatory exposure - publishing real-time StableScore ratings on-chain for every major stablecoin.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html
      lang="en"
      className={`${spaceGrotesk.variable} ${inter.variable} ${jetbrainsMono.variable}`}
    >
      <body>
        <div className="loom-bg" />
        <div className="orbs">
          <div className="orb orb-a" />
          <div className="orb orb-i" />
          <div className="orb orb-m" />
        </div>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
