#!/usr/bin/env bash
# Refresh the read-only mirror of the context layer and the voice skill that drafting tasks read.
# Usage: bash sync-mirror.sh <context-layer clone> <voice skill clone> <mirror dir>
# Both clones should be on origin/main. Copies authored context and skill rules only (no corpus, no copied material).
set -euo pipefail
CL="${1:?context layer clone}"; SK="${2:?voice skill clone}"; LIVE="${3:?mirror dir}"
TMP="$(mktemp -d)"
mkdir -p "$TMP/context-layer/context" "$TMP/context-layer/loop" "$TMP/skill/references" "$TMP/skill/agents" "$TMP/skill/scripts"
cp "$CL"/AGENTS.md "$CL"/CLAUDE.md "$CL"/QUESTIONS.md "$TMP/context-layer/"
[ -f "$CL"/loop/log.md ] && cp "$CL"/loop/log.md "$TMP/context-layer/loop/"
cp "$CL"/context/*.md "$TMP/context-layer/context/"
cp "$SK"/SKILL.md "$TMP/skill/"
cp "$SK"/references/*.md "$TMP/skill/references/"
cp "$SK"/agents/*.md "$TMP/skill/agents/" 2>/dev/null || true
cp "$SK"/scripts/* "$TMP/skill/scripts/" 2>/dev/null || true
{
  echo "context-layer main: $(git -C "$CL" rev-parse --short HEAD) $(git -C "$CL" log -1 --format=%cs)"
  echo "skill main: $(git -C "$SK" rev-parse --short HEAD) $(git -C "$SK" log -1 --format=%cs)"
  echo "mirrored: $(date '+%Y-%m-%d %H:%M %Z')"
} > "$TMP/VERSION"
mkdir -p "$LIVE"
rm -rf "$LIVE/context-layer" "$LIVE/skill"
cp -r "$TMP/context-layer" "$TMP/skill" "$TMP/VERSION" "$LIVE/"
rm -rf "$TMP"
cat "$LIVE/VERSION"
