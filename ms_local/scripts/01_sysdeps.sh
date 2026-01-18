#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/00_env.sh"

# Ubuntu/Debian 기준
if ! command -v apt-get >/dev/null 2>&1; then
  echo "apt-get not found. Please install build deps manually for your distro." >&2
  exit 1
fi

sudo apt-get update
sudo apt-get install -y --no-install-recommends \
  git git-lfs ca-certificates curl wget \
  build-essential ninja-build cmake pkg-config \
  ccache \
  python3-venv python3-dev

# ccache 초기 설정
ccache --max-size="$CCACHE_MAXSIZE" || true
ccache -z || true

echo "OK: system deps installed."

