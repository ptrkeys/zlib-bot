#!/bin/bash
# setup_webhook.sh — 配置 Telegram Webhook

# ============================================================
# 使用前先填好下面的值
# ============================================================
BOT_TOKEN="YOUR_BOT_TOKEN"
VERCEL_URL="https://zlib-bot-delta.vercel.app"   # 部署后 Vercel 给你的地址

# ============================================================
# 执行
# ============================================================
FULL_URL="${VERCEL_URL}/${BOT_TOKEN}"

echo "设置 Webhook..."
echo "URL: $FULL_URL"

curl -s -F "url=${FULL_URL}" \
     "https://api.telegram.org/bot${BOT_TOKEN}/setWebhook"

echo ""
echo "验证 Webhook..."
curl -s "https://api.telegram.org/bot${BOT_TOKEN}/getWebhookInfo" | python3 -m json.tool
