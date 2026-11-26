#!/usr/bin/env bash
# Build Keymood for the iOS simulator, install it and launch it.
#
#   ./mobile/run-sim.sh                 the booted simulator
#   ./mobile/run-sim.sh <device-udid>   a specific one
#
# A good run ends with "[sim] launched", and Keymood opens in the simulator.
#
# Needs network the first time, to fetch Capacitor's Swift package. Run it from a
# normal terminal: inside a sandboxed shell xcodebuild cannot download it and waits
# forever on "Checking out ... capacitor-swift-pm" (AstroVarium met the same).

set -euo pipefail
cd "$(dirname "$0")"
DEV="${1:-booted}"
LOG="${TMPDIR:-/tmp}/keymood-sim-build.log"

./sync-web.sh | grep -E "FAIL|\[verify\]" || true
echo "[sim] building (the first time fetches Capacitor, a minute or two) ..."
xcodebuild -project ios/App/App.xcodeproj -scheme App -configuration Debug \
  -sdk iphonesimulator -destination "generic/platform=iOS Simulator" \
  -derivedDataPath build-sim build > "$LOG" 2>&1 \
  || { echo "[sim] BUILD FAILED, first errors:"; grep -E "error:" "$LOG" | head -10; exit 1; }
echo "[sim] built"
xcrun simctl install "$DEV" build-sim/Build/Products/Debug-iphonesimulator/App.app
xcrun simctl launch --terminate-running-process "$DEV" app.keymood.mobile >/dev/null
echo "[sim] launched"
