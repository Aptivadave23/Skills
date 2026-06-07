# Release Pattern

Use this as the default layout for .NET repos that should keep version bumps behind a successful CI run.

## Workflow layout

1. Create a `CI` workflow.
   - Trigger on `pull_request`, `push` to `main`, and optional `workflow_dispatch`.
   - Run `dotnet restore` and `dotnet build`.
   - Do not run `semantic-release` here.

2. Create a `Release` workflow.
   - Trigger on `workflow_run` for the `CI` workflow.
   - Require `workflow_run.event == 'push'`.
   - Require `workflow_run.conclusion == 'success'`.
   - Also support a separate tag-triggered release path for seeded assets if the repo uses it.

3. In the release workflow:
   - Check out the `workflow_run.head_sha`.
   - Use the `workflow_run.head_branch` as the release base branch.
   - Skip any commit whose subject starts with `chore(release): `.
   - Run `semantic-release` only after the guard passes.
   - Read the next version from `.next-release-version` when present.
   - Import a GPG key before committing the release bump.
   - Commit the changelog and version bump to `release/<version>`.
   - Open or update a PR from `release/<version>` back to the base branch.
   - Approve and enable auto-merge with `GITHUB_TOKEN`.

## Secrets

- `AUTO_APPROVE_TOKEN`: use only for `gh pr create` if `GITHUB_TOKEN` is blocked.
- `GPG_PRIVATE_KEY`: ASCII-armored private key for release commit signing.
- `GPG_PASSPHRASE`: passphrase for the private key.
- `GPG_GIT_USER_NAME`: author name for the signed release commit.
- `GPG_GIT_USER_EMAIL`: author email for the signed release commit.

## Guardrails

- Do not create a release branch from CI output that has not passed.
- Do not allow the same PAT identity to create and approve the release PR.
- Keep seeded tag releases separate from semantic-release so they do not create an extra version bump.
- If the release commit pushes a branch named `release/<version>`, guard against retriggering the release workflow on that branch.
