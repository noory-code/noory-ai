/**
 * Foundation reference kinds — the consumer-plane Symbol refs whose
 * outgoing edges express essence **injection** onto a flow
 * (D-2026-05-30-D). `actor_ref` is deliberately excluded: it is the
 * sequence *subject*, not a foundation overlay.
 *
 * SSOT shared by the injection edge styling (`edgeTransform`) and the
 * layout anchoring (`actorAnchoredLayout`, D-2026-05-30-G) so the two
 * never drift on what counts as an injection.
 */
export const FOUNDATION_REF_KINDS: ReadonlySet<string> = new Set([
  "mission_ref",
  "value_ref",
  "identity_ref",
]);
