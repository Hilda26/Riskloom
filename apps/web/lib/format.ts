export function formatPegPrice(price: number): string {
  return `$${price.toFixed(4)}`;
}

export function pegPriceClass(price: number): string {
  // Round to 6 decimal places first - floating point subtraction
  // (e.g. 1 - 0.99) can land a hair past an exact boundary otherwise.
  const deviation = Math.round(Math.abs(price - 1) * 1e6) / 1e6;
  if (deviation <= 0.0005) return "safe";
  if (deviation <= 0.01) return "warn-c";
  return "danger-c";
}

export function formatMarketCap(value: number | null): string {
  if (value === null) return "--";
  if (value >= 1_000_000_000) return `$${(value / 1_000_000_000).toFixed(1)}B`;
  if (value >= 1_000_000) return `$${(value / 1_000_000).toFixed(0)}M`;
  return `$${value.toFixed(0)}`;
}
