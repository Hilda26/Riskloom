import { test, expect } from "@playwright/test";

test("dashboard requires a connected wallet", async ({ page }) => {
  await page.goto("/dashboard");
  await expect(
    page.getByText(/Connect a wallet to access the risk intelligence dashboard/i),
  ).toBeVisible();
});
