"""
Open Library 搜索模块
API 文档：https://openlibrary.org/dev/docs/api/books
"""

import requests
from typing import Optional

UA = "ZlibBot/1.0 (Telegram Bot; contact@example.com)"
HEADERS = {"User-Agent": UA}
OL_URL = "https://openlibrary.org/search.json"


def format_size(bytes_size: str) -> str:
    """将字节大小转换为人类可读格式"""
    try:
        size = int(bytes_size)
        for unit in ["B", "KB", "MB", "GB"]:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"
    except (ValueError, TypeError):
        return bytes_size


def search_books(query: str, limit: int = 5) -> list[dict]:
    """
    搜索 Open Library，返回结构化书籍列表
    """
    params = {
        "q": query,
        "limit": limit,
        "fields": "key,title,author_name,isbn,first_publish_year,"
                  "publisher,number_of_pages_median,cover_i,subject,"
                  "language,editions_count",
    }

    try:
        resp = requests.get(OL_URL, params=params, headers=HEADERS, timeout=10)
        resp.raise_for_status()
        data = resp.json()
    except requests.RequestException as e:
        raise RuntimeError(f"搜索失败: {e}")

    docs = data.get("docs", [])
    results = []

    for doc in docs:
        # 提取 ISBN
        isbns = doc.get("isbn", [])
        isbn = isbns[0] if isbns else ""

        # 封面
        cover_id = doc.get("cover_i")
        cover_url = (
            f"https://covers.openlibrary.org/b/id/{cover_id}-M.jpg"
            if cover_id else None
        )

        # 作者
        authors = doc.get("author_name", [])
        author_str = "; ".join(authors[:3]) if authors else "未知作者"

        # 出版社
        publishers = doc.get("publisher", [])
        publisher = publishers[0] if publishers else "未知出版社"

        # 页数
        pages = doc.get("number_of_pages_median")

        # 主题/分类
        subjects = doc.get("subject", [])
        subject_str = "; ".join(subjects[:3]) if subjects else ""

        # 语言
        languages = doc.get("language", [])
        lang_str = languages[0] if languages else ""

        results.append({
            "title": doc.get("title", "无标题"),
            "author": author_str,
            "year": doc.get("first_publish_year", ""),
            "isbn": isbn,
            "publisher": publisher,
            "pages": pages,
            "cover": cover_url,
            "subject": subject_str,
            "language": lang_str,
            "ol_key": doc.get("key", ""),
            "editions": doc.get("editions_count", 0),
        })

    return results


def build_reply(books: list[dict], query: str) -> str:
    """将搜索结果格式化为 Telegram 消息"""
    if not books:
        return f"🔍 没有找到与「{query}」相关的书籍。\n\n试试换个关键词？"

    lines = [f"🔍 为你找到 *{len(books)}* 本相关书籍：\n"]

    for i, book in enumerate(books, 1):
        title = book["title"]
        author = book["author"]
        year = book["year"]
        pages = book["pages"]
        isbn = book["isbn"]
        publisher = book["publisher"]

        # 构造 Open Library 详情页
        ol_key = book["ol_key"]
        ol_url = f"https://openlibrary.org{ol_key}" if ol_key else ""

        lines.append(f"*{i}. {title}*")
        lines.append(f"   👤 {author}")
        if year:
            lines.append(f"   📅 {year}")
        if pages:
            lines.append(f"   📖 {pages} 页")
        if publisher and publisher != "未知出版社":
            lines.append(f"   🏢 {publisher}")
        if isbn:
            lines.append(f"   🔢 ISBN: {isbn}")
        if ol_url:
            lines.append(f"   🔗 {ol_url}")
        lines.append("")

    lines.append("—— 数据来源：Open Library")
    return "\n".join(lines)
