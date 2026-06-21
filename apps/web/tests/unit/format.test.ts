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
