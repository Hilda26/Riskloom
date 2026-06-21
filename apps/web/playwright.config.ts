import { defineConfig } from "@playwright/test";

export default defineConfig({
  testDir: "./tests/e2e",
  // Generous timeout/workers=1: against `next dev` the first hit on any
  // route pays Next's on-demand compile cost (10-20s is normal), and
  // running serially avoids two first-compiles contending for CPU at
  // once. Production (`next start`) serves precompiled output and
  // would not need this headroom.
  timeout: 60_000,
  workers: 1,
  retries: 0,
  use: {
    baseURL: process.env.E2E_BASE_URL ?? "http://localhost:3000",
    headless: true,
    navigationTimeout: 60_000,
  },
});
