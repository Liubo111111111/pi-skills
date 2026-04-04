---
name: agent-safety-guard
description: "Protect against destructive agent file operations. Use when agents may delete, overwrite, move, sync, or batch-edit files, especially in OpenClaw workspaces, code repos, and mixed directory layouts."
---

# Agent Safety Guard

## Purpose

Prevent high-impact filesystem mistakes in agent workflows, especially:
- accidental deletion in the wrong directory
- recursive overwrite/move across large trees
- workspace/project mixing
- destructive changes being propagated by auto-sync
- improvised recovery after a bad command

This skill is a **guardrail protocol**, not a generic coding skill.

## When to use

Activate this skill when any task involves:
- `rm`, `mv`, `cp -r`, `find ... -delete`, bulk rename, bulk overwrite
- git operations that can discard work (`reset --hard`, `clean -fd`, force checkout)
- auto-sync, backup, mirroring, or deployment after file mutations
- agents working across multiple directories or repos
- OpenClaw workspace maintenance

## Core rules

### 1) Never rely on `cd` persistence
Do **not** assume a previous `cd` changes the working directory of later tool calls.

Safe patterns:
- set `workdir` explicitly for each exec/tool call
- or use one command like: `cd /target/path && <command>`

Unsafe pattern:
- `cd some/path`
- later: `rm -rf ./*`

### 2) Treat destructive commands as checkpointed actions
Before any destructive or high-blast-radius command, collect and review:
- current directory: `pwd`
- target path
- directory listing summary: `ls` / `find`
- estimated impacted file count
- whether target is in an approved directory allowlist

If any of these are unclear, stop and ask.

### 3) High-risk commands require confirmation
Require explicit human confirmation before running commands such as:
- `rm -rf`
- `find ... -delete`
- recursive move/copy over existing trees
- `git reset --hard`
- `git clean -fd`
- mass replacement touching many files
- anything targeting workspace root or parent directories

### 4) Enforce directory boundaries
Prefer a separated layout:
- `~/.openclaw/workspace/` → agent runtime / memory / skills / tooling
- `~/projects/` → code repositories
- `~/Obsidian/` or equivalent → notes / docs

Rules:
- do not store active code repos inside the main agent workspace unless intentional
- do not mix runtime state with source repos
- treat workspace root as sensitive

### 5) Add blast-radius checks
Pause if any command would:
- affect more than a small threshold of files
- touch root-like paths (`.`, `./*`, `..`, `/`, `~`)
- touch critical directories (`skills/`, `memory/`, `data/`, config files)
- run against a path different from the task’s stated target

### 6) Stop sync before spreading damage
If major deletion or corruption is detected:
1. pause sync / backup propagation if possible
2. inspect scope of damage
3. recover from backup / git / upstream source
4. create a timeline and root-cause note
5. only then resume sync

Do not let automation immediately push a bad local state upstream.

### 7) Recovery before reconstruction
After an incident:
- recover original files first
- avoid “recreating empty shells” unless explicitly needed
- prefer authoritative sources: backups, git remotes, snapshots

## Recommended preflight checklist

Before risky file operations, verify:

```bash
pwd
ls
find <target> | wc -l
```

For git-destructive actions, also verify:

```bash
git status --short
git rev-parse --show-toplevel
```

## Human checkpoint message template

Use a short confirmation like:

- Current dir: `<pwd>`
- Target: `<path>`
- Estimated impact: `<N>` files
- Operation: `<command>`

Proceed? [y/N]

## What this skill is trying to prevent

Classic failure mode:
- agent thinks it is inside a subdirectory
- destructive command runs in workspace root instead
- sync propagates deletion
- recovery becomes multi-system incident response

This skill exists to make that sequence much harder.

## Minimum safe policy

If you cannot verify directory, target, and blast radius, do not run the command.
