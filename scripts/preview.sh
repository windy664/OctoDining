#!/usr/bin/env bash
set -euo pipefail

project_root=$(cd "$(dirname "$0")/.." && pwd)
octo_cli=${OCTO_CLI:-/home/windy/Project/octosense-ws/OctoScript-App-Design-Flow/tools/octo}
preview_bundle="$project_root/.local-state/preview-bundle"

cd "$project_root"
python3 scripts/dev_bundle.py --output "$preview_bundle"
if curl --connect-timeout 1 --max-time 2 -fsS http://127.0.0.1:8141/quit >/dev/null 2>&1; then
    echo "Stopped the previous preview on port 8141."
    for _attempt in 1 2 3 4 5 6 7 8 9 10; do
        if ! curl --connect-timeout 1 --max-time 1 -fsS http://127.0.0.1:8141/s >/dev/null 2>&1; then
            break
        fi
        sleep 0.1
    done
fi
"$octo_cli" check "$preview_bundle"
"$octo_cli" run "$preview_bundle" --port 8141 --detach
echo "Preview started. Agent-unavailable responses use the clearly labelled local preview mode."
