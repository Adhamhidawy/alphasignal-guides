"""Ask one closed question after Claude Code's required checks pass: which ONE extra check should run?

The wrapper runs Claude Code on a task (optional), runs the repository's required checks, builds an
evidence packet from git, sends one next_check question to a decision model (hosted Jev or a local
Ollaya model), and logs the answer next to a filename rule's answer. In shadow mode (the default)
nothing else happens. With --run-extra it runs the one allowlisted suite the answer names.

The answer can only add a check. Required checks always run, a failed required check stops the
wrapper before any decision call, and nothing the model returns is executed as a command.

    uv run python next_check.py --repo demo --no-agent
    uv run python next_check.py --repo demo --no-agent --backend jev --keychain-service typesafe-api-key
    uv run python next_check.py --repo demo --run-extra
"""

import argparse
import glob
import hashlib
import json
import os
import re
import shlex
import subprocess
import time
import tomllib
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

import httpx

LOCAL_HOSTS = {"127.0.0.1", "localhost", "::1"}
COUNTS = re.compile(r"(\d+) (passed|failed|errors?)\b")
SECURITY_NAME = re.compile(r"(auth|login|secret|token|permission)", re.IGNORECASE)


def child_env() -> dict:
    # Claude Code and the test commands never see the hosted decision-model key.
    return {name: value for name, value in os.environ.items() if name != "TYPESAFE_API_KEY"}


def run_command(command, repo, stdin=None, timeout=900):
    argv = shlex.split(command) if isinstance(command, str) else list(command)
    return subprocess.run(argv, cwd=repo, input=stdin, capture_output=True, text=True, env=child_env(),
                          timeout=timeout)


def run_agent(config, repo, task, contract) -> dict:
    """Claude Code does the engineering. The wrapper hands it the task and the files it may edit."""
    agent = config["agent"]
    files = sorted({path for pattern in agent["files"] for path in glob.glob(pattern, root_dir=repo, recursive=True)})
    prompt = (f"Task:\n{task}\n\nDocumented contract:\n{contract}\n\n"
              "Source files you may read and edit (paths are relative to the working directory):\n"
              + "\n".join(f"- {path}" for path in files) + "\n")
    result = run_command(agent["command"], repo, stdin=prompt, timeout=agent.get("timeout_s", 900))
    try:
        envelope = json.loads(result.stdout)
    except json.JSONDecodeError:
        envelope = {"is_error": True, "result": result.stderr[-500:]}
    return {"exit_code": result.returncode, "is_error": envelope.get("is_error"),
            "cost_usd": envelope.get("total_cost_usd"), "permission_denials": len(envelope.get("permission_denials") or []),
            "summary": envelope.get("result")}


def run_check(name, command, repo) -> dict:
    """Run one check command. Pass/fail is the exit code; the last output line is the evidence."""
    result = run_command(command, repo)
    lines = [line.strip(" =") for line in result.stdout.splitlines() if line.strip(" =")]
    evidence = lines[-1][:200] if lines else result.stderr.strip()[-200:]
    counts = {kind.rstrip("s"): int(number) for number, kind in COUNTS.findall(evidence)}
    passed, failed = counts.get("passed", 0), counts.get("failed", 0) + counts.get("error", 0)
    return {"name": name, "command": command, "status": "pass" if result.returncode == 0 else "fail",
            "exit_code": result.returncode, "passed": passed, "failed": failed, "tests": passed + failed,
            "evidence": evidence}


def git(repo, *args) -> str:
    return subprocess.run(["git", *args], cwd=repo, capture_output=True, text=True).stdout


def diff_state(repo, budget) -> dict:
    """Changed paths, line counts, and the unified diff of the working tree against HEAD, new files included."""
    files = {}
    for line in git(repo, "diff", "--relative", "--no-renames", "--numstat", "HEAD").splitlines():
        added, removed, path = line.split("\t", 2)
        files[path] = {"insertions": int(added) if added != "-" else 0, "deletions": int(removed) if removed != "-" else 0}
    diff = git(repo, "diff", "--relative", "--no-renames", "HEAD")
    for path in git(repo, "ls-files", "--others", "--exclude-standard").splitlines():
        files[path] = {"insertions": len((Path(repo) / path).read_text(errors="replace").splitlines()), "deletions": 0}
        diff += git(repo, "diff", "--no-index", "--", "/dev/null", path)
    if len(diff) > budget:
        diff = diff[:budget] + f"\n[diff truncated at {budget} of {len(diff)} characters]\n"
    return {"changed_paths": sorted(files), "diff": diff,
            "diff_stat": {"files_changed": len(files), "insertions": sum(f["insertions"] for f in files.values()),
                          "deletions": sum(f["deletions"] for f in files.values()), "files": files}}


def rule_choice(changed_paths) -> str:
    """The baseline to beat: the experiment's filename rule. Replace it with the rule your team would write."""
    if any(SECURITY_NAME.search(path) for path in changed_paths):
        return "security_review"
    if len({path.rsplit("/", 1)[-1] for path in changed_paths}) >= 3:
        return "integration_tests"
    return "targeted_tests"


def api_key(base_url, keychain_service) -> str:
    if urlparse(base_url).hostname in LOCAL_HOSTS:
        return "local"  # a local Ollaya server accepts any key, so the hosted key never goes to localhost
    if keychain_service:  # macOS Keychain keeps the key out of the shell environment and history
        return subprocess.run(["security", "find-generic-password", "-a", os.environ["USER"], "-s", keychain_service, "-w"],
                              capture_output=True, text=True, check=True).stdout.strip()
    return os.environ["TYPESAFE_API_KEY"]


def decide(backend, state, question, key, transport=None) -> dict:
    """One POST to /v1/systemone: state plus one Choice question in, a typed answer with probabilities out."""
    body = {"model": backend["model"], "state": state, "questions": {"next_check": question}}
    local = urlparse(backend["base_url"]).hostname in LOCAL_HOSTS
    with httpx.Client(base_url=backend["base_url"], timeout=120, trust_env=not local, follow_redirects=False,
                      transport=transport) as client:
        started = time.perf_counter()
        response = client.post("/v1/systemone", content=json.dumps(body, sort_keys=True),  # same key order on every backend
                               headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"})
        elapsed_ms = (time.perf_counter() - started) * 1000
    response.raise_for_status()
    data = response.json()
    answer = data["answers"]["next_check"]
    if answer["choice"] not in question["criteria"]:
        raise ValueError(f"unexpected option {answer['choice']!r}")
    return {"model": data["model"], "choice": answer["choice"], "probabilities": answer["probabilities"],
            "confidence": answer["confidence"], "usage": data.get("usage"), "elapsed_ms": round(elapsed_ms, 1)}


def write_log(repo, row, packet):
    folder = Path(repo) / ".next-check"
    (folder / "packets").mkdir(parents=True, exist_ok=True)
    (folder / ".gitignore").write_text("*\n")  # keeps the log out of the diff the next run reads
    if packet:
        (folder / "packets" / f"{row['packet_sha256'][:12]}.json").write_text(json.dumps(packet, indent=2, sort_keys=True))
    with open(folder / "runs.jsonl", "a") as handle:
        handle.write(json.dumps(row, sort_keys=True) + "\n")


def main(argv=None, transport=None) -> int:
    parser = argparse.ArgumentParser(description="Ask a decision model which ONE extra check to run.")
    parser.add_argument("--repo", default=".", help="repository holding next_check.toml (default: current directory)")
    parser.add_argument("--task", help="task text (default: the file named by task_file in next_check.toml)")
    parser.add_argument("--no-agent", action="store_true", help="skip Claude Code and evaluate the current diff")
    parser.add_argument("--backend", default="local", help="a [backends.NAME] table in next_check.toml")
    parser.add_argument("--keychain-service", help="macOS Keychain service holding the hosted API key")
    parser.add_argument("--run-extra", action="store_true", help="run the suite the answer names (default: log only)")
    parser.add_argument("--min-confidence", type=float, help="below this, run nothing and ask for inspection (off by default)")
    args = parser.parse_args(argv)

    repo = Path(args.repo).resolve()
    config = tomllib.loads((repo / "next_check.toml").read_text())
    task = args.task or (repo / config["task_file"]).read_text().strip()
    contract = (repo / config["contract_file"]).read_text().strip() if config.get("contract_file") else ""
    row = {"time": datetime.now(timezone.utc).isoformat(timespec="seconds"), "task": task, "backend": args.backend,
           "mode": "active" if args.run_extra else "shadow"}

    if not args.no_agent:
        row["agent"] = run_agent(config, repo, task, contract)
        print(f"Claude Code finished: exit {row['agent']['exit_code']}, cost ${row['agent']['cost_usd']}")

    required = [run_check(check["name"], check["command"], repo) for check in config["required"]]
    row["required_checks"] = [{key: check[key] for key in ("name", "status", "evidence")} for check in required]
    for check in required:
        print(f"required  {check['name']}: {check['status']} ({check['evidence']})")
    if any(check["status"] != "pass" for check in required):
        print("A required check failed. Hand the log to the developer. No extra check is chosen.")
        write_log(repo, row, None)
        return 2

    state = {"task": task, **diff_state(repo, config.get("diff_char_budget", 12_000)), "required_checks": required,
             "available_checks": config["extra"]}
    if contract:
        state["contract"] = contract
    question = {"type": "choice", **config["question"]}
    packet = {"state": state, "questions": {"next_check": question}}
    row["packet_sha256"] = hashlib.sha256(json.dumps(packet, sort_keys=True).encode()).hexdigest()

    backend = config["backends"][args.backend]
    answer = decide(backend, state, question, api_key(backend["base_url"], args.keychain_service), transport)
    row.update(answer=answer, rule_choice=rule_choice(state["changed_paths"]), extra=None)
    choice = answer["choice"]
    print(f"decision  {answer['model']}: {choice} (p={answer['probabilities'][choice]}, "
          f"confidence={answer['confidence']}, {answer['elapsed_ms']} ms); filename rule: {row['rule_choice']}")

    if choice == "inspect_first" or (args.min_confidence is not None and answer["confidence"] < args.min_confidence):
        print("No extra suite chosen with enough confidence. Ask a person to inspect the change.")
    elif args.run_extra:
        row["extra"] = run_check(choice, config["extra"][choice]["command"], repo)  # only allowlisted commands run
        print(f"extra     {choice}: {row['extra']['status']} ({row['extra']['evidence']})")
    else:
        print(f"shadow mode: logged, not run ({config['extra'][choice]['command']})")
    write_log(repo, row, packet)
    return 1 if row["extra"] and row["extra"]["status"] == "fail" else 0


if __name__ == "__main__":
    raise SystemExit(main())
