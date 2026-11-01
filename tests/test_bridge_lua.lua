-- Запускается в REAPER; проверяет мост на заглушках, проект не меняет.
local _, script = reaper.get_action_context()
local root = script:match('^(.*)[/\\]tests[/\\]')
local report = root .. '/tests/bridge_lua_result.txt'
local function run()
    local json = dofile(root .. '/lua/mcp_json.lua')
    local data = json.decode([==[{"args":["Бас, L [1]", "C:\\Music\\bass.mid", "\u0411\u0430\u0441", 1e-5]}]==])
    assert(#data.args == 4 and data.args[1] == 'Бас, L [1]', 'Запятые и скобки в имени')
    assert(data.args[2] == [[C:\Music\bass.mid]], 'Путь Windows')
    assert(data.args[3] == 'Бас' and data.args[4] == 0.00001, 'Unicode и число')
    local state = {}
    local mock = setmetatable({
        GetResourcePath = function() return '/unused' end,
        RecursiveCreateDirectory = function() end,
        ShowConsoleMsg = function() end,
        EnumerateFiles = function() return nil end,
        defer = function() end,
        genGuid = function() return 'test' end,
        SetExtState = function(_, key, value) state[key] = value end,
        GetExtState = function(_, key) return state[key] end,
        GetCursorPosition = function() return 0 end,
        TimeMap_GetTimeSigAtTime = function() return 7, 8, 120 end,
        TimeMap2_timeToQN = function(_, position) return position * 2 end,
        TimeMap2_QNToTime = function(_, qn) return qn / 2 end,
    }, {__index = reaper})
    local env = setmetatable({reaper = mock}, {__index = _G})
    assert(loadfile(root .. '/lua/mcp_bridge.lua', 't', env))()
    local signature = env.DSL_FUNCTIONS.GetTimeSignature()
    assert(signature.numerator == 7 and signature.denominator == 8, 'Размер 7/8')
    assert(env.DSL_FUNCTIONS.GetTempo().ret == 120, 'Темп')
    assert(env.DSL_FUNCTIONS.BarsToTime(2, 0).ret == 3.5, 'Два такта 7/8 при 120 BPM')
    mock.TimeMap_GetTimeSigAtTime = function() return 3, 4, 120 end
    assert(env.DSL_FUNCTIONS.BarsToTime(2, 0).ret == 3, 'Два такта 3/4 при 120 BPM')
end
local ok, err = pcall(run)
local f = assert(io.open(report, 'w'))
f:write(ok and 'PASS: JSON, Unicode, Windows paths, tempo, 7/8, 3/4, BarsToTime\n' or 'FAIL: ' .. tostring(err))
f:close()
