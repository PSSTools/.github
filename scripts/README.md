# Maintainer scripts

## `ca-sweep.py` — the quarterly contributor-agreement sweep

Run this **once a quarter**. It covers the two parts of
[`CONTRIBUTING.md`](../CONTRIBUTING.md) that no CI job can hold on its own.

```sh
./scripts/ca-sweep.py                # both sections
./scripts/ca-sweep.py --settings     # settings drift only
./scripts/ca-sweep.py --contributors # cumulative threshold only
```

Read-only. It reports; it never changes anything. Exit status is non-zero when
it finds something.

### Why each half exists

**`--contributors` is clause 3 of the significance threshold.** The per-pull-request
check in `reusable-significance.yml` can only see one pull request. Twenty
forty-line pull requests are eight hundred lines that never trip a per-PR gate,
so a per-PR check alone has a hole the whole contribution history fits through.
Walking history live in CI is not worth building; a quarterly pass catches the
slow accumulator while they are still active and reachable — which is exactly
when re-papering works, and the window this sweep's cadence bounds.

**`--settings` catches drift.** The organization is on the GitHub free plan, so
`GET /orgs/psstools/rulesets` returns 403 and there is no org-wide ruleset to
pin anything with. Every setting is per repository, set by hand, and nothing
stops one from being changed back.

Two are worth understanding:

- **`squash_merge_commit_message`.** At `COMMIT_MESSAGES` the source commit
  messages are concatenated into the squash commit, so sign-off trailers
  survive. If it ever flips to `PR_BODY`, **the DCO check still passes on the
  pull request's commits while what lands on the default branch carries no
  sign-off at all** — and the permanent record is the branch, not the closed
  pull request.
- **`enforce_admins` must stay `false`.** Development happens on a private
  Forgejo instance and the mirror pushes to the default branch as an org owner.
  The DCO check is `on: pull_request`, so it does not run for a direct push —
  with `enforce_admins = true` those pushes would be judged against a required
  check that never reports and **every sync cycle would fail**, silently. The
  check still applies to everyone else's pull requests, which is the entire
  population the gate exists for.

### Keeping it in step

`SOURCE_EXT` and `EXCLUDE_RE` are duplicated from
`.github/workflows/reusable-significance.yml` on purpose — a workflow cannot
import from a script. **Change one, change the other.** A contributor who is
under the threshold per pull request and over it cumulatively should not get two
different answers about which files counted.
