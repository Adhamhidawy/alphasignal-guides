"""Offline tests for next_check.py: temporary git repos, a mocked decision endpoint, a fake agent."""

import json
import subprocess
import sys
import textwrap

import httpx
import pytest

import next_check

QUESTION = {"instructions": "Pick one.", "criteria": {
    "targeted_tests": "t", "integration_tests": "i", "security_review": "s", "inspect_first": "x"}}


def git(repo, *args):
    subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True)


def make_repo(tmp_path, required_ok=True):
    repo = tmp_path / "repo"
    (repo / "src").mkdir(parents=True)
    (repo / "src" / "app.py").write_text("VALUE = 1\n")
    (repo / "TASK.md").write_text("Make VALUE two.\n")
    py = sys.executable
    fake_agent = repo / "fake_agent.py"
    fake_agent.write_text(textwrap.dedent("""
        import json, pathlib, sys
        prompt = sys.stdin.read()
        pathlib.Path("src/app.py").write_text("VALUE = 2\\n")
        print(json.dumps({"is_error": False, "total_cost_usd": 0.01, "result": "Changed VALUE.",
                          "permission_denials": [], "prompt_seen": prompt}))
    """))
    config = {
        "task_file": "TASK.md",
        "required": [{"name": "always", "command": f"{py} -c \"print('1 passed in 0.01s')\""}],
        "extra": {
            "targeted_tests": {"command": f"{py} -c \"print('2 passed in 0.01s')\"", "description": "t", "tests": ["a"]},
            "integration_tests": {"command": f"{py} -c \"import sys; print('1 failed, 3 passed in 0.02s'); sys.exit(1)\"",
                                  "description": "i", "tests": ["b"]},
            "security_review": {"command": f"{py} -c \"print('3 passed in 0.01s')\"", "description": "s", "tests": ["c"]},
        },
        "agent": {"files": ["src/**/*.py"], "command": [py, str(fake_agent)]},
        "question": QUESTION,
        "backends": {"local": {"base_url": "http://127.0.0.1:11435", "model": "winnow:e4b"},
                     "jev": {"base_url": "https://api.typesafe.ai", "model": "jev-1.13.0"}},
    }
    if not required_ok:
        config["required"].append({"name": "broken", "command": f"{py} -c \"import sys; print('1 failed in 0.01s'); sys.exit(1)\""})
    (repo / "next_check.toml").write_text(to_toml(config))
    git(repo, "init", "-q")
    git(repo, "add", "-A")
    git(repo, "-c", "user.name=t", "-c", "user.email=t@example.invalid", "commit", "-q", "-m", "base")
    return repo


def to_toml(config):
    def value(v):
        if isinstance(v, str):
            return json.dumps(v)
        if isinstance(v, list):
            return "[" + ", ".join(value(x) for x in v) + "]"
        raise TypeError(v)
    lines = [f'task_file = {value(config["task_file"])}']
    lines += ["[agent]", f'files = {value(config["agent"]["files"])}', f'command = {value(config["agent"]["command"])}']
    for check in config["required"]:
        lines += ["[[required]]", f'name = {value(check["name"])}', f'command = {value(check["command"])}']
    for name, suite in config["extra"].items():
        lines += [f"[extra.{name}]"] + [f"{k} = {value(v)}" for k, v in suite.items()]
    lines += ["[question]", f'instructions = {value(config["question"]["instructions"])}', "[question.criteria]"]
    lines += [f"{k} = {value(v)}" for k, v in config["question"]["criteria"].items()]
    for name, backend in config["backends"].items():
        lines += [f"[backends.{name}]"] + [f"{k} = {value(v)}" for k, v in backend.items()]
    return "\n".join(lines) + "\n"


class Endpoint:
    """Records requests and answers like /v1/systemone."""

    def __init__(self, choice="integration_tests", confidence=0.78):
        self.requests, self.choice, self.confidence = [], choice, confidence

    def __call__(self, request):
        self.requests.append(request)
        body = json.loads(request.content)
        probabilities = {option: 0.0 for option in body["questions"]["next_check"]["criteria"]}
        probabilities[self.choice] = 1.0
        return httpx.Response(200, json={"model": body["model"], "usage": {"input_tokens": 10, "output_tokens": 0},
                                         "answers": {"next_check": {"type": "choice", "choice": self.choice,
                                                                    "probabilities": probabilities,
                                                                    "confidence": self.confidence}}})


def runs(repo):
    return [json.loads(line) for line in (repo / ".next-check" / "runs.jsonl").read_text().splitlines()]


def test_rule_choice_matches_the_experiment_rule():
    assert next_check.rule_choice(["src/auth/session.py"]) == "security_review"
    assert next_check.rule_choice(["src/token_messages.py"]) == "security_review"
    assert next_check.rule_choice(["src/a.py", "src/b.py", "lib/c.py"]) == "integration_tests"
    assert next_check.rule_choice(["src/a.py", "lib/a.py", "src/b.py"]) == "targeted_tests"  # 2 distinct basenames
    assert next_check.rule_choice(["src/repository.py"]) == "targeted_tests"


def test_diff_state_includes_new_files_counts_lines_and_truncates(tmp_path):
    repo = make_repo(tmp_path)
    (repo / "src" / "app.py").write_text("VALUE = 2\nOTHER = 3\n")
    (repo / "src" / "new.py").write_text("a = 1\nb = 2\n")
    state = next_check.diff_state(repo, budget=100_000)
    assert state["changed_paths"] == ["src/app.py", "src/new.py"]
    assert state["diff_stat"]["files"]["src/app.py"] == {"insertions": 2, "deletions": 1}
    assert state["diff_stat"]["files"]["src/new.py"] == {"insertions": 2, "deletions": 0}
    assert "+OTHER = 3" in state["diff"] and "+b = 2" in state["diff"]
    short = next_check.diff_state(repo, budget=40)
    assert "[diff truncated at 40 of" in short["diff"]


def test_diff_state_ignores_its_own_log_folder(tmp_path):
    repo = make_repo(tmp_path)
    next_check.write_log(repo, {"packet_sha256": "0" * 64}, {"state": {}})
    assert next_check.diff_state(repo, budget=1000)["changed_paths"] == []


def test_run_check_reads_status_and_pytest_counts(tmp_path):
    py = sys.executable
    ok = next_check.run_check("ok", f"{py} -c \"print('=== 7 passed in 0.15s ===')\"", tmp_path)
    assert ok["status"] == "pass" and ok["passed"] == 7 and ok["tests"] == 7 and ok["evidence"] == "7 passed in 0.15s"
    bad = next_check.run_check("bad", f"{py} -c \"import sys; print('1 failed, 3 passed, 2 errors in 1s'); sys.exit(1)\"", tmp_path)
    assert bad["status"] == "fail" and bad["failed"] == 3 and bad["passed"] == 3 and bad["exit_code"] == 1


def test_child_processes_never_see_the_hosted_key(monkeypatch):
    monkeypatch.setenv("TYPESAFE_API_KEY", "sk-test-not-real")
    assert "TYPESAFE_API_KEY" not in next_check.child_env()


def test_local_backend_gets_a_dummy_key_even_when_a_hosted_key_is_set(monkeypatch):
    monkeypatch.setenv("TYPESAFE_API_KEY", "sk-test-not-real")
    assert next_check.api_key("http://127.0.0.1:11435", None) == "local"
    assert next_check.api_key("https://api.typesafe.ai", None) == "sk-test-not-real"


def test_decide_sends_exactly_model_state_questions_with_sorted_keys():
    endpoint = Endpoint()
    question = {"type": "choice", **QUESTION}
    answer = next_check.decide({"base_url": "http://127.0.0.1:11435", "model": "winnow:e4b"}, {"b": 1, "a": 2},
                               question, "local", transport=httpx.MockTransport(endpoint))
    request = endpoint.requests[0]
    assert request.url.path == "/v1/systemone" and request.headers["Authorization"] == "Bearer local"
    assert request.content == json.dumps({"model": "winnow:e4b", "state": {"a": 2, "b": 1},
                                          "questions": {"next_check": question}}, sort_keys=True).encode()
    assert answer["choice"] == "integration_tests" and answer["confidence"] == 0.78


def test_decide_rejects_an_option_outside_the_menu():
    endpoint = Endpoint(choice="ship_it")
    with pytest.raises(ValueError):
        next_check.decide({"base_url": "http://127.0.0.1:11435", "model": "m"}, {}, {"type": "choice", **QUESTION},
                          "local", transport=httpx.MockTransport(endpoint))


def test_shadow_mode_runs_agent_and_required_checks_then_logs_without_running_extra(tmp_path):
    repo = make_repo(tmp_path)
    endpoint = Endpoint()
    assert next_check.main(["--repo", str(repo)], transport=httpx.MockTransport(endpoint)) == 0
    row = runs(repo)[0]
    assert row["mode"] == "shadow" and row["extra"] is None
    assert row["agent"]["cost_usd"] == 0.01 and row["answer"]["choice"] == "integration_tests"
    assert row["rule_choice"] == "targeted_tests"
    state = json.loads(endpoint.requests[0].content)["state"]
    assert state["changed_paths"] == ["src/app.py"] and "+VALUE = 2" in state["diff"]
    assert state["required_checks"][0]["evidence"] == "1 passed in 0.01s"
    assert set(state["available_checks"]) == {"targeted_tests", "integration_tests", "security_review"}
    saved = list((repo / ".next-check" / "packets").glob("*.json"))
    assert len(saved) == 1 and json.loads(saved[0].read_text())["state"] == state


def test_agent_prompt_lists_task_and_editable_files(tmp_path):
    repo = make_repo(tmp_path)
    result = next_check.run_agent(next_check.tomllib.loads((repo / "next_check.toml").read_text()), repo,
                                  "Make VALUE two.", "")
    assert result["is_error"] is False and result["summary"] == "Changed VALUE."


def test_run_extra_runs_only_the_allowlisted_command_for_the_choice(tmp_path):
    repo = make_repo(tmp_path)
    code = next_check.main(["--repo", str(repo), "--no-agent", "--run-extra"],
                           transport=httpx.MockTransport(Endpoint("integration_tests")))
    row = runs(repo)[0]
    assert code == 1 and row["extra"]["name"] == "integration_tests" and row["extra"]["status"] == "fail"
    assert row["extra"]["failed"] == 1 and "agent" not in row


def test_inspect_first_and_low_confidence_run_nothing(tmp_path):
    repo = make_repo(tmp_path)
    assert next_check.main(["--repo", str(repo), "--no-agent", "--run-extra"],
                           transport=httpx.MockTransport(Endpoint("inspect_first"))) == 0
    assert next_check.main(["--repo", str(repo), "--no-agent", "--run-extra", "--min-confidence", "0.5"],
                           transport=httpx.MockTransport(Endpoint("targeted_tests", confidence=0.2))) == 0
    assert [row["extra"] for row in runs(repo)] == [None, None]


def test_failed_required_check_stops_before_any_decision_call(tmp_path):
    repo = make_repo(tmp_path, required_ok=False)
    endpoint = Endpoint()
    assert next_check.main(["--repo", str(repo), "--no-agent"], transport=httpx.MockTransport(endpoint)) == 2
    assert endpoint.requests == [] and "answer" not in runs(repo)[0]
