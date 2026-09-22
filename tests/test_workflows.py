"""Functional tests for the CA-T1 (DCO) and CA-T2 (significance) workflows.

These workflows are called by every psstools repository, so a regression here
is a regression everywhere at once. The tests extract the Python heredocs
straight out of the workflow YAML and run them against synthetic API payloads
-- no network, no Actions runner, no fixtures to keep in step with the source.

    python3 tests/test_workflows.py

Requires PyYAML and nothing else.
"""
import json, os, subprocess, sys, tempfile, yaml

SP = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")


def heredocs(run):
    out, cur = [], None
    for line in (run or "").split("\n"):
        if cur is None:
            if "<<'PY'" in line:
                cur = []
        elif line.strip() == "PY":
            out.append("\n".join(cur)); cur = None
        else:
            cur.append(line)
    return out


def extract(path, job, step, idx=0):
    d = yaml.safe_load(open(os.path.join(SP, path)))
    return heredocs(d["jobs"][job]["steps"][step]["run"])[idx]


def run_py(code, files):
    with tempfile.TemporaryDirectory() as td:
        for name, obj in files.items():
            with open(os.path.join(td, name), "w") as fh:
                json.dump(obj, fh)
        p = subprocess.run([sys.executable, "-c", code], cwd=td,
                           capture_output=True, text=True)
        return p


def commit(sha, msg, author_email, committer_email=None, parents=1):
    return {
        "sha": sha,
        "parents": [{"sha": "p"}] * parents,
        "commit": {
            "message": msg,
            "author": {"name": "A", "email": author_email},
            "committer": {"name": "C", "email": committer_email or author_email},
        },
    }


def f(name, status="modified", add=0, dele=0):
    return {"filename": name, "status": status, "additions": add, "deletions": dele}


fails = []


def check(label, cond, detail=""):
    print(("PASS  " if cond else "FAIL  ") + label + (("  -- " + detail) if not cond and detail else ""))
    if not cond:
        fails.append(label)


# ---------------------------------------------------------------- CA-T1 DCO
dco = extract(".github/workflows/dco.yml", "dco", 0)
SIGNED = "fix thing\n\nSigned-off-by: A <a@example.com>"

cases = [
    ("dco: properly signed passes", [commit("1" * 40, SIGNED, "a@example.com")], 0),
    ("dco: missing trailer fails", [commit("2" * 40, "fix thing", "a@example.com")], 1),
    ("dco: mismatched email fails",
     [commit("3" * 40, "x\n\nSigned-off-by: B <b@example.com>", "a@example.com")], 1),
    ("dco: case-insensitive email passes",
     [commit("4" * 40, "x\n\nSigned-off-by: A <A@Example.COM>", "a@example.com")], 0),
    ("dco: committer-matched signoff passes",
     [commit("5" * 40, "x\n\nSigned-off-by: C <c@example.com>", "a@example.com", "c@example.com")], 0),
    ("dco: merge commit skipped",
     [commit("6" * 40, "Merge branch", "a@example.com", parents=2)], 0),
    ("dco: one bad among good fails",
     [commit("7" * 40, SIGNED, "a@example.com"), commit("8" * 40, "nope", "a@example.com")], 1),
    ("dco: trailing whitespace tolerated",
     [commit("9" * 40, "x\n\nSigned-off-by:  A <a@example.com>  ", "a@example.com")], 0),
]
for label, commits, want in cases:
    p = run_py(dco, {"commits.json": commits})
    check(label, p.returncode == want, f"rc={p.returncode} want={want}\n{p.stdout}\n{p.stderr}")

# -------------------------------------------------------- CA-T2 significance
sig = extract(".github/workflows/significance.yml", "significance", 0)


def verdict(files):
    p = run_py(sig, {"files.json": files})
    assert p.returncode == 0, p.stderr
    return json.loads(p.stdout)


v = verdict([f("src/pssparser/newmod.py", "added", 20)])
check("sig: new src/ file trips clause 1", v["clause1"] and v["trips"], json.dumps(v))

v = verdict([f("src/pssparser/existing.py", "modified", 150, 10)])
check("sig: 140 net lines trips clause 2", v["clause2"] and not v["clause1"], json.dumps(v))

v = verdict([f("src/pssparser/existing.py", "modified", 40, 5)])
check("sig: 35 net lines does not trip", not v["trips"], json.dumps(v))

v = verdict([f("src/pssparser/existing.py", "modified", 101, 0)])
check("sig: 101 net trips, 100 is the floor", v["clause2"], json.dumps(v))

v = verdict([f("src/pssparser/existing.py", "modified", 100, 0)])
check("sig: exactly 100 net does not trip", not v["trips"], json.dumps(v))

v = verdict([f("src/pssparser/generated/PSSLexer.py", "added", 9000)])
check("sig: ANTLR generated file excluded", not v["trips"] and v["skipped"] == 1, json.dumps(v))

v = verdict([f("src/pssparser/PSSParserVisitor.py", "added", 4000)])
check("sig: *Visitor.py excluded by name", not v["trips"], json.dumps(v))

v = verdict([f("poetry.lock", "modified", 900, 800), f("package-lock.json", "modified", 500, 400)])
check("sig: lockfiles excluded", not v["trips"], json.dumps(v))

v = verdict([f("third_party/zlib/zlib.c", "added", 5000)])
check("sig: vendored tree excluded", not v["trips"], json.dumps(v))

v = verdict([f("docs/guide.md", "added", 900)])
check("sig: docs-only PR does not trip", not v["trips"], json.dumps(v))

v = verdict([f("README.md", "modified", 300, 1)])
check("sig: markdown not counted as source", not v["trips"], json.dumps(v))

v = verdict([f("ts/src/index.ts", "added", 10)])
check("sig: new file under ts/ trips clause 1", v["clause1"], json.dumps(v))

v = verdict([f("tests/test_foo.py", "added", 10)])
check("sig: new test file does not trip clause 1", not v["clause1"], json.dumps(v))

v = verdict([f("src/pssparser/a.py", "modified", 60, 0), f("python/b.py", "modified", 60, 0)])
check("sig: line count aggregates across files", v["clause2"], json.dumps(v))

v = verdict([f("src/pssparser/a.py", "modified", 20, 400)])
check("sig: large deletion does not trip", not v["trips"], json.dumps(v))

print()
print(f"{len(fails)} failure(s)" if fails else "all green")
sys.exit(1 if fails else 0)
