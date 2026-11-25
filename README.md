# KN990x shared workflows and defaults

The CI and release pieces that every public KN990x repository uses, kept in one
place so they cannot drift apart — and tested here, against fixtures, before any repository
picks up a new version. It also holds the default community health files for every KN990x
repository (see [Community defaults](#community-defaults)).

| Piece | Kind | Used for |
| --- | --- | --- |
| [`actions/validate-config`](actions/validate-config/action.yml) | Composite action | First step of every `ci.yml`: actionlint (with shellcheck) on the workflows. |
| [`ghcr-publish.yml`](.github/workflows/ghcr-publish.yml) | Reusable workflow | Release → GHCR: tag/version check, CI-passed check, amd64 + arm64 smoke tests, multi-arch push with provenance and SBOM, release assets. `push: false` is the monthly dry run. |
| [`fleet-check.yml`](.github/workflows/fleet-check.yml) | Scheduled here | Monthly "Fleet status" issue in this repository: CI, audit, release dry run, shared pin and disabled workflows for every public repository with a CI. |

## How a change reaches the repositories

1. Change it here. [CI](.github/workflows/ci.yml) validates the workflows and runs the whole
   release pipeline on a tiny image in both architectures ([`test/fixture`](test/fixture)).
2. Green on `main` tags the next release by itself — but only when something the
   repositories consume changed (`actions/`, `ghcr-publish.yml`), since
   every release moves a pin in each of them. A patch by default; put `#minor` / `#major` in a
   commit message for more (a major is for a breaking input change).
3. Each repository pins a release by SHA (`@<sha> # vX.Y.Z`) and moves the pin when its
   dependencies are updated; its CI tests the new version before it lands.

Dependency updates are done by the maintainer, locally and with each repository's full
check, rather than through automated pull requests. Security alerts stay on.

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

## License

[Apache-2.0](LICENSE)
