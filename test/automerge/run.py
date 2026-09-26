"""Runs the decision script of .github/workflows/dependabot-merge.yml against canned API
answers, through a fake `gh`, and checks for each case whether it would merge.

Every rule the workflow enforces has a case here, so a change that loosens one fails CI
before any repository can pick it up.
"""
import copy, json, os, pathlib, re, subprocess, sys, tempfile, textwrap

ROOT = pathlib.Path(__file__).resolve().parents[2]
WORKFLOW = ROOT / ".github/workflows/dependabot-merge.yml"
REPO, HEAD, OLD = "KN990x/example", "a" * 40, "b" * 40

source = WORKFLOW.read_text()
script = textwrap.dedent(re.search(r"python3 - <<'PY'\n(.*?)\n\s*PY\n", source, re.S).group(1))

FAKE_GH = r'''#!/usr/bin/env python3
import json, os, sys
scenario = json.load(open(os.environ["SCENARIO"]))
args = sys.argv[1:]
if args[:1] == ["api"]:
    path = args[1]
    for key in sorted(scenario["api"], key=len, reverse=True):
        if path.startswith(key):
            print(json.dumps(scenario["api"][key]))
            sys.exit(0)
    sys.exit(f"fake gh: no answer for {path}")
with open(os.environ["CALLS"], "a") as fh:
    fh.write(" ".join(args) + "\n")
'''

METADATA = "Bump x\n\n---\nupdated-dependencies:\n- dependency-name: x\n  update-type: version-update:semver-{kind}\n...\n"

def base():
    pr = {"state": "open", "user": {"login": "dependabot[bot]"}, "labels": [],
          "head": {"sha": HEAD, "repo": {"full_name": REPO}},
          "mergeable": True, "mergeable_state": "clean", "title": "Bump x in the npm group"}
    return {"api": {
        f"repos/{REPO}/pulls/7/reviews": [{"user": {"login": "KN990x"}, "state": "APPROVED", "commit_id": HEAD}],
        f"repos/{REPO}/pulls/7/commits": [{"author": {"login": "dependabot[bot]"},
                                           "commit": {"message": METADATA.format(kind="minor")}}],
        f"repos/{REPO}/pulls/7/files": [{"filename": "pnpm-lock.yaml", "patch": "-a\n+b"},
                                        {"filename": "package.json", "patch": "-a\n+b"}],
        f"repos/{REPO}/pulls/7": pr,
        f"repos/{REPO}/actions/workflows/ci.yml/runs": {"total_count": 1},
    }}

def case(name, expect_merge, mutate=lambda s: None, event="pull_request_review", extra_env=None):
    scenario = base()
    mutate(scenario)
    with tempfile.TemporaryDirectory() as tmp:
        tmp = pathlib.Path(tmp)
        (tmp / "gh").write_text(FAKE_GH)
        (tmp / "gh").chmod(0o755)
        (tmp / "scenario.json").write_text(json.dumps(scenario))
        calls = tmp / "calls"
        env = {**os.environ, "PATH": f"{tmp}:{os.environ['PATH']}", "SCENARIO": str(tmp / "scenario.json"),
               "CALLS": str(calls), "REPO": REPO, "OWNER": "KN990x", "DEFAULT_BRANCH": "main",
               "EVENT_NAME": event, "RUN_CONCLUSION": "success", "RUN_PRS": json.dumps([{"number": 7}]),
               "REVIEW_PR": "7", "CI_WORKFLOW": "ci.yml", "APPROVERS": "", "MERGEABLE_WAIT": "0",
               "GITHUB_STEP_SUMMARY": ""}
        env.update(extra_env or {})
        out = subprocess.run([sys.executable, "-c", script], env=env, capture_output=True, text=True)
        made = calls.read_text() if calls.exists() else ""
        merged = "pr merge 7" in made
        ok = out.returncode == 0 and merged == expect_merge and (not merged or "workflow run ci.yml" in made)
        print(f"{'ok  ' if ok else 'FAIL'} {name}: {'merged' if merged else 'not merged'} — {out.stdout.strip() or out.stderr.strip()}")
        return ok

def set_path(path, value):
    def mutate(s):
        target = s["api"]
        *keys, last = path
        for k in keys:
            target = target[k]
        target[last] = value
    return mutate

R = f"repos/{REPO}/pulls/7"
results = [
    case("approved, green, routine (review event)", True),
    case("approved, green, routine (CI event)", True, event="workflow_run"),
    case("CI run failed", False, event="workflow_run", extra_env={"RUN_CONCLUSION": "failure"}),
    case("no green CI on the head", False, set_path([f"repos/{REPO}/actions/workflows/ci.yml/runs"], {"total_count": 0})),
    case("no review at all", False, set_path([f"{R}/reviews"], [])),
    case("approval on an older commit (rebased since)", False,
         set_path([f"{R}/reviews"], [{"user": {"login": "KN990x"}, "state": "APPROVED", "commit_id": OLD}])),
    case("approval by someone not authorised", False,
         set_path([f"{R}/reviews"], [{"user": {"login": "mallory"}, "state": "APPROVED", "commit_id": HEAD}])),
    case("custom approver list", True,
         set_path([f"{R}/reviews"], [{"user": {"login": "timon-bot"}, "state": "APPROVED", "commit_id": HEAD}]),
         extra_env={"APPROVERS": "timon-bot KN990x"}),
    case("approved, then changes requested", False,
         set_path([f"{R}/reviews"], [{"user": {"login": "KN990x"}, "state": "APPROVED", "commit_id": HEAD},
                                     {"user": {"login": "KN990x"}, "state": "CHANGES_REQUESTED", "commit_id": HEAD}])),
    case("changes requested, then approved on the head", True,
         set_path([f"{R}/reviews"], [{"user": {"login": "KN990x"}, "state": "CHANGES_REQUESTED", "commit_id": OLD},
                                     {"user": {"login": "KN990x"}, "state": "APPROVED", "commit_id": HEAD}])),
    case("not opened by Dependabot", False, set_path([R, "user", "login"], "someone")),
    case("labelled no-automerge", False, set_path([R, "labels"], [{"name": "no-automerge"}])),
    case("a human pushed on top", False,
         set_path([f"{R}/commits"], [{"author": {"login": "dependabot[bot]"}, "commit": {"message": METADATA.format(kind="minor")}},
                                     {"author": {"login": "someone"}, "commit": {"message": "tweak"}}])),
    case("major update", False,
         set_path([f"{R}/commits"], [{"author": {"login": "dependabot[bot]"}, "commit": {"message": METADATA.format(kind="major")}}])),
    case("touches source code", False,
         set_path([f"{R}/files"], [{"filename": "src/server/app.js", "patch": "-a\n+b"}])),
    case("workflow change beyond `uses:`", False,
         set_path([f"{R}/files"], [{"filename": ".github/workflows/ci.yml", "patch": "-  run: a\n+  run: b"}])),
    case("workflow pin bump", True,
         set_path([f"{R}/files"], [{"filename": ".github/workflows/ci.yml",
                                    "patch": "-      - uses: a/b@1111 # v1\n+      - uses: a/b@2222 # v2"}])),
    case("Dockerfile change beyond FROM", False,
         set_path([f"{R}/files"], [{"filename": "Dockerfile", "patch": "-RUN a\n+RUN b"}])),
    case("not mergeable", False, set_path([R, "mergeable"], False)),
    case("closed PR", False, set_path([R, "state"], "closed")),
]
print(f"{sum(results)}/{len(results)} cases behave.")
sys.exit(0 if all(results) else 1)
