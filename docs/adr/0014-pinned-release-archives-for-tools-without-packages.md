# 0014 - Pinned release archives for tools without a package

Status: Accepted
Date: 2026-11-14

## Context

Several mandatory tools have no package on every supported distribution.
On Ubuntu 24.04 that includes `chezmoi`, `uv`, `lazygit` and `delta`.
Upstream installers are usually `curl | sh`, which runs unverified remote code as the user.

## Options considered

- Run the upstream install scripts, which is simple but trusts whatever the server returns at install time.
- Fetch the release archive and the upstream checksum file at install time, which only detects corruption because both come from the same origin.
- Pin the archive URL and SHA-256 in a reviewed file in this repository, and refuse any download that does not match.

## Decision

`packages/releases.toml` pins a version, a URL and a SHA-256 for each tool and each Linux architecture.
`scripts/pin-releases.py` regenerates it, and the diff of that file is the review step for a version bump.
`bootstrap/install_release.py` downloads over https only, verifies the digest, and writes only the named executables, by base name, into `~/.local/bin`.
The system package manager is still preferred wherever a package exists, and `bootstrap/install.sh` falls back to a pinned archive only when it does not.
The security checks fail the build if a script pipes a download into a shell.

## Consequences

The pinned versions age until someone runs the pin script, which is deliberate and visible in the history.
macOS and Windows have no pinned archives, they use Homebrew, winget and scoop.
A tool with neither a package nor a pinned archive is reported as manual, and only a missing mandatory tool makes the installer fail.
Verified by running the installer in Ubuntu 24.04, Fedora and Arch containers, `[verified: Arch]` for the maintainer machine and "tested in container" for the other two.
