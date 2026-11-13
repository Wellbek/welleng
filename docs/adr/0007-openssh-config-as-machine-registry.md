# 0007 - OpenSSH config as the machine registry

Status: Accepted
Date: 2026-11-13

## Context

Remote machines need names, hosts, users, ports, identity files and jump hosts, plus an easy way to pick one.
Whatever format is chosen must keep working without this project installed.

## Options considered

- A custom database or YAML registry: a second source of truth that drifts from `ssh_config`.
- OpenSSH config as the registry, with a small selector and editor on top.

## Decision

OpenSSH config is the registry.
One `Include ~/.ssh/config.d/*.conf` line is added at the top of `~/.ssh/config`, and hosts added through welleng become fragments in that directory.
Optional description and tags live in structured comments above each block.
Hand-edited entries are read but never rewritten.

## Consequences

`ssh <name>` always works without welleng, because nothing is proprietary.
Host fragments contain IP addresses and usernames, so they are local and never tracked in this repository.
Private keys stay in `~/.ssh`, and the config stores a path only.
Out of scope: syncing keys, managing remote installs and remote Claude sessions.
