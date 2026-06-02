# CEAPP Packaging And Signing Handoff

This open skill generates CEAPP source projects. It does not create official or KOL-signed final packages. Packaging and signing are performed by the CanEngine client or the CanEngine backend signing service.

## Recommended Main Flow

1. Use the skill to generate a CEAPP project root directory.
2. Confirm the project contains at least:
   - `app.json`
   - `index.html`
   - local CSS / JS files
   - local `assets/` when assets are needed
3. Open CanEngine.
4. Go to `我的 → 开发者身份 / CEAPP打包与签名`.
5. Drag the CEAPP project root folder into the signing area.
6. CanEngine validates the project, packages it, signs it with the current authorized identity, and exports a `.ceapp` file.

## Supported Inputs In CanEngine

CanEngine should support two input types:

| Input | Purpose | Output |
|---|---|---|
| CEAPP project root folder | Main flow for skill-generated apps | Packaged and signed `.ceapp` |
| Existing `.ceapp` file | Re-signing or source labeling | Re-signed `.ceapp` |

When the input is a project folder, CanEngine performs packaging first, then signing.

When the input is an existing `.ceapp`, CanEngine verifies the existing package state, then re-signs or warns as needed.

## Signing Identity Rules

The current CanEngine authorization determines the signing label:

| Identity | Label | Color | Meaning |
|---|---|---|---|
| Official | `官方` | Green | CanEngine official source |
| KOL publisher | Backend-configured KOL display name, for example `仙人掌` | Blue | Trusted publisher identity |
| Normal user / local signer | User name, for example `王灿` | Yellow | Self-signed / lower trust |
| Unsigned | `未签名` | Gray | Source cannot be verified |
| Invalid signature | `签名无效` | Red | Package may have been modified |

The skill must not hardcode or generate official/KOL signing credentials.

## What This Skill Must Not Do

Do not include any of the following in generated projects or default docs:

- official CanEngine private keys
- KOL private keys
- default official key IDs as if they were usable by public developers
- instructions that imply a self-signed package is official or trusted
- scripts that make official/KOL signing the default path

Environment-variable based signing may exist only as advanced internal or CI documentation outside the open skill. It must not be the public default flow.

## Terminology

- `publisherId`: a public identifier for the signer.
- `keyId`: a public identifier for a signing key.
- `publicKey`: public verification key.
- `privateKey`: secret signing key. It must never be committed to the skill, starter, source project, or public repository.

`keyId` is not a password. It is safe to display as metadata, but it cannot sign anything by itself.
