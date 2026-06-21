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
