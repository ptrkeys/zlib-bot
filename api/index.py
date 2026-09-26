"""
Vercel Serverless Function — WSGI 入口
"""

import os
import sys

# 加入项目根目录到 path
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from api_app import flask_app

# Vercel's Python runtime auto-detects a top-level WSGI app named `app`.
# The bot Application is initialized/shut down per-request inside the
# webhook view instead of once at cold start, since each invocation may
# run on a different event loop.
app = flask_app
