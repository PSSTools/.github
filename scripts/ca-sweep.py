#!/usr/bin/env python3
"""The contributor-agreement sweep: the parts of the policy no CI job can hold.

Two things in the contributor agreement are deliberately NOT automated in CI,
and this script is what makes them real rather than aspirational. Run it
quarterly.

    ./scripts/ca-sweep.py                # both sections
    ./scripts/ca-sweep.py --settings     # drift only
    ./scripts/ca-sweep.py --contributors # clause 3 only

**--contributors implements clause 3 of the significance threshold**: a
contributor's *cumulative* merged additions passing 100 net lines. Twenty
forty-line pull requests are eight hundred lines that never trip a per-PR
gate, so a per-PR check alone has a hole the entire contribution history fits
through. Walking history live in CI is not worth building; a periodic pass
catches the slow accumulator while they are still active and reachable, which
is precisely when re-papering works.

**--settings checks for drift** in the things that were set by hand. The
organization is on the GitHub free plan, so there are no org-wide rulesets
(`GET /orgs/.../rulesets` returns 403) -- every setting is per repository and
nothing prevents one from being changed back. The sharp one is
`squash_merge_commit_message`: if it flips from COMMIT_MESSAGES to PR_BODY,
the DCO check still passes on the pull request's commits while what lands on
the default branch carries no sign-off at all. The permanent record is the
branch, not the closed pull request.

Requires `gh` (authenticated) and `git`. Read-only: it reports, it never
changes anything.
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from collections import defaultdict

ORG = "psstools"
THRESHOLD = 100

# Kept deliberately in step with .github/workflows/reusable-significance.yml.
# If you change one, change the other -- a contributor who is under the
# threshold per pull request and over it cumulatively should not get two
# different answers about which files counted.
SOURCE_EXT = (
    ".py", ".pyi", ".ts", ".tsx", ".js", ".jsx",
    ".c", ".h", ".cc", ".cpp", ".hpp", ".cxx", ".hxx",
    ".java", ".rs", ".go", ".sv", ".svh", ".v", ".vh",
    ".pss", ".g4", ".cmake", ".sh",
)
EXCLUDE_RE = re.compile(
    r"(^|/)("
    r"generated|gen|_generated|vendor|vendored|third_party|thirdparty|"
    r"node_modules|dist|build|out|\.venv|__pycache__"
    r")(/|$)"
    r"|(^|/)(antlr|antlr4)(/|$)"
    r"|(^|/)[^/]*(Lexer|Parser|Listener|Visitor)\.(py|ts|java|js)$"
    r"|(^|/)(poetry\.lock|package-lock\.json|yarn\.lock|pnpm-lock\.yaml|"
    r"Cargo\.lock|uv\.lock|requirements.*\.txt)$"
    r"|\.(interp|tokens)$",
    re.IGNORECASE,
)

BOTS = {"dependabot[bot]", "github-actions[bot]", "renovate[bot]"}


def sh(*args, **kw):
    return subprocess.run(args, capture_output=True, text=True, **kw)


def gh_json(path):
    p = sh("gh", "api", path)
    if p.returncode != 0 or not p.stdout.strip():
        return None
    try:
        return json.loads(p.stdout)
    except json.JSONDecodeError:
        return None


def active_repos():
    p = sh("gh", "repo", "list", ORG, "--limit", "100", "--json",
           "name,isArchived,defaultBranchRef")
    return sorted(
        (r["name"], (r["defaultBranchRef"] or {}).get("name", "main"))
        for r in json.loads(p.stdout) if not r["isArchived"]
    )


# --------------------------------------------------------------- settings --
def check_settings(repos):
    problems = []
    print("== Org ==")
    org = gh_json(f"orgs/{ORG}")
    signoff = org.get("web_commit_signoff_required") if org else None
    ok = signoff is True
    print(f"  {'ok   ' if ok else 'DRIFT'} web_commit_signoff_required = {signoff}"
          "  (CA-S1, want true)")
    if not ok:
        problems.append("org web_commit_signoff_required is not true (CA-S1)")

    print("\n== Repositories ==")
    for name, branch in repos:
        slug = f"{ORG}/{name}"
        r = gh_json(f"repos/{slug}")
        if r is None:
            problems.append(f"{name}: could not read repository")
            continue
        issues = []

        # CA-S3. COMMIT_MESSAGES concatenates the source commit messages, so
        # the sign-off trailers survive the squash. PR_BODY does not.
        if r.get("squash_merge_commit_message") != "COMMIT_MESSAGES":
            issues.append(
                f"squash_merge_commit_message = {r.get('squash_merge_commit_message')}"
                " -- sign-off trailers would NOT survive a squash merge (CA-S3)")

        # CA-T1/CA-T2 callers present.
        tree = gh_json(f"repos/{slug}/contents/.github/workflows")
        names = {f["name"] for f in tree} if isinstance(tree, list) else set()
        for want in ("dco.yml", "icla-significance.yml"):
            if want not in names:
                issues.append(f"missing .github/workflows/{want}")

        # The label the significance workflow applies.
        if gh_json(f"repos/{slug}/labels/needs-icla") is None:
            issues.append("missing the needs-icla label")

        # CA-S2. Required status checks on the default branch.
        prot = gh_json(f"repos/{slug}/branches/{branch}/protection")
        if prot is None:
            issues.append(f"branch {branch} is NOT protected -- the DCO check is "
                          "advisory, and a pull request can be merged past it (CA-S2)")
        else:
            contexts = (prot.get("required_status_checks") or {}).get("contexts") or []
            if not any("Signed-off-by" in c or "dco" in c.lower() for c in contexts):
                issues.append(f"branch {branch} is protected but the DCO check is not "
                              f"required (contexts: {contexts or 'none'}) (CA-S2)")
            # enforce_admins MUST stay false: the Forgejo -> GitHub mirror
            # pushes to this branch as an org owner, and the DCO check does not
            # run on a direct push. true would fail every sync cycle.
            if (prot.get("enforce_admins") or {}).get("enabled"):
                issues.append("enforce_admins is TRUE -- this breaks the Forgejo mirror, "
                              "which pushes to this branch as an admin and cannot satisfy "
                              "a pull_request-only check (see CA-S4)")

        if issues:
            print(f"  DRIFT {name}")
            for i in issues:
                print(f"        - {i}")
                problems.append(f"{name}: {i}")
        else:
            print(f"  ok    {name}")
    return problems


# ----------------------------------------------------------- contributors --
def net_additions(repo, branch, workdir):
    """{author: net source lines added} on `branch`, using the same file
    exclusions as the per-pull-request significance check."""
    path = os.path.join(workdir, repo)
    if sh("git", "clone", "--quiet", "--filter=blob:none", "--single-branch",
          "--branch", branch,
          f"https://github.com/{ORG}/{repo}.git", path).returncode != 0:
        return None

    # --no-merges: a merge commit's content is the sum of commits already
    # counted, so counting it would double every merged line.
    p = sh("git", "-C", path, "log", branch, "--no-merges",
           "--numstat", "--format=%x01%an <%ae>")
    totals = defaultdict(int)
    author = None
    for line in p.stdout.splitlines():
        if line.startswith("\x01"):
            author = line[1:]
            continue
        parts = line.split("\t")
        if len(parts) != 3 or author is None:
            continue
        add, dele, fname = parts
        if add == "-" or dele == "-":        # binary file
            continue
        if EXCLUDE_RE.search(fname) or not fname.endswith(SOURCE_EXT):
            continue
        totals[author] += int(add) - int(dele)
    return totals


def icla_on_file():
    """Contacts recorded in CONTRIBUTORS.md as having an agreement on file."""
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    path = os.path.join(here, "CONTRIBUTORS.md")
    if not os.path.exists(path):
        return set()
    known = set()
    for line in open(path):
        if not line.startswith("|") or line.startswith("|---") or "ICLA" in line:
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) >= 4 and cells[3] and not cells[3].lower().startswith("no"):
            known.add(cells[1].lower())
    return known


def check_contributors(repos):
    known = icla_on_file()
    print(f"CONTRIBUTORS.md records an agreement or exemption for "
          f"{len(known)} contact(s).\n")
    workdir = tempfile.mkdtemp(prefix="ca-sweep-")
    over = defaultdict(dict)
    try:
        for name, branch in repos:
            totals = net_additions(name, branch, workdir)
            if totals is None:
                print(f"  ?     {name}: could not clone")
                continue
            hits = {a: n for a, n in totals.items()
                    if n > THRESHOLD and a.split("<")[0].strip() not in BOTS}
            print(f"  {'FLAG ' if hits else 'ok   '} {name}  ({len(totals)} author(s))")
            for a, n in sorted(hits.items(), key=lambda kv: -kv[1]):
                print(f"         {n:>7} net source lines  {a}")
                over[a][name] = n
    finally:
        shutil.rmtree(workdir, ignore_errors=True)

    print(f"\n== Clause 3: contributors over {THRESHOLD} cumulative net source lines ==")
    needs = []
    for author, per_repo in sorted(over.items(), key=lambda kv: -sum(kv[1].values())):
        email = author.split("<")[-1].rstrip(">").lower()
        if email in known:
            status = "agreement on file"
        else:
            status = "*** NO AGREEMENT RECORDED ***"
            needs.append(author)
        print(f"  {sum(per_repo.values()):>7} total  {author}  [{status}]")
        for r, n in sorted(per_repo.items(), key=lambda kv: -kv[1]):
            print(f"            {n:>7}  {r}")
    return needs


def main():
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--settings", action="store_true")
    ap.add_argument("--contributors", action="store_true")
    a = ap.parse_args()
    both = not (a.settings or a.contributors)

    problems, needs = [], []
    if a.settings or both:
        print("#" * 70)
        print("# Settings drift (CA-S1, CA-S2, CA-S3, CA-T1, CA-T2)")
        print("#" * 70)
        problems = check_settings(active_repos())
    if a.contributors or both:
        print("\n" + "#" * 70)
        print("# Cumulative contribution sweep (significance threshold, clause 3)")
        print("#" * 70)
        needs = check_contributors(active_repos())

    print("\n" + "=" * 70)
    if problems:
        print(f"{len(problems)} settings problem(s) -- see above.")
    if needs:
        print(f"{len(needs)} contributor(s) past the threshold with no agreement recorded:")
        for n in needs:
            print(f"  - {n}")
        print("\nReach out while they are still active. An unreachable contributor is\n"
              "the residual risk this sweep exists to bound -- and in practice that is\n"
              "rarely a vanished person, it is far more often a willing one whose answer\n"
              "is \"I would have to run it past legal\", after which nothing happens.")
    if not problems and not needs:
        print("Clean: no settings drift, nobody past the threshold unpapered.")
    return 1 if (problems or needs) else 0


if __name__ == "__main__":
    sys.exit(main())
