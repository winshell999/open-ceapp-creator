# Refactor handoff

## Delivered

- Rewritten SKILL.md: evidence-first workflow, smallest profile, reusable implementation, mandatory release gates.
- A safe public bridge adapter, bounded errors, distinct file identities, single-flight mutations and late-result reconciliation.
- A blocking-runJob-aware controller with pre-submit full-event subscription, ownership checks and real terminal-state handling.
- Standard-library Python CLI with actual output files and atomic success/error JSON.
- A bilingual local desktop UI with light/dark themes, complete error/empty/cancel/unknown states and nine functional panels.
- Nine standalone generated source demos; exact manifests and no fabricated required shared dataset IDs.
- Public method inventory, opt-in advanced examples, scaffolder, structural validator, contract auditor, regression tests and a native acceptance matrix.

## Files to open

Read SKILL.md for the skill. Open assets/starter/index.html for the full Lab. Package exactly one assets/demos/<profile> directory for native acceptance.
The new ZIP is a complete skill, not a patch. Original MIT attribution is retained. The previous Canvas contents remain under backups/pre-refactor-20260926.

## Important behavioral changes

The new helper API is CEI18n.create(). Migrate helper and callers together in older apps. Bridge errors no longer silently become demo success. AI/phone/notification effects only follow explicit actions. Unknown outcomes block automatic resubmission. Shared data is opt-in with exact IDs.
The new Lab has its own simple demo mark and product-workbench layout. The provided landing-page design skill was applied only where its scope fits; no marketing hero, remote fonts or runtime design framework was added.

## External dependencies and unresolved gates

The CanEngine host source was read but not modified. Its current public API is the boundary. This work does not install runtimes, authorize real AI, connect a phone or sign/install a CEAPP.
Read reports/VALIDATION_REPORT.md for precise passed/simulated/not-run checks. Native testing is still required on the user's installed OS builds and configured bridges.
