# Contributing

This is the default guide for every KN990x repository that does not ship its own
`CONTRIBUTING.md`. When a repository has one, read that instead: it covers its toolchain,
layout and checks.

## Before you start

- **Bugs and ideas:** open an issue with the templates provided. For anything larger than
  a small fix, open an issue first so we can agree on scope before you spend time on it.
- **Security problems:** never in a public issue. See the
  [security policy](SECURITY.md).

## Making a change

1. Fork the repository and work on a branch.
2. Use the toolchain the repository pins: **pnpm only** (never npm or Yarn; `corepack
   enable` picks up the version in `packageManager`) and the Node version in `.nvmrc`.
3. Run the repository's full local check before opening the pull request (the README or
   the repository's own `CONTRIBUTING.md` names it; usually `pnpm run check`).
4. Keep the pull request focused, and say **why** the change is needed, not only what it
   does. Add or update tests for behaviour you change.
5. Write code, comments, commit messages and documentation in English. User-facing strings
   go in both languages the project ships (English and Spanish).

## What not to send

- Secrets, real tokens, personal emails, or homelab hostnames and IPs — not even in tests
  or examples. Use placeholders such as `example.com`.
- Unrelated refactors or formatting changes mixed into a fix.
- Changes to dependency versions on their own: Dependabot handles those.

## Licence

By contributing, you agree that your contribution is licensed under the licence in the
repository's `LICENSE` file.
