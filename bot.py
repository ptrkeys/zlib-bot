"""
Z-Library Bot — Telegram Bot for Book Search
使用 Open Library 作为主要数据源（免费、无需登录）

部署方式：Vercel（免费）
"""

import os
import re
import logging
from functools import wraps

from flask import Flask, request, abort
import requests

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
    ConversationHandler,
)

from search import search_books, build_reply

# =======================
# 配置
# =======================
BOT_TOKEN = os.environ.get("BOT_TOKEN", "").strip()
ALLOWED_USERS = set(u.strip() for u in os.environ.get("ALLOWED_USERS", "").split(",") if u.strip())
PORT = int(os.environ.get("PORT", 8080))

# Vercel 无持久化存储，简单用内存 dict
user_sessions: dict = {}

# =======================
# Flask App
# =======================
app = Flask(__name__)

# =======================
# 日志
# =======================
logging.basicConfig(
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


# =======================
# 工具函数
# =======================
def restricted(func):
    """只允许白名单用户使用 bot"""
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        user_id = str(update.effective_user.id) if update.effective_user else ""
        if ALLOWED_USERS and user_id not in ALLOWED_USERS:
            logger.warning(f"未授权用户 {user_id} 尝试使用 bot")
            return
        return await func(update, context, *args, **kwargs)
    return wrapper


async def cmd_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """处理 /start 命令"""
    await update.message.reply_text(
        "📚 *欢迎使用书籍搜索 Bot！*\n\n"
        "发送书名或关键词，我会帮你搜索书籍。\n\n"
        "*支持的命令：*\n"
        "/search <书名> — 搜索书籍\n"
        "/help — 显示帮助",
        parse_mode="Markdown",
    )


async def cmd_help(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """处理 /help 命令"""
    await update.message.reply_text(
        "*使用说明*\n\n"
        "直接发送书名或关键词即可搜索。\n"
        "也可以使用 /search <书名> 命令。\n\n"
        "数据来源：Open Library（免费开放的书籍数据库）",
        parse_mode="Markdown",
    )


async def cmd_search(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """处理 /search 命令"""
    query = " ".join(ctx.args).strip()
    if not query:
        await update.message.reply_text("请提供搜索关键词，如：/search python 编程")
        return

    await update.message.reply_text(f"🔍 正在搜索「{query}」...")

    try:
        results = search_books(query, limit=5)
        reply = build_reply(results, query)
        await update.message.reply_text(reply, parse_mode="Markdown")
    except Exception as e:
        logger.error(f"搜索出错: {e}")
        await update.message.reply_text(f"❌ 搜索失败：{e}")


async def handle_message(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """处理普通文本消息（直接发送书名）"""
    query = update.message.text.strip()
    if not query:
        return

    # 忽略命令
    if query.startswith("/"):
        return

    await update.message.reply_text(f"🔍 正在搜索「{query}」...")

    try:
        results = search_books(query, limit=5)
        reply = build_reply(results, query)
        await update.message.reply_text(reply, parse_mode="Markdown")
    except Exception as e:
        logger.error(f"搜索出错: {e}")
        await update.message.reply_text(f"❌ 搜索失败：{e}")


async def error_handler(update: object, ctx: ContextTypes.DEFAULT_TYPE):
    """错误处理"""
    logger.error(f"Bot 错误: {ctx.error}")


# =======================
# Vercel Webhook Handler
# =======================
@app.route(f"/{BOT_TOKEN}", methods=["POST"])
async def webhook():
    """处理 Telegram 发来的 webhook 更新"""
    if not BOT_TOKEN:
        abort(500, "BOT_TOKEN not configured")

    if request.method == "POST":
        # 解析 JSON
        data = request.get_json(force=True)
        update = Update.de_json(data, app.bot)

        # 简单白名单过滤
        if ALLOWED_USERS:
            user_id = str(update.effective_user.id) if update.effective_user else ""
            if user_id not in ALLOWED_USERS:
                return "", 200

        # 分发处理
        await app.dispatcher.process_update(update)
        return "", 200


@app.route("/", methods=["GET"])
def index():
    return "📚 Z-Library Bot is running!"


# =======================
# 本地测试模式（可选）
# =======================
def run_local():
    """本地运行（轮询模式），用于测试"""
    from telegram.ext import ApplicationBuilder
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", cmd_start))
    application.add_handler(CommandHandler("help", cmd_help))
    application.add_handler(CommandHandler("search", cmd_search))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_error_handler(error_handler)

    logger.info("Bot 本地模式启动（轮询）...")
    application.run_polling()


# =======================
# Vercel WSGI Entry
# =======================
def handler(event, context):
    """Vercel serverless handler"""
    return app(event, context)


if __name__ == "__main__":
    run_local()
