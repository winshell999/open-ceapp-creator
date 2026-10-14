# Protected remote website skill validation · 2026-10-14

Scope: public CEAPP declaration, creator CLI, structural validator and privacy guidance. The skill and template versions remain 1.8.0. Fixtures use reserved example domains and synthetic values; no live website configuration or credentials are included.

| Check | Result |
|---|---|
| `python tests/test_tools.py` | PASS — 40 tests, including protected CLI output, provider/profile rejection, credential-free errors, server-file exclusion and version preservation |
| `python tests/test_prefill.py` | PASS — 9 tests |
| `node --test tests/bridge.test.cjs` | PASS — 37 tests |
| `python scripts/audit_contract.py assets` | PASS — no unknown literal public bridge methods |
| Skill-creator `quick_validate.py` | PASS — frontmatter and skill structure; validation tooling isolated from the user's environment |
| Published protected manifest example | PASS — source validator accepts the example |
| All template app/minimum versions | PASS — 1.8.0; existing app versions are not rewritten by validation |
| Public source and archive privacy scan | PASS — reserved remote template URL, no copied website PHP, live site key, private paths or unreviewed local captures |
| Generated protected app in macOS/Windows native host | NOT_RUN — this update changes skill authoring and validation, not native host code |
| Live website registration or deployment in this update | NOT_RUN — creator output alone does not protect a website |

The complete public `skill.zip` includes functional source, templates, tests and reviewed text evidence. Raw local logs/screenshots and private configuration are excluded. The validator rejects known unsafe declarations and server files; it does not prove that arbitrary package content has no secrets, or that server access control is correctly deployed. Each created website needs its own HTTP and native acceptance.

Matching host source hashes use repository-relative names in `REMOTE_WEB_AUTH_SOURCE_SHA256.json`.
