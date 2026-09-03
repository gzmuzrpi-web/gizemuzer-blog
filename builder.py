#!/usr/bin/env python3
"""
builder.py - gizemuzer.com Static Site Generator
Zero external dependencies, fast, produces modern semantic HTML/CSS/JS.
"""

import os
import re
import shutil
import html
from datetime import datetime
from pathlib import Path

SITE_URL = "https://gizemuzer.xyz"
SITE_TITLE = "Gizem Uzer"
SITE_TAGLINE = "Düşünceler, yazılar ve dijital bahçe"
SITE_DESCRIPTION = "Gizem Uzer'in teknoloji, yapay zeka, sade yaşam ve yaratıcı üretim üzerine kişisel notları ve denemeleri."
AUTHOR_NAME = "Gizem Uzer"
AUTHOR_BIO = "Düşüncelerini, teknolojiye ve hayata dair gözlemlerini dijital bahçesinde paylaşan bir araştırmacı ve yazar."

BASE_DIR = Path(__file__).resolve().parent
CONTENT_DIR = BASE_DIR / "content"
BLOG_DIR = CONTENT_DIR / "blog"
PAGES_DIR = CONTENT_DIR / "pages"
STATIC_DIR = BASE_DIR / "static"
DIST_DIR = BASE_DIR / "dist"

MONTHS_TR = {
    1: "Ocak", 2: "Şubat", 3: "Mart", 4: "Nisan", 5: "Mayıs", 6: "Haziran",
    7: "Temmuz", 8: "Ağustos", 9: "Eylül", 10: "Ekim", 11: "Kasım", 12: "Aralık"
}

def format_date_tr(date_val):
    if isinstance(date_val, str):
        try:
            dt = datetime.strptime(date_val.strip(), "%Y-%m-%d")
        except ValueError:
            return date_val
    elif isinstance(date_val, datetime):
        dt = date_val
    else:
        return str(date_val)
    return f"{dt.day} {MONTHS_TR.get(dt.month, '')} {dt.year}"

def parse_frontmatter(content):
    metadata = {}
    body = content
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            raw_meta = parts[1]
            body = parts[2]
            for line in raw_meta.strip().splitlines():
                if ":" in line:
                    key, val = line.split(":", 1)
                    key = key.strip()
                    val = val.strip()
                    # Handle boolean
                    if val.lower() == "true":
                        metadata[key] = True
                    elif val.lower() == "false":
                        metadata[key] = False
                    # Handle list [a, b]
                    elif val.startswith("[") and val.endswith("]"):
                        items = [x.strip().strip("'\"") for x in val[1:-1].split(",") if x.strip()]
                        metadata[key] = items
                    else:
                        metadata[key] = val.strip("'\"")
    return metadata, body.strip()

def calculate_reading_time(text):
    words = len(re.findall(r'\w+', text))
    minutes = max(1, round(words / 180))
    return f"{minutes} dk okuma"

def markdown_to_html(md_text):
    """Clean and robust Markdown parser to HTML without third-party dependencies."""
    lines = md_text.splitlines()
    html_out = []
    in_code_block = False
    code_lang = ""
    code_lines = []
    in_list = False
    list_type = None # 'ul' or 'ol'
    in_blockquote = False
    quote_lines = []

    def flush_list():
        nonlocal in_list, list_type
        if in_list:
            html_out.append(f"</{list_type}>")
            in_list = False
            list_type = None

    def flush_quote():
        nonlocal in_blockquote, quote_lines
        if in_blockquote:
            quote_content = " ".join(quote_lines)
            html_out.append(f"<blockquote><p>{parse_inline(quote_content)}</p></blockquote>")
            in_blockquote = False
            quote_lines = []

    def parse_inline(text):
        # Images: ![alt](url)
        text = re.sub(r'!\[([^\]]*)\]\(([^)]+)\)', r'<img src="\2" alt="\1" loading="lazy" />', text)
        # Links: [text](url)
        text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', text)
        # Bold: **text** or __text__
        text = re.sub(r'(\*\*|__)(.*?)\1', r'<strong>\2</strong>', text)
        # Italic: *text* or _text_
        text = re.sub(r'(\*|_)(.*?)\1', r'<em>\2</em>', text)
        # Inline code: `code`
        text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)
        return text

    i = 0
    while i < len(lines):
        line = lines[i]

        # Code block fences
        if line.startswith("```"):
            if in_code_block:
                escaped_code = html.escape("\n".join(code_lines))
                lang_attr = f' class="language-{code_lang}"' if code_lang else ""
                html_out.append(f'<pre><code{lang_attr}>{escaped_code}</code></pre>')
                in_code_block = False
                code_lines = []
            else:
                flush_list()
                flush_quote()
                in_code_block = True
                code_lang = line[3:].strip()
                code_lines = []
            i += 1
            continue

        if in_code_block:
            code_lines.append(line)
            i += 1
            continue

        # Blockquote
        if line.startswith(">"):
            flush_list()
            in_blockquote = True
            quote_lines.append(line.lstrip("> ").strip())
            i += 1
            continue
        elif in_blockquote:
            flush_quote()

        # Horizontal rule
        if re.match(r'^(-{3,}|\*{3,}|_{3,})$', line.strip()):
            flush_list()
            html_out.append("<hr />")
            i += 1
            continue

        # Headings
        heading_match = re.match(r'^(#{1,6})\s+(.*)$', line)
        if heading_match:
            flush_list()
            level = len(heading_match.group(1))
            heading_text = heading_match.group(2).strip()
            slug_id = re.sub(r'[^\w\- ]', '', heading_text).strip().lower().replace(" ", "-")
            html_out.append(f'<h{level} id="{slug_id}">{parse_inline(heading_text)}</h{level}>')
            i += 1
            continue

        # Unordered list: - or *
        ul_match = re.match(r'^\s*[-*]\s+(.*)$', line)
        if ul_match:
            if not in_list or list_type != 'ul':
                flush_list()
                in_list = True
                list_type = 'ul'
                html_out.append("<ul>")
            html_out.append(f"<li>{parse_inline(ul_match.group(1))}</li>")
            i += 1
            continue

        # Ordered list: 1.
        ol_match = re.match(r'^\s*(\d+)\.\s+(.*)$', line)
        if ol_match:
            if not in_list or list_type != 'ol':
                flush_list()
                in_list = True
                list_type = 'ol'
                html_out.append("<ol>")
            html_out.append(f"<li>{parse_inline(ol_match.group(2))}</li>")
            i += 1
            continue

        # Empty line
        if not line.strip():
            flush_list()
            i += 1
            continue

        # Paragraph
        flush_list()
        html_out.append(f"<p>{parse_inline(line)}</p>")
        i += 1

    flush_list()
    flush_quote()
    return "\n".join(html_out)

def render_base(title, description, content_html, active_nav="home", canonical_path="/", extra_head=""):
    canonical_url = f"{SITE_URL}{canonical_path}"
    full_title = f"{title} — {SITE_TITLE}" if title != SITE_TITLE else f"{SITE_TITLE} — {SITE_TAGLINE}"

    nav_links = [
        ("/", "Ana Sayfa", "home"),
        ("/blog/", "Yazılar", "blog"),
        ("/hakkimda/", "Hakkımda", "about"),
        ("/iletisim/", "İletişim", "contact")
    ]

    nav_items_html = []
    for url, label, key in nav_links:
        active_class = ' class="active"' if active_nav == key else ''
        nav_items_html.append(f'<a href="{url}"{active_class}>{label}</a>')
    nav_html = "\n".join(nav_items_html)

    return f"""<!DOCTYPE html>
<html lang="tr">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{html.escape(full_title)}</title>
  <meta name="description" content="{html.escape(description)}">
  <link rel="canonical" href="{canonical_url}">
  
  <!-- Open Graph / Facebook -->
  <meta property="og:type" content="website">
  <meta property="og:url" content="{canonical_url}">
  <meta property="og:title" content="{html.escape(full_title)}">
  <meta property="og:description" content="{html.escape(description)}">
  <meta property="og:site_name" content="{SITE_TITLE}">

  <!-- Twitter Card -->
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{html.escape(full_title)}">
  <meta name="twitter:description" content="{html.escape(description)}">

  <!-- RSS & Sitemap -->
  <link rel="alternate" type="application/rss+xml" title="{SITE_TITLE} RSS Feed" href="/feed.xml">
  <link rel="sitemap" type="application/xml" title="Sitemap" href="/sitemap.xml">

  <!-- Styles -->
  <link rel="stylesheet" href="/css/style.css">
  {extra_head}
</head>
<body>
  <div id="reading-progress"></div>

  <header class="site-header">
    <div class="container nav-wrap">
      <a href="/" class="site-logo">
        <span class="dot"></span>
        <span>{SITE_TITLE}</span>
      </a>

      <div class="nav-actions">
        <nav class="main-nav">
          {nav_html}
        </nav>
        <button id="theme-toggle" class="theme-toggle-btn" aria-label="Temayı değiştir">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>
        </button>
      </div>
    </div>
  </header>

  <main>
    {content_html}
  </main>

  <footer class="site-footer">
    <div class="container footer-content">
      <p>&copy; {datetime.now().year} {SITE_TITLE}. Tüm hakları saklıdır.</p>
      <div class="footer-links">
        <a href="/feed.xml">RSS Akışı</a>
        <a href="/hakkimda/">Hakkımda</a>
        <a href="/iletisim/">İletişim</a>
        <a href="https://linkedin.com" target="_blank" rel="noopener">LinkedIn</a>
        <a href="https://x.com" target="_blank" rel="noopener">X / Twitter</a>
      </div>
    </div>
  </footer>

  <script src="/js/main.js"></script>
</body>
</html>"""

def build_site():
    print(f"🚀 Blog derleniyor: {SITE_URL}")
    if DIST_DIR.exists():
        shutil.rmtree(DIST_DIR)
    DIST_DIR.mkdir(parents=True)

    # 1. Copy static assets
    if STATIC_DIR.exists():
        shutil.copytree(STATIC_DIR, DIST_DIR, dirs_exist_ok=True)

    # 2. Parse all blog posts
    posts = []
    if BLOG_DIR.exists():
        for md_file in BLOG_DIR.glob("*.md"):
            content = md_file.read_text(encoding="utf-8")
            meta, body = parse_frontmatter(content)
            
            if meta.get("draft", False):
                continue

            slug = meta.get("slug", md_file.stem)
            title = meta.get("title", slug.replace("-", " ").title())
            date_str = str(meta.get("date", "2026-09-01"))
            excerpt = meta.get("excerpt", "")
            tags = meta.get("tags", [])
            featured = meta.get("featured", False)
            reading_time = calculate_reading_time(body)

            html_body = markdown_to_html(body)

            posts.append({
                "slug": slug,
                "title": title,
                "date": date_str,
                "date_formatted": format_date_tr(date_str),
                "excerpt": excerpt,
                "tags": tags,
                "featured": featured,
                "reading_time": reading_time,
                "body_html": html_body,
                "raw_body": body
            })

    # Sort posts descending by date
    posts.sort(key=lambda x: x["date"], reverse=True)

    # 3. Generate Individual Post Pages (/blog/[slug]/index.html)
    all_tags = set()
    for idx, p in enumerate(posts):
        for t in p["tags"]:
            all_tags.add(t)

        prev_post = posts[idx + 1] if idx + 1 < len(posts) else None
        next_post = posts[idx - 1] if idx > 0 else None

        tags_html = "".join([f'<a href="/blog/?tag={html.escape(t)}" class="tag-pill">#{t}</a>' for t in p["tags"]])

        nav_links_html = '<div style="display: flex; justify-content: space-between; margin-top: 3rem; padding-top: 2rem; border-top: 1px solid var(--border); font-size: 0.95rem;">'
        if prev_post:
            nav_links_html += f'<a href="/blog/{prev_post["slug"]}/" style="color: var(--text-muted); text-decoration: none;">← {html.escape(prev_post["title"])}</a>'
        else:
            nav_links_html += '<span></span>'
        if next_post:
            nav_links_html += f'<a href="/blog/{next_post["slug"]}/" style="color: var(--text-muted); text-decoration: none;">{html.escape(next_post["title"])} →</a>'
        nav_links_html += '</div>'

        article_html = f"""
        <article class="container">
          <header class="article-header">
            <a href="/blog/" class="article-back-link">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="19" y1="12" x2="5" y2="12"/><polyline points="12 19 5 12 12 5"/></svg>
              Tüm Yazılara Dön
            </a>
            <h1>{html.escape(p["title"])}</h1>
            <div class="article-meta-bar">
              <div class="author-chip">
                <span class="author-avatar-sm">GU</span>
                <span>{AUTHOR_NAME}</span>
              </div>
              <span>•</span>
              <time datetime="{p["date"]}">{p["date_formatted"]}</time>
              <span>•</span>
              <span>{p["reading_time"]}</span>
            </div>
          </header>

          <div class="prose">
            {p["body_html"]}
          </div>

          <div class="post-tags">
            {tags_html}
          </div>

          <div class="author-card">
            <div class="author-card-avatar">GU</div>
            <div class="author-card-info">
              <h4>{AUTHOR_NAME}</h4>
              <p>{AUTHOR_BIO}</p>
            </div>
          </div>

          {nav_links_html}
        </article>
        """

        post_dir = DIST_DIR / "blog" / p["slug"]
        post_dir.mkdir(parents=True, exist_ok=True)
        full_page = render_base(
            title=p["title"],
            description=p["excerpt"],
            content_html=article_html,
            active_nav="blog",
            canonical_path=f"/blog/{p['slug']}/"
        )
        (post_dir / "index.html").write_text(full_page, encoding="utf-8")

    # 4. Generate Blog Listing (/blog/index.html)
    tag_chips = ['<button class="filter-chip active" data-tag="all">Tümü</button>']
    for t in sorted(all_tags):
        tag_chips.append(f'<button class="filter-chip" data-tag="{html.escape(t)}">#{html.escape(t)}</button>')
    tag_chips_html = "\n".join(tag_chips)

    cards_html = []
    for p in posts:
        tags_data = ",".join(p["tags"])
        tags_badges = "".join([f'<span class="tag">#{t}</span>' for t in p["tags"]])
        card = f"""
        <a href="/blog/{p["slug"]}/" class="post-card" data-title="{html.escape(p["title"].lower())}" data-excerpt="{html.escape(p["excerpt"].lower())}" data-tags="{html.escape(tags_data)}">
          <div class="post-card-meta">
            <time datetime="{p["date"]}">{p["date_formatted"]}</time>
            <span>•</span>
            <span>{p["reading_time"]}</span>
            {tags_badges}
          </div>
          <h3>{html.escape(p["title"])}</h3>
          <p class="excerpt">{html.escape(p["excerpt"])}</p>
          <div class="post-card-footer">
            <span>Devamını Oku →</span>
          </div>
        </a>
        """
        cards_html.append(card)

    blog_index_html = f"""
    <div class="container" style="padding-top: 3.5rem; padding-bottom: 4rem;">
      <h1 style="font-size: 2.4rem; font-weight: 800; letter-spacing: -0.03em; margin-bottom: 0.5rem;">Yazılar & Düşünceler</h1>
      <p style="font-size: 1.15rem; color: var(--text-muted); margin-bottom: 2rem;">Teknoloji, yapay zeka, yaratıcı üretim ve hayata dair notlar.</p>

      <div class="search-box">
        <svg class="search-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
        <input type="text" id="blog-search" class="search-input" placeholder="Yazılarda ara (başlık veya konu)...">
      </div>

      <div class="filter-tags">
        {tag_chips_html}
      </div>

      <div class="post-list" id="post-list">
        {"".join(cards_html)}
      </div>
    </div>
    """
    blog_dir = DIST_DIR / "blog"
    blog_dir.mkdir(parents=True, exist_ok=True)
    (blog_dir / "index.html").write_text(
        render_base("Yazılar", "Gizem Uzer'in tüm yazıları ve düşünceleri.", blog_index_html, active_nav="blog", canonical_path="/blog/"),
        encoding="utf-8"
    )

    # 5. Generate Home Page (/index.html)
    featured_cards = []
    for p in [x for x in posts if x["featured"]][:2]:
        tags_badges = "".join([f'<span class="tag">#{t}</span>' for t in p["tags"]])
        card = f"""
        <a href="/blog/{p["slug"]}/" class="post-card">
          <div class="post-card-meta">
            <time datetime="{p["date"]}">{p["date_formatted"]}</time>
            <span>•</span>
            <span>{p["reading_time"]}</span>
            {tags_badges}
          </div>
          <h3>{html.escape(p["title"])}</h3>
          <p class="excerpt">{html.escape(p["excerpt"])}</p>
          <div class="post-card-footer">
            <span>Devamını Oku →</span>
          </div>
        </a>
        """
        featured_cards.append(card)

    recent_cards = []
    for p in posts[:3]:
        tags_badges = "".join([f'<span class="tag">#{t}</span>' for t in p["tags"]])
        card = f"""
        <a href="/blog/{p["slug"]}/" class="post-card">
          <div class="post-card-meta">
            <time datetime="{p["date"]}">{p["date_formatted"]}</time>
            <span>•</span>
            <span>{p["reading_time"]}</span>
            {tags_badges}
          </div>
          <h3>{html.escape(p["title"])}</h3>
          <p class="excerpt">{html.escape(p["excerpt"])}</p>
          <div class="post-card-footer">
            <span>Yazıyı İncele →</span>
          </div>
        </a>
        """
        recent_cards.append(card)

    home_html = f"""
    <section class="hero container">
      <div class="hero-tag">✨ Kişisel Blog & Dijital Bahçe</div>
      <h1>Düşünceler, yazılar ve keşifler.</h1>
      <p class="lead">
        Merhaba, ben <strong>Gizem Uzer</strong>. Teknoloji, yapay zeka, insan yaratıcılığı ve sade yaşam üzerine fikirlerimi demlediğim kişisel alanıma hoş geldiniz.
      </p>
      <div class="hero-meta">
        <a href="/blog/" class="btn btn-primary">Yazıları Keşfet →</a>
        <a href="/hakkimda/" class="btn btn-secondary">Hakkımda</a>
      </div>
    </section>

    <div class="container">
      <div class="section-header">
        <h2>Öne Çıkan Düşünceler</h2>
        <a href="/blog/" class="view-all">Tümünü Gör →</a>
      </div>
      <div class="post-list">
        {"".join(featured_cards)}
      </div>

      <div class="section-header">
        <h2>Son Eklenenler</h2>
        <a href="/blog/" class="view-all">Arşive Git →</a>
      </div>
      <div class="post-list">
        {"".join(recent_cards)}
      </div>

      <div class="newsletter-card">
        <h3>Yeni Yazılardan Haberdar Olun</h3>
        <p>Yalnızca gerçekten paylaşmaya değer yeni bir düşünce ya da makale yayınladığımda gelen sakin bir e-posta bülteni.</p>
        <form class="newsletter-form" onsubmit="event.preventDefault(); alert('Teşekkürler! Bülten listesine eklendiniz.');">
          <input type="email" placeholder="E-posta adresiniz..." required>
          <button type="submit" class="btn btn-primary">Abone Ol</button>
        </form>
      </div>
    </div>
    """
    (DIST_DIR / "index.html").write_text(
        render_base(SITE_TITLE, SITE_DESCRIPTION, home_html, active_nav="home", canonical_path="/"),
        encoding="utf-8"
    )

    # 6. Generate About Page (/hakkimda/index.html)
    about_file = PAGES_DIR / "about.md"
    about_body = ""
    about_title = "Hakkımda"
    about_subtitle = "Gizem Uzer kimdir?"
    if about_file.exists():
        meta, body = parse_frontmatter(about_file.read_text(encoding="utf-8"))
        about_title = meta.get("title", about_title)
        about_subtitle = meta.get("subtitle", about_subtitle)
        about_body = markdown_to_html(body)

    about_page_html = f"""
    <div class="container" style="padding: 3.5rem 1.5rem 5rem;">
      <header class="article-header" style="margin-bottom: 2rem;">
        <h1 style="font-size: 2.6rem;">{html.escape(about_title)}</h1>
        <p style="font-size: 1.2rem; color: var(--text-muted);">{html.escape(about_subtitle)}</p>
      </header>
      <div class="prose">
        {about_body}
      </div>
    </div>
    """
    about_dir = DIST_DIR / "hakkimda"
    about_dir.mkdir(parents=True, exist_ok=True)
    (about_dir / "index.html").write_text(
        render_base(about_title, about_subtitle, about_page_html, active_nav="about", canonical_path="/hakkimda/"),
        encoding="utf-8"
    )

    # 7. Generate Contact Page (/iletisim/index.html)
    contact_file = PAGES_DIR / "contact.md"
    contact_body = ""
    contact_title = "İletişim"
    contact_subtitle = "Bağlantıda kalalım"
    if contact_file.exists():
        meta, body = parse_frontmatter(contact_file.read_text(encoding="utf-8"))
        contact_title = meta.get("title", contact_title)
        contact_subtitle = meta.get("subtitle", contact_subtitle)
        contact_body = markdown_to_html(body)

    contact_page_html = f"""
    <div class="container" style="padding: 3.5rem 1.5rem 5rem;">
      <header class="article-header" style="margin-bottom: 2rem;">
        <h1 style="font-size: 2.6rem;">{html.escape(contact_title)}</h1>
        <p style="font-size: 1.2rem; color: var(--text-muted);">{html.escape(contact_subtitle)}</p>
      </header>
      <div class="prose">
        {contact_body}
      </div>
    </div>
    """
    contact_dir = DIST_DIR / "iletisim"
    contact_dir.mkdir(parents=True, exist_ok=True)
    (contact_dir / "index.html").write_text(
        render_base(contact_title, contact_subtitle, contact_page_html, active_nav="contact", canonical_path="/iletisim/"),
        encoding="utf-8"
    )

    # 8. Generate RSS 2.0 Feed (/feed.xml)
    rss_items = []
    for p in posts:
        dt = datetime.strptime(p["date"], "%Y-%m-%d")
        pub_date = dt.strftime("%a, %d %b %Y 00:00:00 +0300")
        item_xml = f"""    <item>
      <title>{html.escape(p["title"])}</title>
      <link>{SITE_URL}/blog/{p["slug"]}/</link>
      <guid isPermaLink="true">{SITE_URL}/blog/{p["slug"]}/</guid>
      <pubDate>{pub_date}</pubDate>
      <description>{html.escape(p["excerpt"])}</description>
    </item>"""
        rss_items.append(item_xml)

    rss_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title>{SITE_TITLE}</title>
    <link>{SITE_URL}</link>
    <description>{SITE_DESCRIPTION}</description>
    <language>tr</language>
    <atom:link href="{SITE_URL}/feed.xml" rel="self" type="application/rss+xml"/>
    {"\n".join(rss_items)}
  </channel>
</rss>"""
    (DIST_DIR / "feed.xml").write_text(rss_xml, encoding="utf-8")

    # 9. Generate Sitemap (/sitemap.xml)
    sitemap_urls = [
        f"  <url><loc>{SITE_URL}/</loc><changefreq>weekly</changefreq><priority>1.0</priority></url>",
        f"  <url><loc>{SITE_URL}/blog/</loc><changefreq>daily</changefreq><priority>0.9</priority></url>",
        f"  <url><loc>{SITE_URL}/hakkimda/</loc><changefreq>monthly</changefreq><priority>0.7</priority></url>",
        f"  <url><loc>{SITE_URL}/iletisim/</loc><changefreq>monthly</changefreq><priority>0.6</priority></url>",
    ]
    for p in posts:
        sitemap_urls.append(
            f"  <url><loc>{SITE_URL}/blog/{p['slug']}/</loc><lastmod>{p['date']}</lastmod><changefreq>monthly</changefreq><priority>0.8</priority></url>"
        )

    sitemap_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{"\n".join(sitemap_urls)}
</urlset>"""
    (DIST_DIR / "sitemap.xml").write_text(sitemap_xml, encoding="utf-8")

    # 10. robots.txt
    robots_txt = f"""User-agent: *
Allow: /

Sitemap: {SITE_URL}/sitemap.xml
"""
    (DIST_DIR / "robots.txt").write_text(robots_txt, encoding="utf-8")

    print(f"✨ Başarıyla tamamlandı: {len(posts)} yazı derlendi -> dist/")

if __name__ == "__main__":
    build_site()
