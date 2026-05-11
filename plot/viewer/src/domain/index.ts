/**
 * Plot v0.15 domain layer — per-kind entity classes + discriminated-union
 * dispatch (mirrors ``plot_mcp/models.py``).
 *
 * Phase 2.0: scaffolding only. Phase 2.1+ adds one entity class per
 * commit (Mission, CoreValue, Identity, Actor, Service, …); each class
 * registers itself via ``registerKindParser`` on module load.
 */
export { DomainParseError } from "./DomainParseError";
export type { BaseFields, BaseFieldsJson } from "./BaseFields";
export { parseBaseFields } from "./BaseFields";
export { parseEntity, registerKindParser, registeredKinds } from "./parseEntity";
