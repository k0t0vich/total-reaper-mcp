# Работа над REAPER MCP

Писать по-русски. Перед работой с живым REAPER читать skill
`.agents/skills/reaper-control/SKILL.md`.

- Сначала read-only snapshot. Интеграционные тесты upstream могут менять
  активный проект: запускать их только на выделенном тестовом проекте.
- Правки транспорта проверять `python -m unittest discover -s tests -p test_bridge_reliability.py -v`.
- Lua проверять через `tests/test_bridge_lua.lua`, затем read-only MCP-вызовы.
- Не добавлять локальные `.venv*`, `.mcp.json`, настройки и музыкальные проекты
  в коммиты. В upstream часть окружения уже отслеживается; чужие изменения не включать.
- API сверять с официальной справкой и версией REAPER, multiple-return Lua
  сериализовать явно. Наличие имени API не гарантирует работоспособность обёртки.
