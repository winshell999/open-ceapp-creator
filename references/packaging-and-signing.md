# Packaging and signing

This public skill produces CEAPP source, not an official/KOL-signed trusted package.
The generated root contains app.json, index.html, app-config.js, app.js, styles.css, local assets and only the required scripts/data schema.

Run structural/behavior checks, then open CanEngine > My > Developer identity / CEAPP packaging and signing. Drag the CEAPP project directory into the client. The client validates, packages and signs using the currently authorized identity. Install the output and perform native acceptance.
Do not drag the entire skill directory, assets/demos parent, test directory, backups or documentation repository into the CEAPP packer. Drag exactly one generated app root with app.json at its top level.
The downloadable demo source ZIP is an ordinary source archive, not a .ceapp. Renaming a ZIP does not produce valid trusted signing.

Preserve the original MIT license. Do not embed private keys, official/KOL signer secrets, trusted identities, machine-specific private-key paths or internal signing endpoints.
Official/KOL/local/unsigned/invalid labels identify provenance and risk; self-signing is not official endorsement or a security audit. Signing validity and runtime correctness are separate gates.
# Web mode packaging

Remote Web sources may contain only app.json and an optional local icon. Do not add a dummy index.html/command to satisfy historical static rules: CanEngine 1.8.0 uses app.json as the container anchor. Local Web 1.8.0 still uses a real packaged backend entry and permits empty commands. Both retain the normal signing/install/license flow; online mode is not an unsigned production entry.

A remote package signature protects the manifest and bundled files, not future website responses. A site deployment can change content without a new CEAPP; URL/origin/storage changes require a new signed configuration. Keep appId stable for normal updates, use separate test/production identities, and include the real minimum host/platform requirements.

Protected remote packages include the public `authorization: "canengine"` declaration, not website PHP, site keys, admin credentials, License Tokens, tickets or sessions. Package and re-sign the updated source without changing its version unless the user asks. Check both signed metadata and the payload manifest for the intended minimum 1.8.0, and update the actual delivered copy rather than only its source. A public skill/source ZIP must exclude live site configurations, private paths, databases, signing material and unsanitized logs/screenshots; use reserved example domains and synthetic fixtures. See [remote-web-authorization.md](remote-web-authorization.md).

## Optional Python native build

The client defaults to normal packaging, including when `ceapp.build.json` exists. Normal packages keep the source, assets and declared platforms without checking or installing compiler tools. One normal package works across Mac/Windows only when the application and dependencies actually support both.

For Python local websites with empty commands, `ceapp.build.json` enables the optional Source protection packaging (Advanced) choice. My and Canvas use the same mode/progress/delivery dialog and `CEAppSignerPackageProject` host implementation. Select protection explicitly, prepare developer tools when needed, then compile/package/sign; CLI users must pass `ceapp-pack -mode python`. Both modes set the optional import password inside that shared dialog. Environment-ready text is green and the preparation action is Install build environment. Mac and Windows use one pipeline, compile separately on each OS/architecture and can merge exported .cebuild artifacts into one signed CEAPP. .cebuild is a developer exchange artifact, not installable; only receive builds from a trusted environment. The final package is verified as a whole before the installer keeps only the current platform backend and common files. See [Python compiled packaging](python-compiled-packaging.md) for the configuration, resource/data adaptation and unpacked layout. The build manifest is authoring metadata and is not shipped. A failed/cancelled protected build stops; it must not publish a fallback Python source package or replace an earlier package. Containers are verified for integrity and signature before replacing the target. Neither host nor app version is automatically changed.
