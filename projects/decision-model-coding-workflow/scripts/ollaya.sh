#!/bin/sh
# Run Ollaya with its binary, models, logs, and HOME kept inside this folder, on loopback only.
#   scripts/ollaya.sh serve              start the server on 127.0.0.1:11435 and leave it running
#   scripts/ollaya.sh pull winnow:e4b    download the local decision model (8.0 GB)
# Start the server before any other command, or the CLI starts its own untracked background server.
set -eu
PKG="$(cd "$(dirname "$0")/.." && pwd)"
export HOME="$PKG/.ollaya/home"
export OLLAYA_HOST=127.0.0.1:11435
export OLLAYA_MODELS="${OLLAYA_MODELS:-$PKG/.ollaya/models}"
export OLLAYA_LOG_DIR="$PKG/.ollaya/logs"
export OLLAYA_KEEP_ALIVE=-1
mkdir -p "$HOME" "$OLLAYA_LOG_DIR"
exec "$PKG/.ollaya/bin/ollaya" "$@"
