# CEAPP Creator validation report

Date: 2026-09-26. Source baseline: CanEngine 1.7.3 repository snapshot.

## Actually executed

| Layer | Result | Evidence |
|---|---|---|
| Bridge adapter regression tests | PASS, 37 tests | node-tests.txt |
| Python processor and generator/validator tests | PASS, 25 tests (including all 9 profiles) | python-tests.txt |
| Full starter structure / JS / Python syntax | PASS | starter-validation.json |
| Nine independent demo structures | PASS, 9 projects | demo-validation.json |
| Literal public method spelling | PASS, 63 unique literal methods checked | contract-audit.json |
| Chromium UI layout | PASS, all 9 panels at 1440/768/390 px in light and dark | browser-report.json |
| Local browser-file preview and language switching | PASS in inlined Chromium rendering | browser-report.json |
| Bridge integration flows in browser | SIMULATED, expected fixtures passed | browser-report.json |
| Native CanEngine WKWebView / WebView2 | NOT_RUN | testing-and-acceptance.md |
| Real provider AI generation / real phone transfer | NOT_RUN | No external service/device calls made |
| Final .ceapp client signing / installation | NOT_RUN | Client-side acceptance still required |

## Browser constraint

The container Chromium blocks file:// and URL navigation with ERR_BLOCKED_BY_ADMINISTRATOR. The successful UI run injected the local HTML, CSS and JS in the original script order, with no live server or external startup requests. It verified rendering and handlers, NOT installed asset URL rewriting or the native WebView.
No uncaught page errors were observed in that run. The supplied screenshots are real screenshots of the rendered app, not generated UI artwork.

## What is and is not covered

The contract inventory records 76 public methods plus 5 collection/dataset factory members from inspected source. Listing these is not a claim that each has had a native execution test. Request/response shapes for the main workflows have source-backed implementations and focused regression tests; opt-in advanced methods have reference implementations and syntax/name checks.
Python fixture tests executed real standard-library code and checked actual output files, contents and JSON. Mock AI text, simulated phone transfers and simulated database persistence are not real-provider/device/database acceptance.

No new generated application may inherit this report as its own PASS. Rerun checks after changing business logic, permissions, runtime dependencies or source baseline. Follow the installed-host acceptance checklist before claiming native support.
