# 📚 Z-Library Bot

Telegram 书籍搜索 Bot，使用 Open Library 作为数据源（免费、无需登录）。

## 功能

- 搜索书籍（书名、作者、关键词）
- 显示书籍详细信息（作者、出版年、页数、ISBN、出版社）
- 附 Open Library 链接
- 支持私聊和群组（@mention 触发）

## 部署到 Vercel（免费）

### 1. 准备 Telegram Bot

1. 在 Telegram 联系 [@BotFather](https://t.me/BotFather)
2. 发送 `/newbot`，创建一个新 bot，记下获得的 **Bot Token**
3. 获取你的 Telegram User ID（发送 `/start` 给 [@userinfobot](https://t.me/userinfobot)）

### 2. 上传到 GitHub

```bash
cd ~/zlib-bot
git init
git add .
git commit -m "init zlib-bot"
gh repo create zlib-bot --public --push  # 或手动上传
```

### 3. 部署到 Vercel

1. 访问 [vercel.com](https://vercel.com)，用 GitHub 登录
2. 点击 "New Project"，导入你的 zlib-bot 仓库
3. 在项目设置中添加环境变量：

   | 环境变量 | 值 |
   |---------|-----|
   | `BOT_TOKEN` | 你的 Telegram Bot Token |
   | `ALLOWED_USERS` | 你的 Telegram User ID（多人用逗号分隔）|
   | `MY_USER_ID` | 你的 Telegram User ID |

4. 点击 Deploy，Vercel 会自动安装依赖并部署

### 4. 配置 Webhook

部署完成后，需要告诉 Telegram 把更新推送到你的 Vercel 地址：

```bash
# 把 YOUR_BOT_TOKEN 和 YOUR_VERCEL_URL 换成实际的值
curl -F "url=https://your-vercel-url.vercel.app/YOUR_BOT_TOKEN" \
  https://api.telegram.org/botYOUR_BOT_TOKEN/setWebhook
```

### 5. 测试

在 Telegram 给你的 bot 发消息试试！

---

## 本地开发测试

```bash
cd ~/zlib-bot

# 复制环境变量文件
cp .env.example .env
# 编辑 .env，填入 BOT_TOKEN

# 运行（轮询模式，不需要公网地址）
python3 bot.py
```

## 项目结构

```
zlib-bot/
├── api/
│   └── index.py       # Vercel Serverless 入口
├── api_app.py          # Flask WSGI App + Bot Handlers
├── bot.py              # 本地运行入口（轮询）
├── search.py           # Open Library 搜索模块
├── requirements.txt    # Python 依赖
├── vercel.json         # Vercel 配置
└── README.md
```

## 数据来源

[Open Library](https://openlibrary.org/) — 免费、开放的书籍数据库，涵盖数千万本书。

> 注意：Open Library 不提供直接下载，只提供书籍元数据和 Open Library 上的公开版权书籍链接。需要下载完整书籍请自行寻找其他资源。
