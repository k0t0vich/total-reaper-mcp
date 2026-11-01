"""Регрессии файлового транспорта без открытого REAPER."""
import asyncio
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import AsyncMock
from server.bridge import ReaperFileBridge
from server.dsl.wrappers import context_get_tempo_info


class BridgeReliability(unittest.IsolatedAsyncioTestCase):
    async def test_clients_do_not_mix_responses_above_1000(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            clients = [ReaperFileBridge(), ReaperFileBridge()]
            for client in clients:
                client.bridge_dir = root
                client.request_id = 1000
            seen = set()
            async def worker():
                while len(seen) < 2:
                    for path in root.glob('request_*.json'):
                        if path.name in seen:
                            continue
                        data = json.loads(path.read_text())
                        seen.add(path.name)
                        response = root / path.name.replace('request_', 'response_')
                        response.write_text(json.dumps({'ok': True, 'ret': data['args'][0]}))
                    await asyncio.sleep(0.001)
            task = asyncio.create_task(worker())
            results = await asyncio.gather(*(client.call_lua('Echo', [i]) for i, client in enumerate(clients)))
            await asyncio.wait_for(task, 1)
            self.assertEqual([r['ret'] for r in results], [0, 1])
            self.assertEqual(len(seen), 2)
            self.assertEqual(list(root.iterdir()), [])

    async def test_cancellation_cleans_pending_request(self):
        with tempfile.TemporaryDirectory() as directory:
            client = ReaperFileBridge()
            client.bridge_dir = Path(directory)
            task = asyncio.create_task(client.call_lua('GetTempo'))
            await asyncio.sleep(0.02)
            task.cancel()
            with self.assertRaises(asyncio.CancelledError):
                await task
            self.assertEqual(list(Path(directory).iterdir()), [])

    async def test_missing_bridge_is_not_reported_as_120_bpm(self):
        bridge = AsyncMock()
        bridge.call_lua.return_value = {'ok': False, 'error': 'Disconnected'}
        result = await context_get_tempo_info(bridge)
        self.assertFalse(result.success)
        self.assertEqual(result.error, 'Disconnected')

    async def test_non_four_four_meter(self):
        bridge = AsyncMock()
        bridge.call_lua.side_effect = [{'ok': True, 'ret': 93.5}, {'ok': True, 'numerator': 7, 'denominator': 8}]
        result = await context_get_tempo_info(bridge)
        self.assertTrue(result.success)
        self.assertEqual(result.changes['time_signature'], '7/8')
        self.assertEqual(result.changes['tempo'], 93.5)
