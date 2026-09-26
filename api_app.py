"""
WSGI-compatible Flask App，供 Vercel Serverless 使用
同时支持本地开发测试（轮询模式）
"""

import os
import sys
import logging
import asyncio
from functools import wraps

from flask import Flask, request, abort
from telegram import Update
from telegram.ext import (
    Application,
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

from search import search_books, build_reply

# =======================
# 配置
# =======================
BOT_TOKEN = os.environ.get("BOT_TOKEN", "").strip()
ALLOWED_USERS = set(
    u.strip() for u in os.environ.get("ALLOWED_USERS", "").split(",") if u.strip()
)

# 你的 Telegram user ID（源哥的 chat id），留空则不限制
MY_USER_ID = os.environ.get("MY_USER_ID", "1894029098").strip()
ALLOWED_USERS.add(MY_USER_ID)  # 始终允许自己

logging.basicConfig(
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger("zlib-bot")

# =======================
# Flask App
# =======================
flask_app = Flask(__name__)

# 全局 bot application（Vercel 冷启动时初始化一次）
bot_app: Application = None


def get_bot() -> Application:
    """获取或创建 bot application"""
    global bot_app
    if bot_app is None:
        bot_app = ApplicationBuilder().token(BOT_TOKEN).build()
        _register_handlers(bot_app)
    return bot_app


def _register_handlers(app: Application):
    """注册命令和消息处理器"""
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("help", cmd_help))
    app.add_handler(CommandHandler("search", cmd_search))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_error_handler(error_handler)


# =======================
# Telegram Handlers
# =======================
async def cmd_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📚 *欢迎使用书籍搜索 Bot！*\n\n"
        "发送书名或关键词，我会帮你搜索 Open Library 上的书籍。\n\n"
        "*命令：*\n"
        "/search <书名> — 搜索书籍\n"
        "/help — 帮助",
        parse_mode="Markdown",
    )


async def cmd_help(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "*使用说明*\n\n"
        "直接发送书名或关键词即可搜索。\n"
        "也可以使用 /search <书名> 命令。\n\n"
        "数据来源：Open Library",
        parse_mode="Markdown",
    )


async def cmd_search(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = " ".join(ctx.args).strip()
    if not query:
        await update.message.reply_text("请提供搜索关键词，如：/search python 编程")
        return
    await do_search(update, query)


async def handle_message(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.message.text.strip()
    if query and not query.startswith("/"):
        await do_search(update, query)


async def do_search(update: Update, query: str):
    """执行搜索并回复"""
    await update.message.reply_text(f"🔍 正在搜索「{query}」...")
    try:
        results = search_books(query, limit=5)
        reply = build_reply(results, query)
        await update.message.reply_text(reply, parse_mode="Markdown")
    except Exception as e:
        logger.error(f"搜索出错: {e}")
        await update.message.reply_text(f"❌ 搜索失败：{str(e)}")


async def error_handler(update: object, ctx: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Bot 错误: {ctx.error}")


# =======================
# Webhook 路由
# =======================
async def _process_update(data: dict):
    bot_app = get_bot()
    async with bot_app:
        update = Update.de_json(data, bot_app.bot)

        # 用户白名单检查
        if ALLOWED_USERS:
            uid = str(update.effective_user.id) if update.effective_user else ""
            if uid not in ALLOWED_USERS:
                logger.warning(f"未授权用户 {uid}")
                return

        await bot_app.process_update(update)


@flask_app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    """Telegram webhook 回调"""
    if not BOT_TOKEN:
        abort(500, "BOT_TOKEN not configured")

    data = request.get_json(force=True)
    asyncio.run(_process_update(data))
    return "", 200


@flask_app.route("/", methods=["GET"])
def index():
    return "📚 Z-Library Bot is running! v1.0"


# =======================
# 本地开发测试
# =======================
def run_local():
    """本地运行（轮询模式）"""
    logging.basicConfig(level=logging.INFO)

    print(f"BOT_TOKEN: {'*' * len(BOT_TOKEN) if BOT_TOKEN else 'NOT SET'}")
    print(f"ALLOWED_USERS: {ALLOWED_USERS}")

    application = ApplicationBuilder().token(BOT_TOKEN).build()
    _register_handlers(application)

    logger.info("Bot 本地模式启动（轮询）...")
    application.run_polling()


if __name__ == "__main__":
    run_local()
