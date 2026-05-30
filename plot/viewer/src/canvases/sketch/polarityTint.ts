/**
 * v0.28.2 (D-2026-05-30-E) — negative-case (failure) tint for `step`.
 *
 * A `step.polarity` of "negative" tints the node red (failure result),
 * "positive" green (success result). "neutral" (the default) and any
 * unknown / missing value return null so the caller keeps the user's
 * own colour — the tint is opt-in, preserving PHILOSOPHY P10 (the user
 * controls every colour) until they explicitly mark polarity.
 */
export function polarityTint(polarity: string | null | undefined): string | null {
  if (polarity === "negative") return "#fee2e2"; // red-100
  if (polarity === "positive") return "#dcfce7"; // green-100
  return null;
}
