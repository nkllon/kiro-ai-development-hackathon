#!/usr/bin/env bash
#
# Orchestrate the baseline test validation workflow by delegating work to
# separate Codex agents. The script launches the inventory agents in parallel,
# waits for them to finish, then runs the baseline validation and documentation
# steps serially.
#
# Usage:
#   ./scripts/run_baseline_agents.sh
#
# Requirements:
#   - Codex CLI available on PATH (`codex`)
#   - Executed from anywhere (script resolves repo root automatically)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
LOG_DIR="$REPO_ROOT/logs/baseline_agents"

if ! command -v codex >/dev/null 2>&1; then
  echo "Error: codex CLI not found in PATH. Install or add to PATH before running." >&2
  exit 1
fi

mkdir -p "$LOG_DIR"

log() {
  printf '[%s] %s\n' "$(date '+%Y-%m-%d %H:%M:%S')" "$*"
}

launch_bg_agent() {
  local name="$1"
  local prompt="$2"
  local log_file="$LOG_DIR/${name}.log"

  log "Launching ${name} (background)…"
  codex -C "$REPO_ROOT" "$prompt" >"$log_file" 2>&1 &
  BG_PIDS+=("$!")
  BG_NAMES+=("$name")
  BG_LOGS+=("$log_file")
}

run_agent() {
  local name="$1"
  local prompt="$2"
  local log_file="$LOG_DIR/${name}.log"

  log "Running ${name}…"
  if codex -C "$REPO_ROOT" "$prompt" | tee "$log_file"; then
    log "${name} completed successfully."
  else
    log "${name} failed. See log: $log_file"
    exit 1
  fi
}

wait_for_bg_agents() {
  local failure=0
  for idx in "${!BG_PIDS[@]}"; do
    local pid="${BG_PIDS[$idx]}"
    local name="${BG_NAMES[$idx]}"
    local log_file="${BG_LOGS[$idx]}"

    if wait "$pid"; then
      log "${name} completed successfully."
    else
      log "${name} failed. See log: $log_file"
      failure=1
    fi
  done
  BG_PIDS=()
  BG_NAMES=()
  BG_LOGS=()

  if [[ $failure -ne 0 ]]; then
    exit 1
  fi
}

declare -a BG_PIDS=()
declare -a BG_NAMES=()
declare -a BG_LOGS=()

read -r -d '' PROMPT_AGENT_A <<'EOF'
Inventory all automated test entrypoints in this repository. Focus on:
- Makefile targets related to testing or validation
- pytest configuration (pytest.ini, pyproject options)
- test-related scripts under scripts/
Produce a structured summary (target name → command → description). Do not edit files.
EOF

read -r -d '' PROMPT_AGENT_B <<'EOF'
Review documentation/specs that describe testing expectations (e.g. docs/ folders, ADRs).
Cross-check required test coverage against the current test entrypoints.
Report gaps where required tests are missing. No file edits.
EOF

read -r -d '' PROMPT_AGENT_C <<'EOF'
Using the consolidated command list from Agents A and B, execute the agreed baseline
test commands from the repository root. Capture exit codes and summarize the outcomes.
Stop and report immediately if any command fails. Do not modify files.
EOF

read -r -d '' PROMPT_AGENT_D <<'EOF'
Document the Last Known Good baseline using Agent C’s results. Create or update
docs/testing/last_known_good.md with:
- Commands executed
- Expected outcomes / pass criteria
- Locations of generated artifacts
Minimize edits elsewhere; ensure Markdown is concise and actionable.
EOF

read -r -d '' PROMPT_AGENT_E <<'EOF'
Update contributor-facing docs (e.g. AGENTS.md) so developers know how to rerun the
Last Known Good baseline. Reference docs/testing/last_known_good.md and list required
commands. Keep edits succinct.
EOF

# Phase 1: run inventory agents A and B in parallel
launch_bg_agent "agent_A_inventory" "$PROMPT_AGENT_A"
launch_bg_agent "agent_B_docs_gap" "$PROMPT_AGENT_B"

wait_for_bg_agents

# Phase 2: baseline validation (serial)
run_agent "agent_C_baseline_run" "$PROMPT_AGENT_C"

# Phase 3: documentation updates (serial, can be adjusted)
run_agent "agent_D_document_baseline" "$PROMPT_AGENT_D"
run_agent "agent_E_update_guides" "$PROMPT_AGENT_E"

log "Workflow complete. Logs are available under $LOG_DIR"
