import { test, expect } from "@playwright/test";

test("landing page renders hero, ticker, and StableScore band", async ({ page }) => {
  await page.goto("/");

  await expect(page.locator("h1.ht")).toContainText("stablecoin");
  await expect(page.locator(".ticker")).toBeVisible();
  await expect(page.locator(".sb-inner")).toBeVisible();
  await expect(page.locator(".ratings-row .rating-slot")).toHaveCount(8);
});

test("hero CTA links to the dashboard", async ({ page }) => {
  await page.goto("/");
  const cta = page.getByRole("link", { name: /Explore the Dashboard/i });
  await expect(cta).toHaveAttribute("href", "/dashboard");
});
