# Standard CEAPP UI

## Design read

A desktop utility/workbench for CEAPP authors and operators, with a restrained product interface, not a marketing page.
`DESIGN_VARIANCE: 3`, `MOTION_INTENSITY: 2`, `VISUAL_DENSITY: 5`.
The selected design_taste_frontend explicitly excludes dense product/workflow UI. Apply its useful accessibility, consistency and state principles; do not transplant its landing-page hero/imagery/animation requirements.
This is native local CSS, not an official Fluent/Carbon clone. The demo mark identifies the Lab only.

## Reuse these concrete files

- assets/starter/index.html: structural shell and local script order.
- assets/starter/styles.css: semantic tokens, focus states, dark/light themes and responsive layouts.
- assets/starter/app.js: panels, actions, result status and guarded event handling.
- assets/starter/assets/ceapp-i18n.js: bilingual labels/errors.

For a business app, keep one clear primary workflow. A small single-purpose tool does not need the nine-panel Lab navigation. Do not ship an uncustomized generic Lab as the requested product.

## Layout rules

Desktop: compact brand/header, narrow navigation, main task and results. No giant hero, neon gradient or decorative metrics. Tablet narrows spacing. Below 768px navigation wraps and panels occupy one column.
Use one accent, one global theme, 7px inputs/buttons and 12px panels. Respect system theme and reduced motion. System fonts avoid network/font files.
Labels sit above inputs. Keep controls visible during work but disable duplicate submission. Explain host-only or missing-method controls. A button that silently does nothing is a failure.
Use real fields and functional previews, not decorative fake screenshots.

## State examples

| State | Visible behavior |
|---|---|
| Loading | Named active action, disabled duplicate, stable result area |
| No host | Explicit browser preview banner and Refresh; local file preview still works |
| Empty | Short instruction to choose/sample input |
| Permission denied | Ask for host authorization; no bypass fallback |
| Runtime missing | Check/install entry, useful rest of UI remains |
| Success | Display actual result/text/files, not simulated completion |
| Cancel requested | Keep task identity until terminal state confirms it |
| Unknown outcome | Do not repeat; inspect/recover late result |
| Error | Persistent inline message and safe technical details |

Every dynamic filename/model response is rendered with textContent. Avoid innerHTML for untrusted content. Deliberately fixed print HTML is separate.

## Visual acceptance

Check all panels at 1440, 768, 390 px in both themes. Test keyboard focus, labels, touch targets, no horizontal overflow, bilingual text and readonly result scrolling.
Record what was inspected, not a blanket accessibility certification. Color token calculations are useful but do not replace assistive technology testing.
