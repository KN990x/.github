# KN990x shared workflows

The CI, dependency and release pieces that every public KN990x repository uses, kept in one
place so they cannot drift apart.

| Piece | Kind | Used for |
| --- | --- | --- |
| [`actions/validate-config`](actions/validate-config/action.yml) | Composite action | First step of every `ci.yml`: actionlint on the workflows and the schema check of `dependabot.yml` (an invalid one disables Dependabot silently). |
| [`actions/majors-report`](actions/majors-report/action.yml) | Composite action | The monthly `Security audit` workflow: rewrites the single "Pending major updates" issue with new majors, held-back packages and runtimes near end of support. |
| [`.github/workflows/ghcr-publish.yml`](.github/workflows/ghcr-publish.yml) | Reusable workflow | Release → GHCR: tag/version check, CI-passed check, amd64 + arm64 smoke tests, multi-arch push with provenance and SBOM, release assets. `push: false` is the monthly dry run. |

## Using it

Always pin by commit SHA, with the release tag as a comment:

```yaml
- uses: KN990x/.github/actions/validate-config@<sha> # v1.0.0
```

```yaml
jobs:
  publish:
    permissions:
      contents: write
      packages: write
      actions: read
    uses: KN990x/.github/.github/workflows/ghcr-publish.yml@<sha> # v1.0.0
    with:
      image: ghcr.io/kn990x/<name>
      tag: ${{ github.event.release.tag_name || inputs.tag }}
      push: ${{ github.event_name == 'release' || inputs.push == true }}
```

Dependabot updates the pin in each repository when a new release of this one is tagged.

## Changing it

1. Change and push here. CI runs the new `validate-config` against this repository itself.
2. Tag a release (`vX.Y.Z`; a breaking input change is a new major).
3. The repositories pick it up in their monthly Dependabot `actions` PR, or bump the SHA by
   hand when it cannot wait.

## License

[MIT](LICENSE)
