"""Replay one saved packet: send its state and next_check question to a decision model, print the answer.

The packets in packets/ are the exact inputs every selector received in the scored run. This is the
experiment's tutorial helper (tools/tutorial_next_check.py), unchanged apart from this docstring.

    uv run python replay_packet.py packets/I01-k6w753.json --backend local
    uv run python replay_packet.py packets/I01-k6w753.json --backend jev --keychain-service typesafe-api-key
"""

import argparse
import json
import os
import subprocess
import time

import httpx

BACKENDS = {
    # hosted: TLS, the real TypeSafe host, the pinned Jev version
    "jev": {"base_url": "https://api.typesafe.ai", "model": "jev-1.13.0", "trust_env": True},
    # local: Ollaya on loopback, same request shape; trust_env=False keeps a system proxy out of the path
    "local": {"base_url": "http://127.0.0.1:11435", "model": "winnow:e4b", "trust_env": False},
}


def api_key(backend: str, keychain_service: str | None) -> str:
    if backend == "local":
        return "local"  # Ollaya accepts any key; never send the hosted key to localhost
    if keychain_service:  # macOS Keychain, so the key never sits in the shell environment
        return subprocess.run(["security", "find-generic-password", "-a", os.environ["USER"], "-s", keychain_service, "-w"],
                              capture_output=True, text=True, check=True).stdout.strip()
    return os.environ["TYPESAFE_API_KEY"]


def next_check(packet: dict, backend: str, key: str) -> dict:
    config = BACKENDS[backend]
    body = {"model": config["model"], "state": packet["state"], "questions": packet["questions"]}
    with httpx.Client(base_url=config["base_url"], timeout=60, trust_env=config["trust_env"], follow_redirects=False) as client:
        started = time.perf_counter()
        response = client.post("/v1/systemone", json=body, headers={"Authorization": f"Bearer {key}"})
        elapsed_ms = (time.perf_counter() - started) * 1000
    response.raise_for_status()
    data = response.json()
    answer = data["answers"]["next_check"]
    if answer["choice"] not in packet["questions"]["next_check"]["criteria"]:
        raise ValueError(f"unexpected option {answer['choice']!r}")
    return {"model": data["model"], "choice": answer["choice"], "probabilities": answer["probabilities"],
            "confidence": answer["confidence"], "usage": data["usage"], "elapsed_ms": round(elapsed_ms, 1)}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("packet")
    parser.add_argument("--backend", choices=sorted(BACKENDS), default="local")
    parser.add_argument("--keychain-service")
    parser.add_argument("--out", help="also write the result as JSON to this path")
    args = parser.parse_args()
    with open(args.packet) as handle:
        packet = json.load(handle)
    result = next_check(packet, args.backend, api_key(args.backend, args.keychain_service))
    print(json.dumps(result, indent=2))
    if args.out:
        with open(args.out, "w") as handle:
            json.dump(result, handle, indent=2)


if __name__ == "__main__":
    main()
