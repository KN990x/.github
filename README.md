# KN990x shared workflows and defaults

The CI, dependency and release pieces that every public KN990x repository uses, kept in one
place so they cannot drift apart — and tested here, against fixtures, before any repository
picks up a new version. It also holds the default community health files for every KN990x
repository (see [Community defaults](#community-defaults)).

| Piece | Kind | Used for |
| --- | --- | --- |
| [`actions/validate-config`](actions/validate-config/action.yml) | Composite action | First step of every `ci.yml`: actionlint (with shellcheck) on the workflows and the schema check of `dependabot.yml` — an invalid one disables Dependabot silently. |
| [`actions/majors-report`](actions/majors-report/action.yml) | Composite action | The monthly `Security audit`: rewrites the single "Pending major updates" issue with new majors, held-back packages, and runtimes against their end of support. |
| [`ghcr-publish.yml`](.github/workflows/ghcr-publish.yml) | Reusable workflow | Release → GHCR: tag/version check, CI-passed check, amd64 + arm64 smoke tests, multi-arch push with provenance and SBOM, release assets. `push: false` is the monthly dry run. |
| [`dependabot-merge.yml`](.github/workflows/dependabot-merge.yml) | Reusable workflow | Merges a Dependabot PR once CI is green **and** an authorised reviewer approved its current head — only if it is routine (no major, dependency files only, nothing pushed on top) — then re-runs CI on `main`. Its rules are tested in CI ([`test/automerge`](test/automerge)). |
| [`fleet-check.yml`](.github/workflows/fleet-check.yml) | Scheduled here | Monthly "Fleet status" issue in this repository: CI, audit, release dry run, shared pin, Dependabot PRs and disabled workflows for every public repository. |

## How a change reaches the repositories

1. Change it here. [CI](.github/workflows/ci.yml) validates the config, runs the majors
   report on a deliberately stale project ([`test/majors`](test/majors)) and the whole release
   pipeline on a tiny image in both architectures ([`test/fixture`](test/fixture)).
2. Green on `main` tags the next release by itself — but only when something the
   repositories consume changed (`actions/`, `ghcr-publish.yml`, `dependabot-merge.yml`), since
   every release moves a pin in each of them. A patch by default; put `#minor` / `#major` in a
   commit message for more (a major is for a breaking input change).
3. Each repository pins a release by SHA (`@<sha> # vX.Y.Z`). Its monthly Dependabot
   `actions` PR moves the pin — without the usual 7-day cooldown, which exists for third
   parties — its CI tests the new version, an authorised reviewer approves it, and `dependabot-merge`
   merges it.

The tool versions used here (the actionlint image, check-jsonschema, every action) are
themselves kept current by this repository's Dependabot. Unlike in the repositories, their
majors arrive as PRs here: no majors report covers this repository.

## Community defaults

GitHub uses the files in [`.github/`](.github) for every KN990x repository that does not have
its own of the same kind — public or private. A repository's own file always wins.

| File | Default for |
| --- | --- |
| [`FUNDING.yml`](.github/FUNDING.yml) | The Sponsor button (Ko-fi). |
| [`SECURITY.md`](.github/SECURITY.md) | How to report a vulnerability privately. The products keep their own, with their threat model. |
| [`CONTRIBUTING.md`](.github/CONTRIBUTING.md) | The common rules (pnpm only, `.nvmrc`, full local check, no secrets). The products keep their own, with their toolchain. |
| [`SUPPORT.md`](.github/SUPPORT.md) | Where to get help. |
| [`CODE_OF_CONDUCT.md`](.github/CODE_OF_CONDUCT.md) | Conduct in issues and pull requests. |
| [`ISSUE_TEMPLATE/`](.github/ISSUE_TEMPLATE) | Bug report and feature request forms; blank issues off. All or nothing: a repository with its own templates uses none of these. |
| [`pull_request_template.md`](.github/pull_request_template.md) | The pull request description. |

A licence cannot be a default: each repository keeps its own `LICENSE`. These files are not
part of a release (nothing that calls this repository uses them).

## Using it

```yaml
- uses: KN990x/.github/actions/validate-config@<sha> # vX.Y.Z
```

```yaml
# .github/workflows/automerge.yml in a repository
on:
  workflow_run:
    workflows: [CI]
    types: [completed]
    branches: ["dependabot/**"]
  pull_request_review:
    types: [submitted]
jobs:
  merge:
    permissions:
      contents: write
      pull-requests: write
      actions: write
    uses: KN990x/.github/.github/workflows/dependabot-merge.yml@<sha> # vX.Y.Z
    with:
      approvers: ${{ vars.AUTOMERGE_APPROVERS }}
```

A Dependabot PR merges when it has a green CI run **and** an approving review on its
current head from an authorised reviewer (`AUTOMERGE_APPROVERS`, default the repository
owner). The approval never overrides the fixed rules (no majors,
dependency files only, nothing pushed on top); a rebase needs a new approval.

To stop automatic merges in one repository, set its Actions variable
`DEPENDABOT_AUTOMERGE` to `off`; for a single PR, label it `no-automerge`.

## License

[Apache-2.0](LICENSE)
