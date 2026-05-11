/**
 * Thrown by per-kind ``Class.fromJson(raw)`` parsers and by
 * ``parseEntity(raw)`` when raw input fails the entity-class invariants.
 *
 * Distinct from generic ``Error`` so callers (especially ``api.ts``) can
 * ``instanceof DomainParseError`` to separate wire-shape failures from
 * network / HTTP errors.
 */
export class DomainParseError extends Error {
  /** The raw input that failed to parse — kept on the error so the
   *  caller can surface it in a debugger / log without re-deriving. */
  readonly raw: unknown;

  constructor(message: string, raw?: unknown) {
    super(message);
    this.name = "DomainParseError";
    this.raw = raw;
  }
}
