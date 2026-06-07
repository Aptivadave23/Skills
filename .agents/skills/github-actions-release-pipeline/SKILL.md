---
name: github-actions-release-pipeline
description: Design, refactor, and harden GitHub Actions CI/CD pipelines for .NET repos that use semantic-release, signed release PRs, tag-seeded releases, and PR-only main branches. Use when creating or updating workflows that should split CI from release, gate version bumps behind successful CI, avoid self-approval, or standardize release automation across repos.
---

# GitHub Actions Release Pipeline

## Overview

Use this skill when building GitHub Actions pipelines that must keep CI and release concerns separate. The preferred pattern is:

- run build validation in a CI workflow
- trigger release automation only after CI succeeds
- run semantic-release only in the release workflow, never in CI
- keep tag-seeded asset publication separate from semantic-release
- split PR creation from approval so the same account does not approve its own release PR

## Preferred Pattern

Start from the reference workflow in [references/release-pattern.md](references/release-pattern.md) and adapt only the repo-specific paths, names, and secrets.

When implementing or reviewing a pipeline:

- Use one CI workflow for `pull_request` and `push` to `main`.
- Use one release workflow triggered by `workflow_run` after CI completes successfully on `push` to `main`.
- Keep tag-triggered release asset publication as a separate job or workflow path.
- Gate release execution on a successful CI conclusion and on `workflow_run.event == 'push'`.
- Skip release automation if the head commit subject starts with `chore(release): `.

## Release Rules

- Run `dotnet restore` and `dotnet build` in CI before any release automation.
- Run `semantic-release` only after CI has succeeded.
- Use `GITHUB_TOKEN` for PR approval and auto-merge.
- Use a separate PAT only for `gh pr create` when GitHub blocks `GITHUB_TOKEN` for that action.
- Import a GPG key before committing the release bump branch so release commits are signed.
- Push the release branch as `release/<version>` and open or update a PR against the original base branch.
- Keep seeded tag releases separate from semantic-release so the tag path can publish packaged assets without producing an extra version bump.

## What To Check

- Confirm workflow names are stable if `workflow_run` depends on them.
- Confirm the release workflow uses the successful CI workflow's head SHA and head branch.
- Confirm the release workflow does not run on release-commit feedback loops.
- Confirm the repo secrets are present before relying on auto-approval.
- Confirm branch protection allows PR-based merges while still permitting the release workflow to operate.

## When To Use This Skill

Use this skill for GitHub Actions work that involves:

- `.github/workflows/*.yml` or `.yaml` release automation
- `semantic-release` configuration
- `workflow_run`-based release gating
- signed release commits and release PRs
- tag-seeded GitHub Releases
- avoiding self-approval and other GitHub Actions token pitfalls
