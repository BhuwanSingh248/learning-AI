import { describe, expect, it } from "vitest";
import { normalizeSymbols } from "@/features/analysis/schemas";

describe("normalizeSymbols", () => {
  it("normalizes separators and deduplicates symbols", () => {
    expect(normalizeSymbols(" aapl, msft\nAAPL   nvda ")).toEqual([
      "AAPL",
      "MSFT",
      "NVDA",
    ]);
  });
});
