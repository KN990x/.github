# Security policy

This is the default policy for every KN990x repository that does not ship its own
`SECURITY.md`. Repositories that do (EasyPages, PullPilot, vuzon, Glassys) describe their
threat model and scope there, and that file takes precedence.

## Reporting a vulnerability

**Please do not open a public issue for anything exploitable.**

Use GitHub's private vulnerability reporting: open the repository's **Security** tab and
choose **Report a vulnerability**. That opens a private advisory visible only to the
maintainer.

Helpful things to include:

- the affected version, image tag or commit;
- what an attacker gains, and what access they need to start;
- steps to reproduce, ideally against a local install;
- any configuration that matters, with placeholders instead of real tokens, domains,
  passwords or hostnames.

## What to expect

These are hobby projects maintained by one person. Expect a first reply within a few
days. Fixes ship in a new release (or on `main` where there are no releases yet), and the
advisory is published once users have had a chance to upgrade, with credit unless you
prefer to stay anonymous.

## Supported versions

Only the latest release receives security fixes. Older tags do not get backports: please
check that the problem still exists on the latest release before reporting it.
