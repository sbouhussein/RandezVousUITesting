#!/usr/bin/env bash
# Proof of concept: one entry point for running the UI tests, headless or on a visible simulator/emulator.
#
#   ./scripts/run_tests.sh <category> [--headless | --visible] [options] [-- extra pytest args]
#
# Categories (by what the test checks; each runs on the platforms that have tests for it):
#   all     every test: web, then iOS, then Android
#   smoke   a few fast checks of the most important flows
#   ux      user-facing flows: joining, activities, feed, leaderboard, entry points
#   access  bans, domain restrictions, ended/expired quests, onboarding fallbacks
#   push    notification tests that send real pushes (slow)
#   web     only web tests (desktop Chrome), whatever their category
#   ios     only iOS tests on the simulator
#   android only Tests/web/android (Android emulator + Android-user-agent Chrome)
# Categories are pytest markers assigned in RandezVousUITests/conftest.py.
#
# Modes:
#   --headless  no windows: Chrome headless, iOS simulator booted without the Simulator app, emulator with -no-window (default)
#   --visible   Chrome, Simulator and emulator windows on screen, so you can watch
#
# Options:
#   --udid <id>   iOS simulator to use (else $IOS_UDID, else the simulator that is already booted)
#   --avd <name>  Android emulator to use (else $ANDROID_DEVICE_NAME, else Pixel_8_API_34)
#   --platform <web|ios|android>  limit smoke/ux/access/push to one platform
#   --dry-run     print what would run without starting anything
#   --list        list the selected tests without running them
#
# Everything after `--` goes straight to pytest, e.g.  ./scripts/run_tests.sh web -- -k notifications

set -u

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TESTS_DIR="$ROOT/RandezVousUITests"
SDK_ROOT="${ANDROID_HOME:-${ANDROID_SDK_ROOT:-$HOME/Library/Android/sdk}}"

CATEGORY=""
MODE="headless"
UDID="${IOS_UDID:-}"
AVD="${ANDROID_DEVICE_NAME:-Pixel_8_API_34}"
DRY_RUN=0
LIST_ONLY=0
PLATFORM=""
EXTRA=()

usage() { sed -n '2,/^$/p' "$0" | sed 's/^# \{0,1\}//'; exit "${1:-0}"; }

while [ $# -gt 0 ]; do
  case "$1" in
    all|smoke|ux|access|push|web|ios|android) CATEGORY="$1" ;;
    --headless) MODE="headless" ;;
    --visible)  MODE="visible" ;;
    --udid)     UDID="${2:?--udid needs a value}"; shift ;;
    --avd)      AVD="${2:?--avd needs a value}"; shift ;;
    --platform) PLATFORM="${2:?--platform needs web, ios or android}"; shift ;;
    --dry-run)  DRY_RUN=1 ;;
    --list)     LIST_ONLY=1 ;;
    -h|--help)  usage 0 ;;
    --)         shift; EXTRA=("$@"); break ;;
    *)          echo "Unknown argument: $1" >&2; usage 1 ;;
  esac
  shift
done

[ -n "$CATEGORY" ] || { echo "Pick a category: all | smoke | ux | access | push | web | ios | android" >&2; usage 1; }

say() { echo "==> $*"; }
# Runs a command, or only prints it with --dry-run.
run() {
  if [ "$DRY_RUN" -eq 1 ]; then echo "[dry-run] $*"; return 0; fi
  "$@"
}

# ---- devices ---------------------------------------------------------------------------------

ensure_ios_simulator() {
  if [ -z "$UDID" ]; then
    UDID="$(xcrun simctl list devices booted 2>/dev/null | grep -Eo '[0-9A-F]{8}-([0-9A-F]{4}-){3}[0-9A-F]{12}' | head -1)"
  fi
  if [ -z "$UDID" ] && [ "$DRY_RUN" -eq 1 ]; then UDID="<booted-simulator>"; fi
  if [ -z "$UDID" ]; then
    echo "No iOS simulator selected: pass --udid <id>, set IOS_UDID, or boot one first." >&2
    return 1
  fi
  say "iOS simulator $UDID"
  run xcrun simctl boot "$UDID" 2>/dev/null || true   # already booted is fine
  [ "$MODE" = "visible" ] && run open -a Simulator
  return 0
}

ensure_android_emulator() {
  local adb="$SDK_ROOT/platform-tools/adb"
  if [ "$DRY_RUN" -eq 0 ] && "$adb" devices 2>/dev/null | grep -q "emulator-.*device$"; then
    say "Android emulator already running"
    return 0
  fi
  local flags="-no-snapshot -no-audio"
  [ "$MODE" = "headless" ] && flags="$flags -no-window"
  say "Starting Android emulator $AVD ($MODE)"
  if [ "$DRY_RUN" -eq 1 ]; then echo "[dry-run] $SDK_ROOT/emulator/emulator -avd $AVD $flags &"; return 0; fi
  # shellcheck disable=SC2086
  nohup "$SDK_ROOT/emulator/emulator" -avd "$AVD" $flags >/tmp/rv_emulator.log 2>&1 &
  local i
  for i in $(seq 1 80); do
    [ "$("$adb" shell getprop sys.boot_completed 2>/dev/null | tr -d '\r')" = "1" ] && break
    sleep 5
  done
  if [ "$("$adb" shell getprop sys.boot_completed 2>/dev/null | tr -d '\r')" != "1" ]; then
    echo "Emulator did not finish booting (see /tmp/rv_emulator.log; a stale ~/.android/avd/$AVD.avd/*.lock can block it)." >&2
    return 1
  fi
  "$adb" shell svc power stayon true >/dev/null 2>&1   # keeps the screen from sleeping mid-run
  return 0
}

# ---- pytest ----------------------------------------------------------------------------------

# pytest <label> <args...>: runs from RandezVousUITests and records failures for the exit code.
FAILED=()
pytest_run() {
  local label="$1"; shift
  local args=("$@")
  [ "$LIST_ONLY" -eq 1 ] && args+=(--collect-only -qq)  # pytest.ini adds -v, so -qq nets out to one test id per line
  say "$label: pytest ${args[*]} ${EXTRA[*]:-}"
  [ "$DRY_RUN" -eq 1 ] && return 0
  ( cd "$TESTS_DIR" && pytest "${args[@]}" ${EXTRA[@]+"${EXTRA[@]}"} )
  local rc=$?
  [ "$rc" -eq 0 ] || [ "$rc" -eq 5 ] || FAILED+=("$label")  # 5 = no tests in that category on this platform
}

# has_tests <pytest args>: true if the selection matches anything, so no device starts for an empty category.
has_tests() { ( cd "$TESTS_DIR" && pytest "$@" --browser chrome --collect-only -qq 2>/dev/null | grep -q "::" ); }

# Each runner takes an optional marker (smoke, ux, access, push); without one it runs the whole platform.
run_web() {
  local args=(Tests/web --ignore=Tests/web/android --browser chrome)
  [ -n "${1:-}" ] && args+=(-m "$1")
  [ "$MODE" = "headless" ] && args+=(--headless)
  pytest_run "web${1:+ ($1)}" "${args[@]}"
}

run_ios() {
  if [ -n "${1:-}" ] && ! has_tests Tests/ios -m "$1"; then say "ios ($1): no tests"; return; fi
  [ "$LIST_ONLY" -eq 1 ] || ensure_ios_simulator || { FAILED+=("ios (no simulator)"); return; }
  local args=(Tests/ios)
  [ -n "${1:-}" ] && args+=(-m "$1")
  [ -n "$UDID" ] && args+=(--udid "$UDID")
  [ "$MODE" = "headless" ] && args+=(--headless)
  pytest_run "ios${1:+ ($1)}" "${args[@]}"
}

run_android() {
  if [ -n "${1:-}" ] && ! has_tests Tests/web/android -m "$1"; then say "android ($1): no tests"; return; fi
  [ "$LIST_ONLY" -eq 1 ] || ensure_android_emulator || { FAILED+=("android (no emulator)"); return; }
  local args=(Tests/web/android)
  [ -n "${1:-}" ] && args+=(-m "$1")
  [ "$MODE" = "headless" ] && args+=(--headless)
  pytest_run "android${1:+ ($1)}" "${args[@]}"
}

# run_marker <marker>: that category on every platform (or just --platform).
run_marker() {
  [ -z "$PLATFORM" ] || [ "$PLATFORM" = "web" ]     && run_web "$1"
  [ -z "$PLATFORM" ] || [ "$PLATFORM" = "ios" ]     && run_ios "$1"
  [ -z "$PLATFORM" ] || [ "$PLATFORM" = "android" ] && run_android "$1"
  return 0
}

# ---- main ------------------------------------------------------------------------------------

if [ -f "$ROOT/.venv/bin/activate" ]; then
  # shellcheck disable=SC1091
  source "$ROOT/.venv/bin/activate"
else
  echo "No .venv found: run ./setup.sh first." >&2
  exit 1
fi

say "category=$CATEGORY mode=$MODE$([ "$DRY_RUN" -eq 1 ] && echo " (dry run)")"
case "$CATEGORY" in
  all)     run_web; run_ios; run_android ;;
  smoke|ux|access|push) run_marker "$CATEGORY" ;;
  web)     run_web ;;
  ios)     run_ios ;;
  android) run_android ;;
esac

if [ ${#FAILED[@]} -gt 0 ]; then
  echo
  say "FAILED: ${FAILED[*]}"
  exit 1
fi
say "done"
