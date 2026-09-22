# Contributing to psstools

Thanks for your interest. This file applies to **every repository in the
[psstools](https://github.com/psstools) organization** unless that repository ships its own
`CONTRIBUTING.md`.

Two things are asked of every contribution, and one more is asked only of substantial ones:

1. **Sign off every commit** (Developer Certificate of Origin) — always.
2. **Follow the [Code of Conduct](CODE_OF_CONDUCT.md)** — always.
3. **Sign an ICLA** — only above the [significance threshold](#when-an-icla-is-required).

---

## Inbound terms

Unless a repository's `LICENSE` says otherwise, psstools projects are licensed under
**Apache License 2.0**, and contributions are accepted **inbound under the same license as
the project is licensed outbound**. Apache-2.0 §5 already says this: a contribution you
submit for inclusion is submitted under the terms of the project's license, absent a
separate agreement.

Source files carry:

```
Copyright <year> Matthew Ballance and Contributors
```

Shared copyright — you keep yours. Nothing here asks you to assign it.

### Relicensing notice

> Contributions to this project may be relicensed under another OSI-approved license, or
> contributed to a standards organization such as Accellera, as part of the project's
> long-term stewardship. By contributing you acknowledge this possibility. Contributions
> above the threshold described below additionally require a signed ICLA, which makes that
> grant explicit.

**Why this exists.** PSS is an Accellera standard, and the plausible best outcome for a
tool like `pssparser` or `pssc` is that it ends up stewarded by the standards body rather
than by one maintainer. Apache-2.0 plus sign-off alone does not let anyone do that
unilaterally — it would require tracking down every contributor. This notice, and the ICLA
above the threshold, keep that door open.

It is **not** here to enable a proprietary relicense. The commitment in the other direction
is explicit: anything already released under Apache-2.0 stays available under Apache-2.0
forever. Apache-2.0 is irrevocable, so that is not merely a promise — no future decision can
take back what has already shipped.

---

## Signing off (DCO)

Every commit must carry a `Signed-off-by` trailer whose name and email match the commit
author. This is the [Developer Certificate of Origin 1.1](DCO) — a statement that you have
the right to submit the code. It is not a copyright assignment and it is not a CLA.

```sh
git commit -s -m "Your message"
```

That appends:

```
Signed-off-by: Your Name <your.email@example.com>
```

Use your real name and a working email address. `git config user.name` / `user.email` are
what `-s` reads.

**Forgot to sign off?**

```sh
git commit --amend -s --no-edit        # the most recent commit
git rebase --signoff origin/main       # every commit on the branch
git push --force-with-lease
```

**Editing in the GitHub web UI** adds the trailer for you — the organization has
`web_commit_signoff_required` enabled, so a typo fix made in the browser is signed off
automatically.

A CI check enforces this on every pull request.

---

## When an ICLA is required

Most contributions need **no paperwork at all** — sign-off is enough. An Individual
Contributor License Agreement is asked for only when a contribution is large enough that it
could, on its own, block the stewardship path described above.

**The ICLA gate trips if any of the following is true:**

1. The pull request **adds a new source file** under a source root (`src/`, `python/`,
   `ts/`).
2. The pull request adds **more than 100 net lines** to tracked source — excluding generated
   files, lockfiles, vendored trees, and ANTLR output.
3. Your **cumulative** merged additions in that repository pass **100 net lines**.

Clause 3 is deliberate: twenty forty-line pull requests are eight hundred lines that would
never trip a per-PR threshold.

Clauses 1 and 2 are checked automatically on each pull request. Clause 3 is reviewed
quarterly by the maintainers (`scripts/ca-sweep.py --contributors`), who will get in touch
if it applies to you — and will do so while you are still working on the project rather
than years later.

### Maintainer waiver, in both directions

Line counts are a proxy for originality, not a definition of it. A maintainer may:

- **waive** the requirement for a mechanical rename, a generated-file refresh, or a
  bulk-but-unoriginal change that trips the threshold on volume alone; or
- **require** it for a thirty-line contribution that is genuinely novel.

The threshold is a floor for your convenience, not a legal test. If you think it has been
applied wrongly in either direction, say so on the pull request.

### Contributing on company time

If you are contributing as part of your employment, your employer — not you — most likely
owns the copyright, and an ICLA signed by you alone will not cover it. Say so early on the
pull request. A Corporate CLA is the right instrument, and starting that conversation before
the code is written is much cheaper than after.

### What happens if the gate trips

The pull request gets a `needs-icla` label and a bot comment explaining why. Review and
iteration continue as normal — the ICLA is needed before **merge**, not before discussion.

> The ICLA and CCLA texts are being finalized. Until they are published here, a maintainer
> will work it out with you directly on the pull request; nothing is blocked on your side in
> the meantime.

Signed agreements are recorded in [`CONTRIBUTORS.md`](CONTRIBUTORS.md).

*Nothing in this document is legal advice.*

---

## Working on a change

**Open an issue first for anything substantial.** For a typo or an obvious bug, just send
the pull request. For a new feature, a refactor, or anything touching the PSS grammar,
please agree on the shape of it first — it is the cheapest point at which to redirect
effort.

**One logical change per pull request.** A formatting sweep bundled with a behavior change
is a pull request that cannot be reviewed and cannot be reverted cleanly.

**Keep the commits legible.** Present tense, imperative subject line, a body explaining
*why* when it is not obvious. Every commit signed off.

**Tests.** If a repository has a test suite, a bug fix should come with a test that fails
before it and passes after. Per-repository build and test instructions live in that
repository's `README.md`.

**CI.** Pull requests run the repository's checks plus the sign-off check. Both must be green
before merge.

---

## Where these projects actually live

psstools repositories are mirrored. Development happens on a private Forgejo instance and
GitHub is the public mirror, kept in step automatically in both directions.

**This changes nothing for you.** Open issues and pull requests on GitHub as normal; that is
where contributions are accepted and where the checks run. A merged pull request reaches the
authoritative copy on its own.

---

## Reporting a security issue

Please do **not** open a public issue for a security vulnerability. Email
matt.ballance@gmail.com instead.

---

## Questions

Open an issue in the relevant repository, or in
[psstools/.github](https://github.com/psstools/.github) if it is about this policy rather
than about any one project.
