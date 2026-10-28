#!/usr/bin/env python3
"""
Vercel Serverless Function Entrypoint for Tigrinya Studio
Exposes `handler` (inheriting from BaseHTTPRequestHandler via StudioRequestHandler)
for `/api/check`, `/api/fix`, `/api/ai-check`, `/api/health`, and `/`.
"""

import os
import sys

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SCRIPTS_DIR = os.path.join(ROOT_DIR, "scripts")

if SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, SCRIPTS_DIR)

from studio import StudioRequestHandler  # noqa: E402


class handler(StudioRequestHandler):
    """Vercel Python Runtime HTTP Request Handler."""
    pass
