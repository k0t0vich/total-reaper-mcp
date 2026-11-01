#!/usr/bin/env bash
# Установка моста и JSON-парсера для REAPER на macOS.
set -euo pipefail
script_dir="$(cd "$(dirname "$0")" && pwd)"
source_dir="$script_dir/../lua"
target_dir="$HOME/Library/Application Support/REAPER/Scripts"
mkdir -p "$target_dir"
for file in mcp_bridge.lua mcp_json.lua; do
  target="$file"
  if [ "$file" = mcp_bridge.lua ]; then target=mcp_bridge_codex.lua; fi
  if [ -f "$target_dir/$target" ]; then cp "$target_dir/$target" "$target_dir/$target.backup"; fi
  cp "$source_dir/$file" "$target_dir/$target"
done
printf '%s\n' "Установлено в $target_dir. Запустите mcp_bridge_codex.lua в REAPER."
