# Packaging and signing

This public skill produces CEAPP source, not an official/KOL-signed trusted package.
The generated root contains app.json, index.html, app-config.js, app.js, styles.css, local assets and only the required scripts/data schema.

Run structural/behavior checks, then open CanEngine > My > Developer identity / CEAPP packaging and signing. Drag the CEAPP project directory into the client. The client validates, packages and signs using the currently authorized identity. Install the output and perform native acceptance.
Do not drag the entire skill directory, assets/demos parent, test directory, backups or documentation repository into the CEAPP packer. Drag exactly one generated app root with app.json at its top level.
The downloadable demo source ZIP is an ordinary source archive, not a .ceapp. Renaming a ZIP does not produce valid trusted signing.

Preserve the original MIT license. Do not embed private keys, official/KOL signer secrets, trusted identities, machine-specific private-key paths or internal signing endpoints.
Official/KOL/local/unsigned/invalid labels identify provenance and risk; self-signing is not official endorsement or a security audit. Signing validity and runtime correctness are separate gates.
