"""
Vercel Serverless Function — WSGI 入口
"""

import os
import sys

# 加入项目根目录到 path
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from api_app import flask_app, init_bot, BOT_TOKEN, get_bot, ALLOWED_USERS

# 冷启动初始化
if not os.environ.get("_VERCEL_WARMED"):
    os.environ["_VERCEL_WARMED"] = "1"
    # 初始化 bot（在 Vercel 冷启动时做一次）
    if BOT_TOKEN:
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(get_bot().initialize())

# Vercel's Python runtime auto-detects a top-level WSGI app named `app`
app = flask_app
