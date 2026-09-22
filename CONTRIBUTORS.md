# Contributors

People who have contributed to psstools projects, across all repositories in the
organization.

This file exists for two reasons: to give credit, and to keep a durable way of reaching
contributors. Commit email addresses go stale — the single most useful thing recorded below
is a contact that will still work in five years.

**Affiliation** is recorded as of the time of contribution and is not updated afterwards.
**ICLA** records whether a signed Individual (or Corporate) Contributor License Agreement is
on file; see [CONTRIBUTING.md](CONTRIBUTING.md#when-an-icla-is-required) for when one is
required. `n/a` means the contributor has not passed the significance threshold and none is
needed.

| Name | Contact | Affiliation at time of contribution | ICLA | Since |
|---|---|---|---|---|
| Matthew Ballance | matt.ballance@gmail.com | — (project maintainer) | n/a — copyright holder | 2019 |
| Matthew Ballance | mballance@oatfieldi9.localdomain | — (same person; legacy workstation identity) | n/a — copyright holder | 2020 |

## A note on the second row

`git` records whatever `user.email` was configured on the machine that made the commit, and
a machine-local address is not a contact — it never reached anybody. The quarterly sweep
(`scripts/ca-sweep.py --contributors`) counts by identity, so an alias that is not recorded
here shows up as an unrecognised contributor past the threshold. It found exactly that on
its first run, which is the behaviour to want: **the alias is listed rather than
special-cased**, because the day that pattern appears for someone who is *not* the
maintainer, it must not be silently absorbed.

## Adding yourself

You do not need to. Maintainers add a row when a contribution merges. If you would like a
different name, contact, or affiliation recorded — or would prefer not to be listed at all —
say so on your pull request or open an issue.

## Automated contributors

`dependabot[bot]` has opened dependency-update pull requests in some repositories. Those are
machine-generated and are not listed here.
