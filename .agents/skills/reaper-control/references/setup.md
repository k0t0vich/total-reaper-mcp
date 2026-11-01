# MCP REAPER на этой машине

| Что | Путь / значение |
|---|---|
| Репозиторий | `~/reaper-mcp/total-reaper-mcp` |
| Python | `<репозиторий>/.venv/bin/python` |
| Запуск | `python -m server.app --profile codex-production`, `cwd` = репозиторий |
| Настройка Codex | `~/.codex/config.toml`, секция `[mcp_servers.reaper]` |
| Lua-мост | `<REAPER resource path>/Scripts/mcp_bridge_codex.lua` |
| Файлы обмена v2 | `<REAPER resource path>/Scripts/mcp_bridge_data_v2/` |
| Установка моста на Mac | из репозитория `bash scripts/install_bridge.sh` |
| Запуск моста на Mac | `/Applications/REAPER.app/Contents/MacOS/REAPER -nonewinst "<путь к Lua-мосту>"` |

Новый мост не читает старую папку `mcp_bridge_data`: в ней могут оставаться
просроченные команды. Не копировать их в v2. Для перезагрузки использовать отдельный Lua-загрузчик с `dofile` моста.
Повторный вызов того же запущенного ReaScript может его остановить.
Новый экземпляр моста завершает прежний цикл через маркер экземпляра.

После изменения Python/профиля переподключить MCP или перезапустить Codex.
После замены Lua перезапустить только мост. Проект REAPER перезапускать не нужно.
На Windows выставить `REAPER_MCP_BRIDGE_DIR` в MCP env на абсолютный
`%APPDATA%\REAPER\Scripts\mcp_bridge_data_v2` с уже раскрытым `%APPDATA%`;
Python и `cwd` указать от Windows-клона. Сам Lua использует `GetResourcePath()`.

Проверки без изменения проекта:

```bash
python -m unittest discover -s tests -p test_bridge_reliability.py -v
```

`tests/test_bridge_lua.lua` запускается в REAPER, проверяет функции на заглушках
и пишет `tests/bridge_lua_result.txt`. Живая проверка — `reaper_health` и
`reaper_project_snapshot`; до/после должны совпасть ID, dirty и state counter.

Исходник skill — `.agents/skills/reaper-control` в форке MCP; пользовательская
копия — `~/.agents/skills/reaper-control`. После обновления синхронизировать их.

При ручной установке рядом с `mcp_bridge_codex.lua` обязателен `mcp_json.lua`
из `lua/` репозитория (MIT, rxi/json.lua). Скрипт установки копирует оба файла.

Расширения на этой машине установлены и проверены 01.11.2026:
SWS 2.14.0.7, ReaPack 1.2.6, js_ReaScriptAPI 1.310 — ARM64.
Библиотеки находятся в `UserPlugins` REAPER; после установки нужен перезапуск.
Проверять загрузку через `reaper_health`, а не по одному наличию файлов.
