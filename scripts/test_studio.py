#!/usr/bin/env python3
"""
Integration test for Tigrinya Web Studio Server.
Tests GET /, GET /api/health, POST /api/check, POST /api/fix.
"""

import sys
import os
import time
import json
import urllib.request
import threading

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from studio import run_server

def main():
    port = 8799
    t = threading.Thread(target=run_server, kwargs={'port': port, 'open_browser': False}, daemon=True)
    t.start()
    time.sleep(1.2)

    # 1. Health check
    req = urllib.request.Request(f'http://127.0.0.1:{port}/api/health')
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode('utf-8'))
        assert data['status'] == 'ok', f'Health check failed: {data}'
    print('[PASS] GET /api/health: OK')

    # 2. Web UI HTML page
    req = urllib.request.Request(f'http://127.0.0.1:{port}/')
    with urllib.request.urlopen(req) as resp:
        html = resp.read().decode('utf-8')
        assert 'Tigrinya Studio' in html, 'UI HTML missing title'
        assert 'issue-highlight' in html, 'UI HTML missing highlight styles'
        assert 'Fix All Deterministic' in html, 'UI HTML missing fix button'
    print('[PASS] GET /: OK (HTML UI served)')

    # 3. POST /api/check
    text = "እቲ ምስጢር -- ኣብ ህይወት እዩ ።"
    payload = json.dumps({'text': text}).encode('utf-8')
    req = urllib.request.Request(f'http://127.0.0.1:{port}/api/check', data=payload, headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode('utf-8'))
        assert data['passed'] is False, 'Expected passed=False'
        assert len(data['issues']) >= 3, f'Expected issues, got {data["issues"]}'
        print(f"[PASS] POST /api/check: OK ({len(data['issues'])} issues, score: {data['score']})")

    # 4. POST /api/fix
    req = urllib.request.Request(f'http://127.0.0.1:{port}/api/fix', data=payload, headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode('utf-8'))
        assert data['fixed_text'] == 'እቲ ምሥጢር፦ ኣብ ሕይወት እዩ።', f'Unexpected fixed text: {data}'
        assert data['fixes_count'] >= 3, f'Expected multiple fixes, got {data["fixes_count"]}'
        print(f"[PASS] POST /api/fix: OK (fixed text: '{data['fixed_text']}', fixes: {data['fixes_count']})")

    print('\nALL STUDIO INTEGRATION TESTS PASSED!')
    return 0

if __name__ == '__main__':
    sys.exit(main())
