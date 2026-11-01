"""Чтение состояния REAPER без изменения проекта."""
import json
from ..bridge import bridge


def register_diagnostics_tools(mcp):
    async def read(function):
        result = await bridge.call_lua(function, [])
        if not result.get("ok"):
            raise RuntimeError(result.get("error", "REAPER не ответил"))
        return json.dumps(result, ensure_ascii=False)

    @mcp.tool()
    async def reaper_health() -> str:
        """Версия REAPER, версия моста и доступные API расширений. Только чтение."""
        return await read("GetBridgeHealth")

    @mcp.tool()
    async def reaper_project_snapshot() -> str:
        """Активный проект, GUID дорожек, FX, темп, размер, транспорт. Только чтение.

        Индексы дорожек и FX начинаются с 0. Повторить перед правкой и после неё;
        при смене project_id нельзя применять ранее вычисленные индексы.
        """
        return await read("GetProjectSnapshot")

    return 2
