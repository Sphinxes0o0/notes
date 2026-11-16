#!/bin/bash
# Sync key files to Hermes skill references

SKILL_REF="$HOME/.hermes/skills/productivity/llm-wiki/references"
WIKI="$HOME/llm-wiki"

cp "$WIKI/AGENT.md" "$SKILL_REF/AGENT.md"
cp "$WIKI/index.md" "$SKILL_REF/index.md"
cp "$WIKI/log.md" "$SKILL_REF/log.md"

echo "Synced llm-wiki → skill references"
