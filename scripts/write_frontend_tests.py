"""
StableShield AI - Frontend Test Writer (STEP 8)
Writes vitest config + unit tests, and Playwright config + e2e tests.
Run from the repository root: python scripts/write_frontend_tests.py
Safe to re-run: existing files are never overwritten.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WEB = ROOT / "apps" / "web"

FILES = {

"vitest.config.ts": """\
import { defineConfig } from "vitest/config";
import react from "@vitejs/plugin-react";
import path from "path";

export default defineConfig({
  plugins: [react()],
  test: {
    environment: "jsdom",
    include: ["tests/unit/**/*.test.{ts,tsx}"],
  },
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "."),
      "@stableshield/shared-types": path.resolve(__dirname, "../../packages/shared-types"),
    },
  },
});
""",

"playwright.config.ts": """\
import { defineConfig } from "@playwright/test";

export default defineConfig({
  testDir: "./tests/e2e",
  timeout: 30_000,
  retries: 0,
  use: {
    baseURL: process.env.E2E_BASE_URL ?? "http://localhost:3000",
    headless: true,
  },
});
""",

"tests/unit/format.test.ts": """\
import { describe, expect, it } from "vitest";
import { formatPegPrice, formatMarketCap, pegPriceClass } from "@/lib/format";

describe("formatPegPrice", () => {
  it("formats with 4 decimal places and a dollar sign", () => {
    expect(formatPegPrice(1.0001)).toBe("$1.0001");
    expect(formatPegPrice(0.9801)).toBe("$0.9801");
    expect(formatPegPrice(1)).toBe("$1.0000");
  });
});

describe("pegPriceClass", () => {
  it("classifies prices within half a cent of peg as safe", () => {
    expect(pegPriceClass(1.0001)).toBe("safe");
    expect(pegPriceClass(0.9999)).toBe("safe");
    expect(pegPriceClass(1)).toBe("safe");
  });

  it("classifies moderate deviation as warn", () => {
    expect(pegPriceClass(0.99)).toBe("warn-c");
    expect(pegPriceClass(1.008)).toBe("warn-c");
  });

  it("classifies severe deviation as danger", () => {
    expect(pegPriceClass(0.9801)).toBe("danger-c");
    expect(pegPriceClass(0.5)).toBe("danger-c");
  });
});

describe("formatMarketCap", () => {
  it("returns -- for null", () => {
    expect(formatMarketCap(null)).toBe("--");
  });

  it("formats billions with one decimal", () => {
    expect(formatMarketCap(43_200_000_000)).toBe("$43.2B");
  });

  it("formats millions with no decimals", () => {
    expect(formatMarketCap(643_000_000)).toBe("$643M");
    expect(formatMarketCap(28_000_000)).toBe("$28M");
  });

  it("formats sub-million values as a raw dollar figure", () => {
    expect(formatMarketCap(500)).toBe("$500");
  });
});
""",

"tests/unit/RatingPill.test.tsx": """\
import { describe, expect, it } from "vitest";
import { render, screen } from "@testing-library/react";
import { RatingPill, riskLevelForGrade, ratingBarFillClass } from "@/components/ui/RatingPill";

describe("RatingPill", () => {
  it("renders the grade text", () => {
    render(<RatingPill grade="AAA" />);
    expect(screen.getByText("AAA")).toBeInTheDocument();
  });
});

describe("riskLevelForGrade", () => {
  it("classifies AAA/AA/A as low risk", () => {
    expect(riskLevelForGrade("AAA")).toBe("low");
    expect(riskLevelForGrade("AA")).toBe("low");
    expect(riskLevelForGrade("A")).toBe("low");
  });

  it("classifies BBB/BB as medium risk", () => {
    expect(riskLevelForGrade("BBB")).toBe("medium");
    expect(riskLevelForGrade("BB")).toBe("medium");
  });

  it("classifies B/CCC/D as critical", () => {
    expect(riskLevelForGrade("B")).toBe("critical");
    expect(riskLevelForGrade("CCC")).toBe("critical");
    expect(riskLevelForGrade("D")).toBe("critical");
  });
});

describe("ratingBarFillClass", () => {
  it("maps risk level to the matching bar fill class", () => {
    expect(ratingBarFillClass("AAA")).toBe("rb-safe");
    expect(ratingBarFillClass("BBB")).toBe("rb-warn");
    expect(ratingBarFillClass("D")).toBe("rb-danger");
  });
});
""",

"tests/e2e/landing.spec.ts": """\
import { test, expect } from \"@playwright/test\";

test(\"landing page renders hero, ticker, and StableScore band\", async ({ page }) => {
  await page.goto(\"/\");

  await expect(page.locator(\"h1.ht\")).toContainText(\"stablecoin\");
  await expect(page.locator(\".ticker\")).toBeVisible();
  await expect(page.locator(\".sb-inner\")).toBeVisible();
  await expect(page.locator(\".ratings-row .rating-slot\")).toHaveCount(8);
});

test(\"hero CTA links to the dashboard\", async ({ page }) => {
  await page.goto(\"/\");
  const cta = page.getByRole(\"link\", { name: /Explore the Dashboard/i });
  await expect(cta).toHaveAttribute(\"href\", \"/dashboard\");
});
""",

"tests/e2e/dashboard.spec.ts": """\
import { test, expect } from \"@playwright/test\";

test(\"dashboard requires a connected wallet\", async ({ page }) => {
  await page.goto(\"/dashboard\");
  await expect(
    page.getByText(/Connect a wallet to access the risk intelligence dashboard/i),
  ).toBeVisible();
});
""",
}


def main() -> None:
    created = []
    for rel, content in FILES.items():
        path = WEB / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        if not path.exists():
            path.write_text(content, encoding="utf-8")
            created.append(rel)

    print(f"Web root: {WEB}")
    print(f"Created {len(created)} file(s).")
    for f in created:
        print(f"  + {f}")
    if not created:
        print("Nothing to do - all files already exist.")


if __name__ == "__main__":
    main()
