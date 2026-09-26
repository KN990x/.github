#!/usr/bin/env bash
# Same interface as every repository's smoke test: <image> <container-name> [platform].
set -euo pipefail

IMAGE="${1:?image required}"
NAME="${2:?container name required}"
PLATFORM="${3:-}"

trap 'docker rm -f "$NAME" >/dev/null 2>&1 || true' EXIT

platform_args=()
if [ -n "$PLATFORM" ]; then
  platform_args=(--platform "$PLATFORM")
fi

docker run -d --name "$NAME" "${platform_args[@]}" -p 8080:8080 "$IMAGE"
for _ in $(seq 1 60); do
  if curl -fsS http://127.0.0.1:8080/ | grep -q pipeline-fixture-ok; then
    echo "Fixture answered${PLATFORM:+ on $PLATFORM}."
    exit 0
  fi
  sleep 1
done
echo "::error::The fixture never answered"
docker logs "$NAME"
exit 1
