# Runnable demos

`assets/starter/` is the full Bridge Lab. `assets/demos/` contains nine independent generated CEAPP source projects with matching manifests. Each directory is individually packageable; never pack the parent demos directory.

| Directory | Initial action | Follow-through |
|---|---|---|
| minimal | Overview > Refresh | Website, clipboard, print and diagnostics hooks |
| files | Files > Choose file / Sample file | Open staged file, remove staging, choose export folder |
| python | Files > Sample file | Inspect -> open/export; slow task -> cancel |
| ai-text | AI > Refresh | Explicit prompt -> text response |
| ai-media | Files > choose an image | Vision/image/video/3D; task refresh/watch/cancel |
| data | Database > Save note | Read/list/delete app-private note |
| phone | Phone > Create session | Real receive/import; add/send sample explicitly |
| notifications | System > Notification status | Send explicit test and open host settings |
| full | Overview > Refresh | All nine panels for host acceptance |

Generate a fresh project instead of renaming IDs by hand:

```bash
python scripts/create_ceapp.py --profile python --app-id my-inspector --name "My Inspector" --output /path/to/new-app
python scripts/create_ceapp.py --profile data --app-id my-reader --name "My Reader" --dataset REAL_DATASET_ID --output /path/to/new-reader
```

Replace REAL_DATASET_ID with a resource actually configured in the host. Do not ship placeholder IDs. The full default has no required shared resources and no schedule registrations.

## Reusable advanced examples

`assets/recipes/advanced-bridges.js` contains opt-in implementations for staged-file lookup/removal, legacy result save/open/reveal, image/file clipboard, small asset data URLs, runtime/environment helpers, notification registration/update/removal, host capability query, print and diagnostics.
These functions do nothing until called. Copy only a needed function and its matching permission/UI/tests; do not add a public generic "execute arbitrary method" panel.
Notification registration is configuration demonstration, not a complete background producer. Adding it requires notification.schedule and a real app feature design. The basic demo intentionally avoids creating persistent background work.

## Form prefill starter · 1.8.0

`assets/form-prefill/` is a local Web field-entry starter. Generate it with `--profile form-prefill --url ACTUAL_HTTPS_PAGE --mapping researched-request.json`. It intentionally has no default site mapping; do not package the raw template. The generator substitutes the signed target and reviewed synthetic request. Customize bilingual labels, options and hints, clear production defaults, then use a click to open/prefill the native website for manual review. See [form-prefill.md](form-prefill.md). `tests/test_prefill.py` and `tests/prefill_browser_smoke.py` validate the generator/local shell; simulated bridge results do not establish website native acceptance.

## Standard fixture inputs

Create sample.csv inside the app with the sample button, or use a small UTF-8 .txt/.json/.csv. Image AI needs an actual staged image. Phone flows need a real phone. AI services are host-configured and may cost money; tests use explicit synthetic fixtures instead.
